#!/usr/bin/env python3

import os
import re
import sys
import pty
import select
import signal
import shlex
import queue
import threading
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
try:
    import dearpygui.dearpygui as dpg
except:
    raise ImportError("pip install dearpygui")

node_name = 'ui_node'
input_msg_type = String
output_msg_type = String

relative_input_topic = 'input'
relative_output_topic = 'output'

qos = 10

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

        try:
            args = shlex.split(command)
        except ValueError as e:
            self.output_queue.put((self.terminal_tag, f"[parse error: {e}]"))
            return

        master_fd, slave_fd = pty.openpty()
        self._master_fd = master_fd
        try:
            self.process = subprocess.Popen(
                args,
                stdout=slave_fd,
                stderr=slave_fd,
                stdin=slave_fd,
                close_fds=True,
                start_new_session=True,
            )
        except FileNotFoundError:
            self.output_queue.put((self.terminal_tag, f"[command not found: {args[0]}]"))
            os.close(master_fd)
            os.close(slave_fd)
            return
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
                elif self.process.poll() is not None:
                    break
        finally:
            if buf:
                text = _strip_ansi(buf.decode('utf-8', errors='replace').rstrip('\r'))
                if text:
                    self.output_queue.put((self.terminal_tag, text))
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            rc = self.process.wait()
            self.output_queue.put((self.terminal_tag, f"[exited: {rc}]"))

    def interrupt(self):
        if self.is_running():
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
            except ProcessLookupError:
                pass


class ui_node_class(Node):
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.declare_parameter('basic_param', 'basic_default')
        self.basic_param = str(self.get_parameter('basic_param').value)

        self.output_queue = queue.Queue()
        self.terminal_procs = {
            prefix: TerminalProcess(f"{prefix}_output_terminal", self.output_queue)
            for prefix in ['ssh', 'diag', 'startup', 'docking', 'scan_mask', 'rqt', 'view', 'rviz', 'slam', 'nav']
        }

        dpg.create_context()
        self.viewport_width = int(1920/2)
        self.viewport_height = int(1080)
        self.padding = 10
        dpg.create_viewport(title='TurtleDel',
                            width=self.viewport_width,
                            height=self.viewport_height,
                            x_pos=0,
                            y_pos=0,
                            decorated=False,
                            )

        window_width = self.viewport_width - 2 * self.padding
        top_width = int(window_width - 2 * self.padding)
        col_gap = self.padding

        window_height = self.viewport_height - 2 * self.padding
        top_height = int((window_height - 2 * self.padding) / 2)

        col_width = int((top_width - col_gap) / 2)

        terminal_prefixes = ['ssh', 'diag', 'startup', 'docking', 'scan_mask', 'rqt', 'view', 'rviz', 'slam', 'nav']

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
                                               label="RESTART",
                                               callback=self.restart_callback,
                                               )
                                dpg.add_text("TurtleDel: Group 2 User Interface")
                            dpg.add_text("System Status:")
                            
                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                for status_prefix in ["WIFI", "RPI", "C3"]:
                                    self.status_indicator(status_prefix, self)
                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                for status_prefix in ["Batt", "Diag", "Hazard", "Docked"]:
                                    self.status_indicator(status_prefix, self)
                            with dpg.group(horizontal=True, horizontal_spacing=self.padding):
                                for status_prefix in ["/scan", "/scan_masked", "/odom", "/rfid", "/oakd"]:
                                    self.status_indicator(status_prefix, self)
                            

                        with dpg.child_window(width=-1, height=-1, border=True, tag="right_col"):
                            dpg.add_text("Hello, world")
                            dpg.add_button(label="Save", width=-1)
                            dpg.add_input_text(label="string", default_value="Quick brown fox", width=-1)
                            dpg.add_slider_float(label="float", default_value=0.273, max_value=1, width=-1)

                dpg.add_spacer(height=col_gap//4)
                with dpg.child_window(tag="bottom_window",
                                      width=-1,
                                      height=-1,
                                      border=True):
                    with dpg.tab_bar(label="Tab Bar"):
                        
                        
                        for terminal_prefix in terminal_prefixes:
                            self.terminal_tab_class(terminal_prefix, self)
                        

        with dpg.theme() as terminal_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0)
        for terminal_prefix in terminal_prefixes:
            dpg.bind_item_theme(f"{terminal_prefix}_output_terminal", terminal_theme)

        dpg.setup_dearpygui()
        dpg.show_viewport()

        self.node_subscriber_ = self.create_subscription(
            msg_type=input_msg_type,
            topic=relative_input_topic,
            callback=self.subscriber_callback,
            qos_profile=qos
            )

        self.node_publisher_ = self.create_publisher(
            msg_type=output_msg_type,
            topic=relative_output_topic,
            qos_profile=qos
            )

        self.create_timer(0.05, self.timer_callback)

        self.create_timer(1, self.ip_callback)

    class status_indicator():
        def __init__(self, staus_prefix, node):
            radius=6
            with dpg.group(horizontal=True, horizontal_spacing=node.padding):
                with dpg.drawlist(width=2*radius, height=2.6*radius):
                    dpg.draw_circle(tag=f"{staus_prefix}_status",
                                    center=(radius, 1.6*radius), 
                                    radius=radius, 
                                    color=RED, 
                                    fill=RED, 
                                    label=f"{staus_prefix}"
                                    )
                dpg.add_text(f"{staus_prefix}")

    class terminal_tab_class():
        def __init__(self, terminal_prefix, node):
            with dpg.tab(label=terminal_prefix):
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
                     ["C3", "2"],
                     ["RPI", "3"]]
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", "192.168.1.3"],
            capture_output=True
        )
        alive = result.returncode == 0
        color = GREEN if alive else RED
        # DearPyGui is not thread-safe, so use configure_item carefully
        # or post to a queue and update in timer_callback instead
        dpg.configure_item("RPI_status", color=color, fill=color)


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

    def subscriber_callback(self, input_msg: input_msg_type):
        self.get_logger().info(f'Input: {str(input_msg)}')
        output_msg = output_msg_type()
        output_msg = input_msg
        self.node_publisher_.publish(output_msg)
        self.get_logger().info(f'Output: {str(output_msg)}')

    def timer_callback(self):
        try:
            while True:
                tag, text = self.output_queue.get_nowait()
                self._terminal_print(text, tag)
        except queue.Empty:
            pass

        if not dpg.is_dearpygui_running():
            self.get_logger().info(f'No longer rendering, exiting UI Node.')
            raise SystemExit
        dpg.render_dearpygui_frame()


def main(args=None):
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
    
