#!/usr/bin/env python3

import array
import os
import re
import sys
import pty
import select
import signal
import queue
import threading
import subprocess
from datetime import datetime, timezone

import rclpy
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import BatteryState, LaserScan, Image, Imu
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped, TransformStamped
from tf2_msgs.msg import TFMessage
from diagnostic_msgs.msg import DiagnosticArray
from nav_msgs.msg import Odometry, OccupancyGrid
from irobot_create_msgs.msg import HazardDetectionVector, DockStatus

try:
    import dearpygui.dearpygui as dpg
except:
    raise ImportError("pip install dearpygui")

node_name = 'ui_node'

relative_input_topic = 'input'
relative_output_topic = 'output'

qos = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE
)

GREEN = (0, 255, 0, 255)
YELLOW = (255, 255, 0, 255)
RED = (255, 0, 0, 255)

# Strip ANSI/VT escape sequences and terminal control codes
_ANSI_RE = re.compile(
    r'\x1B\][^\x07]*\x07'                              # OSC ending with BEL (title sets etc.)
    r'|\x1B\][^\x1B]*\x1B\\'                           # OSC ending with ST
    r'|(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]'                # CSI sequences (colors, cursor, etc.)
    r'|\x1B[^\[\]].'                                    # other 2-char ESC sequences
    r'|[\x00-\x08\x0B-\x0C\x0E-\x1A\x1C-\x1F]'       # control chars (ESC \x1B excluded)
)

def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub('', text)


class TerminalProcess:
    def __init__(self, terminal_tag: str, output_queue: queue.Queue):
        self.terminal_tag = terminal_tag
        self.output_queue = output_queue
        self.process = None
        self._master_fd = None

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def run(self, command: str):
        if self.is_running():
            self.interrupt()

        master_fd, slave_fd = pty.openpty()
        self._master_fd = master_fd
        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                executable='/bin/bash',
                stdout=slave_fd,
                stderr=slave_fd,
                stdin=slave_fd,
                close_fds=True,
                start_new_session=True,
            )
        except OSError as e:
            self.output_queue.put((self.terminal_tag, f"[error: {e}]"))
            os.close(master_fd)
            os.close(slave_fd)
            return
        os.close(slave_fd)
        threading.Thread(target=self._read_loop, daemon=True).start()

    def send_input(self, text: str):
        if self._master_fd is not None and self.is_running():
            try:
                os.write(self._master_fd, (text + '\n').encode())
            except OSError:
                pass

    def _read_loop(self):
        buf = b""
        try:
            while True:
                if not isinstance(self._master_fd, int):
                    continue
                try:
                    r, _, _ = select.select([self._master_fd], [], [], 0.1)
                except (ValueError, OSError):
                    break
                if r:
                    try:
                        data = os.read(self._master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    buf += data
                    while b'\n' in buf:
                        line, buf = buf.split(b'\n', 1)
                        text = _strip_ansi(line.decode('utf-8', errors='replace').rstrip('\r'))
                        self.output_queue.put((self.terminal_tag, text))
                    # Flush partial line (e.g. input() prompts that have no trailing newline)
                    if buf:
                        text = _strip_ansi(buf.decode('utf-8', errors='replace').rstrip('\r'))
                        if text:
                            self.output_queue.put((self.terminal_tag, text))
                            buf = b""
                elif self.process is not None and self.process.poll() is not None:
                    break
        finally:
            if buf:
                text = _strip_ansi(buf.decode('utf-8', errors='replace').rstrip('\r'))
                if text:
                    self.output_queue.put((self.terminal_tag, text))
            if self._master_fd is not None:
                try:
                    os.close(self._master_fd)
                except OSError:
                    pass
            if self.process is not None:
                rc = self.process.wait()
                self.output_queue.put((self.terminal_tag, f"[exited: {rc}]"))

    def interrupt(self):
        if self.is_running():
            try:
                if self.process is not None:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
            except ProcessLookupError:
                pass


class ui_node_class(Node):
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.declare_parameter('basic_param', 'basic_default')
        self.basic_param = str(self.get_parameter('basic_param').value)

        self.status_prefixes = ["/battery_state", "/diagnostics_agg", "/scan", "/odom", "/imu", "/tf", "/dock_status", "/cmd_vel", "/map", "/costmap", "/rfid", "/rfid_goal"]
        status_prefixes = self.status_prefixes
        compute_prefixes = ['pc_blocking', 'rqt', 'rviz', 'slam', 'localize', 'nav', 'explore', 'rfid_mgr','bag', 'ssh_blocking', 'ssh_rfid']
        terminal_prefixes = compute_prefixes + status_prefixes
        
        self.rfid_names: list[str] = []
        
        self.output_queue = queue.Queue()
        self.terminal_procs = {
            prefix: TerminalProcess(f"{prefix}_output_terminal", self.output_queue)
            for prefix in terminal_prefixes
        }
        self._pending_network_restart = False

        dpg.create_context()
        self.viewport_width = int(1920/2)
        self.viewport_height = 1100
        self.padding = 10
        dpg.create_viewport(title='TurtleDel',
                            width=self.viewport_width,
                            height=self.viewport_height,
                            x_pos=0,
                            y_pos=30,
                            decorated=False,
                            )

        window_width = self.viewport_width - 2 * self.padding
        top_width = int(window_width - 2 * self.padding)
        col_gap = self.padding

        window_height = self.viewport_height - 2 * self.padding
        top_height = int((window_height - 2 * self.padding) / 2)

        col_width = int((top_width - col_gap) / 2)


        with dpg.window(tag="window",
                        label="",
                        width=self.viewport_width-2*self.padding,
                        height=self.viewport_height-2*self.padding,
                        pos=(self.padding, self.padding),
                        no_title_bar=True,
                        no_collapse=True,
                        no_close=True,
                        no_move=True,
                        ):

            with dpg.group(tag="global_container"):
                with dpg.child_window(tag="top_window",
                                      width=-1,
                                      height=top_height,
                                      border=True):
                    with dpg.group(tag="top_container",
                                   horizontal=True,
                                   horizontal_spacing=col_gap,
                                   ):
                        with dpg.child_window(width=col_width, height=-1, border=True, tag="left_col"):
                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                dpg.add_button(tag="EXIT",
                                               label="EXIT",
                                               callback=self.exit_callback,
                                               )
                                dpg.add_button(tag="RESTART",
                                               label="RESTART UI",
                                               callback=self.restart_callback,
                                               )
                                dpg.add_text("TurtleDel: Group 2 User Interface")

                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                dpg.add_button(tag="bag_record",
                                        label="Record Bag",
                                        callback=self.command("bag", 'rm -rf $HOME/TurtleDel/turtledel_bag && ros2 bag record -o $HOME/TurtleDel/turtledel_bag -a --qos-profile-overrides-path $HOME/TurtleDel/config/bag_qos.yaml'))
                                
                                dpg.add_button(tag="bag_play",
                                        label="Play Bag",
                                        callback=self.command("bag", "ros2 bag play $HOME/TurtleDel/turtledel_bag --clock --qos-profile-overrides-path $HOME/TurtleDel/config/bag_play_qos.yaml"))
                                
                                dpg.add_button(tag="rqt_graph",
                                        label="RQT Graph",
                                        callback=self.command("rqt", "rqt_graph"))

                            dpg.add_text("System State:")
                            
                            connection_rows = [["RaspberryPi", "Create3", "WIFI"]]
                            for row in connection_rows:
                                with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                    for status_prefix in row:
                                        self.status_indicator(status_prefix, self)

                            dpg.add_button(tag="wifi_connect",
                                           label="Connect",
                                           before="WIFI_right",
                                           callback=self._network_change_command("pc_blocking", 'nmcli device wifi rescan && sleep 3 && nmcli device wifi connect "turtlebot-hub-5G"'))
                            
                            dpg.add_button(tag="wifi_disconnect",
                                           label="Disconnect",
                                           before="WIFI_right",
                                           callback=self._network_change_command("pc_blocking", 'nmcli device wifi rescan && sleep 3 && nmcli device wifi connect "eduroam"'))

                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                dpg.add_button(tag="ros2_restart",
                                        label="ROS2 Restart",
                                        callback=self.command("pc_blocking", 'ros2 daemon stop && ros2 daemon start'))
                                dpg.add_button(tag="turtlebot_restart",
                                        label="Turtlebot Restart",
                                        callback=self.command("ssh_blocking", 'sudo systemctl restart turtlebot4.service'))
                                dpg.add_button(tag="create3_restart",
                                        label="Create3 Restart",
                                        callback=self.command("pc_blocking", 'curl -s -X POST http://192.168.1.3:8080/api/restart-app'))
                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                dpg.add_text("Timestamp Issues: ")
                                dpg.add_button(tag="rpi_time_restart",
                                        label="Rasberry Pi Time Restart",
                                        callback=lambda s=None, a=None: self.command("ssh_blocking", 'sudo date -s "' + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S') + '" && sudo systemctl restart chrony && sudo systemctl restart turtlebot4.service && date')(s, a))

                            for status_prefix in status_prefixes:
                                with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                    self.status_indicator(status_prefix, self)
                            
                            dpg.add_text("()",
                                         tag="battery_percent_text",
                                         before="/battery_state_text")
                            
                            # dpg.add_button(tag="scan_mask_node_start",
                            #             label="Start Masking",
                            #             before="/scan_masked_right",
                            #             callback=self.command("scan_mask_node", "ros2 launch scan_mask scan_mask.launch.py"))

                            dpg.add_button(tag="restart_rfid",
                                        label="RFID Scan",
                                        before="/rfid_right",
                                        callback=self.command("ssh_rfid", "source /opt/ros/humble/setup.bash && cd ~/TurtleDel && source install/setup.bash && ros2 launch rfid rfid.launch.py"))
                            
                            dpg.add_button(tag="rfid_mgr_start",
                                        label="RFID Manager",
                                        before="/rfid_right",
                                        callback=self.command("rfid_mgr", "ros2 run rfid_waypoint_mgr rfid_waypoint_mgr_exec"))

                            dpg.add_button(tag="undock",
                                        label="Undock",
                                        before="/dock_status_right",
                                        callback=self.command("pc_blocking", "ros2 action send_goal /undock irobot_create_msgs/action/Undock {}"))

                            dpg.add_button(tag="dock",
                                        label="Dock",
                                        before="/dock_status_right",
                                        callback=self.command("pc_blocking", "ros2 action send_goal /dock irobot_create_msgs/action/Dock {}"))
                            
                            dpg.add_button(tag="teleop_start",
                                        label="TeleOp",
                                        before="/cmd_vel_right",
                                        callback=self.command("external", "ros2 run teleop_twist_keyboard teleop_twist_keyboard"))

                            dpg.add_button(tag="explore_start",
                                        label="Explore",
                                        before="/cmd_vel_right",
                                        callback=self.command("explore", "ros2 run frontier_explorer frontier_explorer_node"))

                            dpg.add_button(tag="rviz_start",
                                        label="RViz",
                                        before="/map_right",
                                        callback=self.command("rviz", "rviz2 -d ~/TurtleDel/config/robot.rviz"))
                            
                            dpg.add_button(tag="slam_start",
                                        label="SLAM",
                                        before="/map_right",
                                        # callback=self.command("slam", "python3 $HOME/TurtleDel/odom_tf_broadcaster.py & ros2 launch turtlebot4_navigation slam.launch.py params:=$HOME/TurtleDel/config/slam.yaml use_sim_time:=false"))
                                        callback=self.command("slam", "ros2 launch turtlebot4_navigation slam.launch.py params:=$HOME/TurtleDel/config/slam.yaml use_sim_time:=false"))
                            
                            dpg.add_button(tag="save_map",
                                        label="Save Map",
                                        before="/map_right",
                                        callback=self.command("pc_blocking", "ros2 run nav2_map_server map_saver_cli -f ~/TurtleDel/map"))
                            
                            dpg.add_button(tag="view_map",
                                        label="View Map",
                                        before="/map_right",
                                        callback=self.command("external", "xdg-open $HOME/TurtleDel/map.pgm"))
                            

                            dpg.add_button(tag="localize_start",
                                        label="Localize",
                                        before="/costmap_right",
                                        callback=self.command("localize", "ros2 launch turtlebot4_navigation localization.launch.py map:=$HOME/TurtleDel/map.yaml params:=$HOME/TurtleDel/config/localization.yaml"))

                            dpg.add_button(tag="nav_start",
                                        label="Nav",
                                        before="/costmap_right",
                                        callback=self.command("nav", "ros2 launch turtlebot4_navigation nav2.launch.py params_file:=/home/joseph/TurtleDel/config/nav2.yaml"))
                                
                            
                            if len(self.rfid_names) == 0:
                                default_value = ""
                            else:
                                default_value = self.rfid_names[0]
                            dpg.add_button(tag="rfid_nav",
                                            label="Nav To",
                                            before="/rfid_goal_right",
                                            callback=self.rfid_nav_request,
                                            width=60)
                            dpg.add_listbox(tag="rfid_name_selector",
                                                items=self.rfid_names,
                                                default_value=default_value,
                                                width=-1,
                                                num_items=4,
                                                )

                        with dpg.child_window(width=-1, height=-1, border=True, tag="right_col"):
                            dpg.add_text("System Topics:")
                            dpg.add_combo(tag="topic_selector",
                                items=status_prefixes,
                                default_value=status_prefixes[0],
                                callback=self.topic_select_callback,
                                width=-1)
                            for terminal_prefix in status_prefixes:
                                visible = (terminal_prefix == status_prefixes[0])
                                with dpg.group(tag=f"{terminal_prefix}_topic_group", show=visible):
                                    with dpg.child_window(tag=f"{terminal_prefix}_output_terminal",
                                                          width=-1, height=-1, border=True):
                                        dpg.add_selectable(label=">", span_columns=True)

                dpg.add_spacer(height=col_gap//4)
                with dpg.child_window(tag="bottom_window",
                                      width=-1,
                                      height=-1,
                                      border=True):
                    with dpg.tab_bar(tag="tab_bar", label="Tab Bar"):
                        for terminal_prefix in compute_prefixes:
                            self.terminal_tab_class(terminal_prefix, self)
                        self.command("ssh_blocking", "ssh ubuntu@192.168.1.3")() #initialize ssh
                        self.command("ssh_rfid", "ssh ubuntu@192.168.1.3")() #initialize ssh
                        self.command("ssh_blocking", "date")() #check date is not 2024

        with dpg.theme() as terminal_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 1)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 1)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 1)
        for terminal_prefix in terminal_prefixes:
            dpg.bind_item_theme(f"{terminal_prefix}_output_terminal", terminal_theme)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        self.battery_state = self.topic_monitor(self, 
            msg_type=BatteryState,
            topic="/battery_state",
            )

        self.diagnostics_agg = self.topic_monitor(self,
            msg_type=DiagnosticArray,
            topic="/diagnostics_agg",
            )
        
        self.scan = self.topic_monitor(self,
            msg_type=LaserScan,
            topic="/scan",
            )
        
        self.odom = self.topic_monitor(self,
            msg_type=Odometry,
            topic="/odom",
            )
        
        self.imu = self.topic_monitor(self,
            msg_type=Imu,
            topic="/imu",
            )

        self.tf = self.topic_monitor(self,
            msg_type=TFMessage,
            topic="/tf",
            )
        
        # self.scan_masked = self.topic_monitor(self,
        #     msg_type=LaserScan,
        #     topic="/scan_masked",
        #     )
        
        self.rfid = self.topic_monitor(self,
            msg_type=String,
            topic="/rfid",
            max_interval_s = 60,
            print_interval = 0.0,
            )
        
        self.dock_status = self.topic_monitor(self,
            msg_type=DockStatus,
            topic="/dock_status",
            )
        
        self.cmd_vel = self.topic_monitor(self,
            msg_type=Twist,
            topic="/cmd_vel",
            )
        
        self.map = self.topic_monitor(self,
            msg_type=OccupancyGrid,
            topic="/map",
            )
        
        self.costmap = self.topic_monitor(self,
            msg_type=OccupancyGrid,
            topic="/local_costmap/costmap",
            tag="/costmap",
            )
        
        self.tf_subscriber = self.create_subscription(
            msg_type=TFMessage,
            topic='/tf',
            callback=self.tf_callback,
            qos_profile=qos
            )
        
        self.rfid_goal = self.topic_monitor(self,
            msg_type=String,
            topic="/rfid_goal",
            )
        
        self.rfid_request_publisher = self.create_publisher(
            msg_type = String, 
            topic = "/rfid_goal",
            qos_profile = qos
            )
        

        self.create_timer(0.05, self.timer_callback)

        self.create_timer(1, self.ip_callback)
        
        self.create_timer(1, self.monitor_health_callback)
    
    def rfid_nav_request(self, sender, app_data):
        rfid_name = dpg.get_value("rfid_name_selector")
        output_msg = String()
        output_msg.data = str(rfid_name)
        self.rfid_request_publisher.publish(output_msg)
        # self.command("pc_blocking", f"ros2 topic pub --once /rfid_goal std_msgs/msg/String '{data}'"))
        
    
    def tf_callback(self, input_msg: TFMessage):
        for transform in input_msg.transforms:
            if not isinstance(transform, TransformStamped):
                continue
            child_frame_id = transform.child_frame_id
            if not isinstance(child_frame_id, str):
                continue
            if child_frame_id[:5] == 'rfid_':
                child_frame_name = child_frame_id[5:]
                if child_frame_name not in self.rfid_names:
                    self.rfid_names.append(child_frame_name)
                    self.rfid_names.sort()
                    dpg.configure_item("rfid_name_selector", items=self.rfid_names)
                    if len(self.rfid_names) == 1:
                        dpg.configure_item("rfid_name_selector", default_value=self.rfid_names[0])

    class status_indicator():
        def __init__(self, staus_prefix, node):
            radius=6
            with dpg.group(horizontal=True, horizontal_spacing=node.padding):
                with dpg.drawlist(tag=f"{staus_prefix}_canvas",width=int(2*radius), height=int(2.6*radius)):
                    dpg.draw_circle(tag=f"{staus_prefix}_status",
                                    center=(radius, 1.6*radius), 
                                    radius=radius, 
                                    color=RED, 
                                    fill=RED, 
                                    label=f"{staus_prefix}"
                                    )
                dpg.add_text(f"{staus_prefix}", tag=f"{staus_prefix}_text")
                dpg.add_text("", tag=f"{staus_prefix}_right")

    def command(self, terminal_prefix: str, command: str):
        def _callback(sender=None, app_data=None):
            if terminal_prefix == "external":
                subprocess.Popen(
                    ['gnome-terminal', '--', 'bash', '-c', command + '; exec bash'],
                    start_new_session=True,
                )
            else:
                dpg.set_value("tab_bar", f"{terminal_prefix}_tab") #focuses this terminal
                input_tag = f"{terminal_prefix}_input_field"
                dpg.set_value(input_tag, command)
                self.submit_callback(input_tag, app_data)
        return _callback

    def _network_change_command(self, terminal_prefix: str, command: str):
        """Like command(), but auto-restarts the node after completion for DDS re-discovery."""
        def _callback(sender=None, app_data=None):
            self._pending_network_restart = True
            self.command(terminal_prefix, command)(sender, app_data)
        return _callback

    def topic_select_callback(self, sender, app_data):
        for prefix in self.status_prefixes:
            dpg.configure_item(f"{prefix}_topic_group", show=(prefix == app_data))

    class terminal_tab_class():
        def __init__(self, terminal_prefix, node):
            with dpg.tab(tag=f"{terminal_prefix}_tab", label=terminal_prefix):
                with dpg.child_window(width=-1, height=-1, border=True, tag=""):
                    with dpg.child_window(tag=f"{terminal_prefix}_output_terminal", 
                                          width=-1, 
                                          height=-30, 
                                          border=True):
                        dpg.add_selectable(label=">", span_columns=True)
                    btn_label = "Interupt"
                    btn_width = node.estimate_button_width(btn_label)
                    with dpg.group(horizontal=True, horizontal_spacing=node.padding):
                        dpg.add_input_text(tag=f"{terminal_prefix}_input_field",
                                            on_enter=True,
                                            callback=node.submit_callback,
                                            width=-(btn_width + node.padding),
                                            )
                        dpg.add_button(tag=f"{terminal_prefix}_interupt",
                                    label=btn_label,
                                    callback=node.interupt_callback,
                                    width=btn_width)

    def _terminal_print(self, text: str, terminal_tag: str = "output_terminal"):
        def _copy(sender, app_data):
            label = dpg.get_item_label(sender)
            if label is not None:
                dpg.set_clipboard_text(label[2:] if label.startswith("> ") else label)
                dpg.set_value(sender, False)
        dpg.add_selectable(label=text, span_columns=True, parent=terminal_tag, callback=_copy)
        dpg.set_y_scroll(terminal_tag, -1.0)

    def estimate_button_width(self, label: str, char_width=8, padding=16) -> int:
        return len(label) * char_width + padding

    def exit_callback(self, sender, app_data):
        dpg.stop_dearpygui()
        
    def restart_callback(self, sender, app_data):
        self._restart = True
        dpg.stop_dearpygui()
    
    def ip_callback(self):
        threading.Thread(target=self.ping_check, daemon=True).start()

    def ping_check(self):
        addresses = [["WIFI", "1"],
                     ["Create3", "4"],
                     ["RaspberryPi", "3"]]
        for set in addresses:
            connection_prefix = set[0]
            ip_end = set[1]
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", f"192.168.1.{ip_end}"],
                # ["ping", "-c", "1", "-W", "1", f"8.8.8.8"],
                capture_output=True
            )
            alive = result.returncode == 0
            color = GREEN if alive else RED
            dpg.configure_item(f"{connection_prefix}_status", color=color, fill=color)

    def submit_callback(self, sender, app_data):
        prefix = dpg.get_item_alias(sender).replace("_input_field", "")
        output_tag = f"{prefix}_output_terminal"
        cmd = dpg.get_value(sender)
        dpg.set_value(sender, "")
        dpg.focus_item(sender)
        proc = self.terminal_procs[prefix]
        if proc.is_running():
            proc.send_input(cmd)
        else:
            self._terminal_print(f"> {cmd}", output_tag)
            proc.run(cmd)

    def interupt_callback(self, sender, app_data):
        prefix = dpg.get_item_alias(sender).replace("_interupt", "")
        output_tag = f"{prefix}_output_terminal"
        input_tag = f"{prefix}_input_field"
        self.terminal_procs[prefix].interrupt()
        self._terminal_print("[interrupted]", output_tag)
        dpg.focus_item(input_tag)

    def monitor_health_callback(self):
        """Check if topic monitors are receiving data within their max_interval_s threshold."""
        monitors = [
            self.battery_state,
            self.diagnostics_agg,
            # self.hazard_detection,
            self.scan,
            self.odom,
            self.imu,
            self.tf,
            # self.scan_masked,
            self.rfid,
            self.dock_status,
            self.cmd_vel,
            self.map,
            self.costmap,
            self.rfid_goal,
            ]
        
        current_time = datetime.now(tz=timezone.utc)
        
        for monitor in monitors:
            if monitor.old_timestamp is None:
                monitor.is_alive = False
            else:
                elapsed = (current_time - monitor.old_timestamp).total_seconds()
                monitor.is_alive = elapsed < monitor.max_interval_s
            if monitor.is_good and monitor.is_alive:
                color = GREEN
            elif monitor.is_alive:
                color = YELLOW 
            else:
                color = RED
            dpg.configure_item(f"{monitor.tag}_status", color=color, fill=color)
    
    class topic_monitor():
        def __init__(self, node, msg_type, topic, tag = None, qos_profile = qos, max_interval_s = 10, print_interval = 0.05):
            self.subscription = node.create_subscription(
                msg_type=msg_type,
                topic=topic,
                callback=self.subscription_callback,
                qos_profile=qos_profile
                )
            
            self.topic = topic
            if tag is None:
                self.tag = self.topic
            else:
                self.tag = tag

            self.input_msg = None
            self.max_interval_s = max_interval_s
            self.old_timestamp = None
            self.current_timestamp = None
            self.time_delta = None
            self.is_alive = False
            self.is_good = False

            self.output_queue = node.output_queue
            self.terminal_tag = f"{self.tag}_output_terminal"
            self.tab_tag = f"{self.tag}_tab"
            self._last_print_time = None
            self._print_interval = print_interval

        def subscription_callback(self, input_msg):
            self.input_msg = input_msg
            self.is_alive = self.topic_is_alive()
            if self.is_alive:
                self.is_good = self.topic_is_good()
            else:
                self.is_good = False

            active_tab = dpg.get_value("tab_bar")
            tab_alias = None if active_tab is None else dpg.get_item_alias(active_tab)
            selected_topic = dpg.get_value("topic_selector")
            if self.tab_tag != tab_alias and self.tag != selected_topic:
                return

            now = datetime.now(tz=timezone.utc)
            if self._last_print_time is None or (now - self._last_print_time).total_seconds() >= self._print_interval:
                self._last_print_time = now
                for line in str(input_msg).split(','):
                    self.output_queue.put((self.terminal_tag, line.strip()))
                self.output_queue.put((self.terminal_tag, "---"))
            
        def topic_is_alive(self):
            self.current_timestamp = datetime.now(tz=timezone.utc) # could get this from header

            if self.old_timestamp is None:
                self.old_timestamp = self.current_timestamp
                self.time_delta = 0.0
                return True

            self.time_delta = self.seconds_between(self.old_timestamp, self.current_timestamp)
            self.old_timestamp = self.current_timestamp
            return self.time_delta < self.max_interval_s

        def topic_is_good(self):
            match self.topic:
                case '/battery_state':
                    if not isinstance(self.input_msg, BatteryState):
                        return False
                    percentage = self.input_msg.percentage*100
                    
                    dpg.set_value("battery_percent_text", f"({round(percentage)}%)")
                    return percentage > 20
                case '/diagnostics_agg':
                    if not isinstance(self.input_msg, DiagnosticArray):
                        return False
                    statuses = self.input_msg.status
                    if not statuses:
                        return False
                    _ignore_patterns = ('joystick', 'frequency too low', 'frequency too high', 'no events recorded', 'stale', 'battery',
                                        'undocked', 'docked', 'no hazards detected', 'enabled', 'hazard detection', 'wheel status', 'dock status')
                    for status in statuses:
                        level = status.level if isinstance(status.level, int) else ord(status.level)
                        if level not in (0, 1, 3):
                            values_text = ' '.join(v.value.lower() + ' ' + v.key.lower() for v in status.values)
                            msg_text = status.message.lower()
                            if any(p in values_text or p in msg_text for p in _ignore_patterns):
                                continue
                            return False
                    return True
                    
                # case "/hazard_detection":
                #     if not isinstance(self.input_msg, HazardDetectionVector):
                #         return False
                #     detections = self.input_msg.detections
                #     if len(detections) > 0:
                #         return False
                #     return True
                    
                case "/scan":
                    if not isinstance(self.input_msg, LaserScan): 
                        return False
                    ranges = self.input_msg.ranges
                    return isinstance(ranges, array.array)
                    
                case "/odom": return isinstance(self.input_msg, Odometry)
                case "/imu": return isinstance(self.input_msg, Imu)
                case "/tf": return isinstance(self.input_msg, TFMessage)

                case "/scan_masked":
                    if not isinstance(self.input_msg, LaserScan):
                        return False
                    ranges = self.input_msg.ranges
                    return isinstance(ranges, array.array)

                case "/rfid": return isinstance(self.input_msg, String)
                case "/dock_status":
                    if not isinstance(self.input_msg, DockStatus):
                        return False
                    return not self.input_msg.is_docked
                case '/cmd_vel': return isinstance(self.input_msg, Twist)
                case '/map': return isinstance(self.input_msg, OccupancyGrid)
                case '/local_costmap/costmap': return isinstance(self.input_msg, OccupancyGrid)
                case '/rfid_goal': return isinstance(self.input_msg, String)
                

        def seconds_between(self, older: datetime, newer: datetime) -> float:
            return (newer - older).total_seconds()

    def timer_callback(self):
        try:
            while True:
                tag, text = self.output_queue.get_nowait()
                self._terminal_print(text, tag)
        except queue.Empty:
            pass

        if self._pending_network_restart and not self.terminal_procs['pc_blocking'].is_running():
            self._pending_network_restart = False
            self.get_logger().info('Network changed, restarting for DDS re-discovery...')
            self._restart = True
            dpg.stop_dearpygui()

        if not dpg.is_dearpygui_running():
            self.get_logger().info(f'No longer rendering, exiting UI Node.')
            raise SystemExit
        dpg.render_dearpygui_frame()


def main(args=None):
    # Ensure ROS env vars are set even when launched outside a sourced shell
    os.environ.setdefault('ROS_DOMAIN_ID', '0')
    os.environ.setdefault('ROS_LOCALHOST_ONLY', '0')
    os.environ.setdefault('RMW_IMPLEMENTATION', 'rmw_fastrtps_cpp')
    node = None
    rclpy.init(args=args)
    try:
        node = ui_node_class()
        node._restart = False
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        print("\nExiting.")
    finally:
        do_restart = node._restart if node is not None else False
        if node is not None:
            node.destroy_node()
        dpg.destroy_context()
        rclpy.try_shutdown()
    if do_restart:
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == '__main__':
    main()
    
