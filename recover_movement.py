#!/usr/bin/env python3
"""Minimal movement recovery script for TurtleBot4 startup."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Dict, Set, Tuple


CREATE3_BASE = "http://10.42.0.1:8080"
REBOOT_WAIT_S = 120
DOCK_DATA_WAIT_S = 120

EXPECTED_TOPICS = {
    "/battery_state",
    "/cmd_vel",
    "/diagnostics",
    "/diagnostics_agg",
    "/diagnostics_toplevel_state",
    "/dock_status",
    "/function_calls",
    "/hazard_detection",
    "/hmi/buttons",
    "/hmi/display",
    "/hmi/display/message",
    "/hmi/led",
    "/imu",
    "/interface_buttons",
    "/ip",
    "/joint_states",
    "/joy",
    "/joy/set_feedback",
    "/mouse",
    "/oakd/rgb/preview/image_raw",
    "/parameter_events",
    "/robot_description",
    "/rosout",
    "/scan",
    "/tf",
    "/tf_static",
    "/wheel_status",
}


class RecoverMovement:
    def __init__(self) -> None:
        self.phase = "init"
        self.stop_heartbeat = threading.Event()
        self.env = os.environ.copy()
        self.env["RMW_IMPLEMENTATION"] = "rmw_fastrtps_cpp"
        self.env["ROS_DOMAIN_ID"] = self.env.get("ROS_DOMAIN_ID", "0")
        if "FASTRTPS_DEFAULT_PROFILES_FILE" not in self.env:
            self.env["FASTRTPS_DEFAULT_PROFILES_FILE"] = "/etc/turtlebot4/fastdds_rpi.xml"

    def now(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def log(self, msg: str) -> None:
        print(f"[{self.now()}] {msg}", flush=True)

    def heartbeat(self) -> None:
        while not self.stop_heartbeat.is_set():
            self.log(f"alive: phase={self.phase}")
            self.stop_heartbeat.wait(1.0)

    def run_ros2(self, args: str, timeout_s: int = 10) -> Tuple[int, str, str]:
        cmd = (
            "source /opt/ros/humble/setup.bash >/dev/null 2>&1; "
            "source /etc/turtlebot4/setup.bash >/dev/null 2>&1 || true; "
            f"ros2 {args}"
        )
        try:
            proc = subprocess.run(
                ["bash", "-lc", cmd],
                env=self.env,
                text=True,
                capture_output=True,
                timeout=timeout_s,
                check=False,
            )
            return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "").strip() if isinstance(e.stdout, str) else ""
            err = (e.stderr or "").strip() if isinstance(e.stderr, str) else ""
            if err:
                err = f"{err}; timed out after {timeout_s}s"
            else:
                err = f"timed out after {timeout_s}s"
            return 124, out, err

    def http_post(self, path: str, timeout_s: int = 8) -> Tuple[int, str]:
        req = urllib.request.Request(f"{CREATE3_BASE}{path}", data=b"", method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            return 0, str(e)

    def http_get(self, path: str, timeout_s: int = 6) -> Tuple[int, str]:
        req = urllib.request.Request(f"{CREATE3_BASE}{path}", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            return 0, str(e)

    def topic_set(self) -> Set[str]:
        rc, out, _err = self.run_ros2("topic list", timeout_s=10)
        if rc != 0:
            return set()
        return {line.strip() for line in out.splitlines() if line.strip()}

    def missing_topics(self) -> Set[str]:
        return EXPECTED_TOPICS - self.topic_set()

    def reboot_create3(self) -> bool:
        self.phase = "reboot_create3"
        status, body = self.http_post("/api/reboot", timeout_s=8)
        ok = status in (200, 202, 204)
        self.log(f"create3 reboot http={status} ok={ok}")
        if body:
            self.log(f"create3 reboot body={body[:180]}")
        return ok

    def wait_for_topics(self, wait_s: int) -> bool:
        self.phase = "wait_topics"
        deadline = time.time() + wait_s
        while time.time() < deadline:
            missing = self.missing_topics()
            if not missing:
                self.log("all expected topics are present")
                return True
            self.log(f"topics missing: {len(missing)}")
            time.sleep(1)
        self.log("timed out waiting for expected topics")
        return False

    def dock_status(self) -> Tuple[bool, bool]:
        self.phase = "check_dock_status"
        rc, out, err = self.run_ros2(
            "topic echo /dock_status --qos-reliability best_effort --once",
            timeout_s=8,
        )
        has_data = rc == 0 and len(out) > 0
        is_docked = "is_docked: true" in out.lower()
        self.log(f"dock_status_has_data={has_data} is_docked={is_docked}")
        if err:
            self.log(f"dock_status stderr={err[:180]}")
        return has_data, is_docked

    def wait_for_dock_data(self, wait_s: int) -> Tuple[bool, bool]:
        self.phase = "wait_dock_data"
        deadline = time.time() + wait_s
        last_is_docked = False
        while time.time() < deadline:
            has_data, is_docked = self.dock_status()
            last_is_docked = is_docked
            if has_data:
                self.log("dock_status data recovered")
                return True, is_docked
            self.log("dock_status still missing; retrying")
            time.sleep(1)
        self.log("timed out waiting for dock_status data")
        return False, last_is_docked

    def wait_for_create3_server(self) -> bool:
        """Wait for Create 3 HTTP server to come back online after reboot."""
        self.phase = "wait_create3_server"
        deadline = time.time() + 60
        while time.time() < deadline:
            status, body = self.http_get("/api/reboot", timeout_s=3)
            if status > 0:
                self.log(f"create3 server responded http={status}")
                return True
            self.log("create3 server not responding yet; retrying")
            time.sleep(1)
        self.log("timed out waiting for create3 server after 60s")
        return False

    def wait_after_create3_reboot(self) -> Tuple[bool, bool]:
        self.phase = "wait_after_create3_reboot"
        self.wait_for_create3_server()
        self.wait_for_topics(REBOOT_WAIT_S)
        return self.wait_for_dock_data(DOCK_DATA_WAIT_S)

    def undock_or_back_up(self, is_docked: bool) -> None:
        self.phase = "final_motion_action"
        if is_docked:
            self.log("robot is docked; sending undock action")
            rc, out, err = self.run_ros2(
                "action send_goal /undock irobot_create_msgs/action/Undock '{}'",
                timeout_s=20,
            )
            self.log(f"undock rc={rc}")
            if out:
                self.log(f"undock out={out[:220]}")
            if err:
                self.log(f"undock err={err[:180]}")
            return

        self.log("robot is undocked; sending slight backward cmd_vel pulse")
        rc, out, err = self.run_ros2(
            "topic pub --once --qos-reliability best_effort /cmd_vel geometry_msgs/msg/Twist '{linear: {x: -0.03}, angular: {z: 0.0}}'",
            timeout_s=8,
        )
        self.log(f"backward pulse rc={rc}")
        if out:
            self.log(f"backward pulse out={out[:220]}")
        if err:
            self.log(f"backward pulse err={err[:180]}")

    def check_protocols(self) -> None:
        self.phase = "check_protocols"
        status_cfg, body_cfg = self.http_get("/ros-config", timeout_s=6)
        status_ovr, body_ovr = self.http_get("/rmw-profile-override", timeout_s=6)
        self.log(f"ros-config http={status_cfg} has_fastrtps={'rmw_fastrtps_cpp' in body_cfg}")
        self.log(f"rmw-profile-override http={status_ovr} bytes={len(body_ovr)}")

    def reboot_pi_no_sudo(self) -> None:
        self.phase = "reboot_pi"
        cmds = [
            "systemctl reboot --no-wall",
            "loginctl reboot",
            "dbus-send --system --type=method_call --dest=org.freedesktop.login1 /org/freedesktop/login1 org.freedesktop.login1.Manager.Reboot boolean:true",
        ]
        for cmd in cmds:
            self.log(f"attempting pi reboot command: {cmd}")
            try:
                proc = subprocess.run(
                    ["bash", "-lc", cmd],
                    env=self.env,
                    text=True,
                    capture_output=True,
                    timeout=6,
                    check=False,
                )
                if proc.returncode == 0:
                    self.log("pi reboot command accepted")
                    return
                self.log(f"pi reboot command failed rc={proc.returncode}")
            except subprocess.TimeoutExpired:
                self.log("pi reboot command timed out")

    def run(self) -> int:
        hb = threading.Thread(target=self.heartbeat, daemon=True)
        hb.start()
        try:
            self.log("recover_movement.py starting")
            self.phase = "initial_topic_check"
            missing = self.missing_topics()
            has_dock_data = False
            is_docked = False
            if missing:
                self.log(f"initial missing topics: {len(missing)}")
                self.reboot_create3()
                has_dock_data, is_docked = self.wait_after_create3_reboot()
            else:
                self.log("all expected topics present on first check")
                has_dock_data, is_docked = self.dock_status()

            if not has_dock_data:
                self.log("dock_status has no data; rebooting Create 3 before protocol checks")
                self.reboot_create3()
                has_dock_data, is_docked = self.wait_after_create3_reboot()
                if has_dock_data:
                    self.undock_or_back_up(is_docked)
                    self.log("dock_status recovered after reboot; final motion action sent; exiting success")
                    return 0

                self.check_protocols()
                self.reboot_pi_no_sudo()
                self.log("completed failure path; exiting")
                return 1

            self.undock_or_back_up(is_docked)
            self.log("dock_status has data; final motion action sent; exiting success")
            return 0
        finally:
            self.phase = "cleanup"
            self.stop_heartbeat.set()
            hb.join(timeout=1)
            self.log("recover_movement.py exiting cleanly")


def main() -> int:
    return RecoverMovement().run()


if __name__ == "__main__":
    sys.exit(main())
