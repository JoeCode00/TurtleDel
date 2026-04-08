#!/usr/bin/env python3

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

class ui_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')
        
        self.declare_parameter('basic_param', 'basic_default') # declare parameters with default values, if any

        self.basic_param = str(self.get_parameter('basic_param').value)

        dpg.create_context()
        viewport_width = int(1920/2)
        viewport_height = int(1080)
        padding = 10
        dpg.create_viewport(title='TurtleDel', 
                            width=viewport_width, 
                            height=viewport_height, 
                            x_pos=0, 
                            y_pos=0,
                            decorated=False,
                            )

        window_width = viewport_width - 2 * padding
        top_width = int(window_width - 2 * padding)
        col_gap = padding
        
        window_height = viewport_height - 2 * padding
        top_height = int((window_height - 2 * padding) / 2)

    
        col_width = int((top_width - col_gap) / 2)

        with dpg.window(tag="window",
                        label="", 
                        width=viewport_width-2*padding, 
                        height=viewport_height-2*padding, 
                        pos=(padding, padding),
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
                            dpg.add_text("Hello, world")
                            dpg.add_button(label="Save", width=-1)
                            dpg.add_input_text(label="string", default_value="Quick brown fox", width=-1)
                            dpg.add_slider_float(label="float", default_value=0.273, max_value=1, width=-1)

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
                    with dpg.group(tag="bottom_container",
                                horizontal=True, 
                                horizontal_spacing=col_gap,
                                ):
                        with dpg.child_window(width=-1, height=-1, border=True, tag=""):
                            # Scrollable output display area
                            with dpg.child_window(tag="output_terminal", width=-1, height=200, border=True):
                                dpg.add_text(">")
                            # User Input Field
                            btn_label = "Interupt"
                            btn_width = self.estimate_button_width(btn_label)
                            with dpg.group(horizontal=True, horizontal_spacing=padding):
                                dpg.add_input_text(tag="input_field",
                                                   on_enter=True,
                                                   callback=self.submit_callback,
                                                   width=-(btn_width + padding),
                                                   )
                                dpg.add_button(tag="k_interupt", label=btn_label,
                                               callback=self.interupt_callback, width=btn_width)
                                
        with dpg.theme() as terminal_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0)
        dpg.bind_item_theme("output_terminal", terminal_theme)

        dpg.setup_dearpygui()
        dpg.show_viewport()

        self.node_subscriber_ = self.create_subscription(
            msg_type=input_msg_type,
            topic=relative_input_topic,
            callback=self.subscriber_callback,
            qos_profile=qos
            )
        
        self.node_publisher_ = self.create_publisher(
            msg_type = output_msg_type, 
            topic = relative_output_topic,
            qos_profile = qos
            )
        
        self.timer = self.create_timer(0.05, self.timer_callback)

    def estimate_button_width(self, label: str, char_width = 8, padding = 16) -> int:
        return len(label) * char_width + padding

    def submit_callback(self, sender, app_data):
        user_input = dpg.get_value("input_field")
        dpg.add_text(f"> {user_input}", parent="output_terminal")
        dpg.set_y_scroll("output_terminal", -1.0)
        dpg.set_value("input_field", "")
        dpg.focus_item("input_field")

    def interupt_callback(self, sender, app_data):
        dpg.add_text("Interupt", parent="output_terminal")
        dpg.set_y_scroll("output_terminal", -1.0)
        dpg.set_value("input_field", "")
        dpg.focus_item("input_field")
        
    def subscriber_callback(self, input_msg: input_msg_type):
        self.get_logger().info(f'Input: {str(input_msg)}')
        output_msg = output_msg_type()
        output_msg = input_msg
        self.node_publisher_.publish(output_msg)
        self.get_logger().info(f'Output: {str(output_msg)}')

    def timer_callback(self):
        # Your non-blocking loop logic here
        if not dpg.is_dearpygui_running():
            self.get_logger().info(f'No longer rendering, exiting UI Node.')
            raise SystemExit
        dpg.render_dearpygui_frame()


def main(args=None):
    node = None
    rclpy.init(args=args)
    try:
        node = ui_node_class()
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        print("\nExiting.")
    finally:
        if node is not None:
            node.destroy_node()
        dpg.destroy_context()
        rclpy.try_shutdown()
    
if __name__ == '__main__':
    main()