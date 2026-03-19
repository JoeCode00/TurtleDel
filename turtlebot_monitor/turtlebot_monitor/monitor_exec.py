#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from diagnostic_msgs.msg import DiagnosticArray as input_message_subclass
from std_msgs.msg import String as output_message_subclass

import time
import subprocess
from ping3 import ping

def terminal_cmd(command, timeout_s: int|float|None = None):
    try:
        if timeout_s is not None:
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True, timeout=timeout_s)
        else:
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        # print("Standard Output:")
        return result.stdout
        # print("Standard Error:")
        # print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")
        raise

def r_sleep(self, seconds: int):
    self.r_print(f"Waiting for {seconds} seconds.")
    time.sleep(seconds)

def data_flow_test(self, topic: str, timeout_s: float):
    self.r_print(f"Testing {topic} data.")
    try:
        data = terminal_cmd(f"ros2 topic echo {topic} --once", timeout_s=timeout_s)
    except:
        self.r_print(f"{topic} data test timed out after {timeout_s} seconds.")
        info = terminal_cmd(f"ros2 topic info {topic}").split("\n")
        topic_type = info[0].split(' ')[-1]
        topic_publishers = float(info[1].split(' ')[-1])
        topic_subscribers = float(info[2].split(' ')[-1])
        if topic_publishers == 0:
            raise RuntimeError(f"There are no publishers for {topic}, so that may be why no data was recieved, or this PC cannot discover the publishers.")
        else:
            raise RuntimeError(f"There are {topic_publishers} publishers on {topic}, but no data was recieved. This topic may have an unreadable type {topic_type}.")
    self.r_print(f"Found {topic} data.")
    return data

node_name = 'monitor_node'
input_msg_type = input_message_subclass
output_msg_type = output_message_subclass

relative_input_topic = 'input'
relative_output_topic = 'output'

qos = 10

class monitor_node_class(Node): # change node class name to <node_class>
    def r_print(self, text: str):
        self.get_logger().info(text)

    def __init__(self):
        super().__init__(node_name)
        self.r_print(f'init {node_name}')
        
        self.declare_parameter('network_name', 'turtlebot-hub-5G') # declare parameters with default values, if any
        self.declare_parameter('pi_address', '192.168.1.3')
        self.declare_parameter('create_3_address', '192.168.1.4')
        self.declare_parameter('ping_ms_max', '250')

        self.network_name = str(self.get_parameter('network_name').value)
        self.pi_address = str(self.get_parameter('pi_address').value)
        self.create_3_address = str(self.get_parameter('create_3_address').value)
        self.ping_ms_max = float(self.get_parameter('ping_ms_max').value)

        def ssh_instructions():
            self.r_print(f"SSH into the Raspberry pi by typing: 'SSH ubuntu@{self.pi_address} with password turtlebot4.")

        def create_3_web_instructions():
            self.r_print(f"Check if the Create 3 is functioning by opening a web page and going to {self.pi_address}:8080. There you may want to reboot the application or the Create 3 (called the Robot).")

        def network_instructions():
            self.r_print(f"Check if the device is on the network. Go to http://192.168.1.1 and use username: admin , password turtlebot4PW!. Look at 'Attached Devices'.")

        self.r_print("Starting up.")
        self.r_print(f"Checking connection to {self.network_name}")
        trial = 0
        max_trials = 3
        sleep_seconds = 10
        matching_connection = False

        while not matching_connection and trial < max_trials:
            try:
                connection = terminal_cmd(f"nmcli connection show --active | grep {self.network_name}")
                if connection != '':
                    matching_connection = True
            except:
                self.r_print(f"Not connected to {self.network_name}")
                self.r_print(f"Connecting to {self.network_name} ({trial+1}/{max_trials}) ")
                terminal_cmd(f'nmcli connection up id "{self.network_name}"')
                r_sleep(self, sleep_seconds)
                trial += 1
                continue

        if not matching_connection:
            raise ConnectionError(f"Could not connect to {self.network_name}, need to plug in the router nearby and wait for 2nd green light to appear.")
        
        try:
            ping_ms = ping(self.pi_address,)
        except Exception as e:
            raise ConnectionError(f"Could not ping the Rapsberry Pi at {self.pi_address}. {e}") 
        # if ping_ms is None or ping_ms > self.ping_ms_max:
        #     raise ConnectionError(f"Ping to Raspberry Pi was too long, {ping_ms} ms (max {self.ping_ms_max})")
        
        try:
            ping_ms = ping(self.create_3_address)
        except Exception as e:
            raise ConnectionError(f"Could not ping the Create 3 at {self.create_3_address}. {e}") 
        # if ping_ms is None or ping_ms > self.ping_ms_max:
        #     raise ConnectionError(f"Ping to Create 3 was too long, {ping_ms} ms (max {self.ping_ms_max})")
        
        
        needed_topics = ["/battery_state", "/cmd_vel", "/diagnostics", "/diagnostics_agg", "/diagnostics_toplevel_state", "/dock_status", "/function_calls", "/hazard_detection", "/hmi/buttons", "/hmi/display", "/hmi/display/message", "/hmi/led", "/imu", "/interface_buttons", "/ip", "/joint_states", "/joy", "/joy/set_feedback", "/mouse", "/oakd/rgb/preview/image_raw", "/parameter_events", "/robot_description", "/rosout", "/scan", "/tf", "/tf_static", "/wheel_status",]
        trial = 0
        max_trials = 3
        sleep_seconds = 10
        all_topics_listed = False
        while not all_topics_listed and trial < max_trials:
            recieved_topics = terminal_cmd("ros2 topic list").split("\n")
            missing_topics = [topic for topic in needed_topics if topic not in recieved_topics]

            if len(missing_topics) > 0:
                self.r_print(f"Missing topics: {missing_topics}")
                self.r_print(f"Waiting to see if more topics appear later ({trial+1}/{max_trials}).")
                r_sleep(self, sleep_seconds)
                trial += 1
                continue
            all_topics_listed = True

        if not all_topics_listed:
            if "/scan" in missing_topics:
                ssh_instructions()
                raise RuntimeError("/scan is missing, which may indicate that the Pi is not running ROS2 or failed to launch the rplidar. Reboot the pi with: sudo reboot")
            if "/battery_state" in missing_topics:
                create_3_web_instructions()
                raise RuntimeError("/battery_state is missing, which may indicate that the Create 3 is not running ROS2 or has another issue. Reboot the application and the robot.")
            if "/odom" in missing_topics:
                create_3_web_instructions()
                raise RuntimeError("/odom is missing, which is a timestamped topic. This may indicate that the Create 3's time has diverged from that of the computer or the Raspberry Pi. This can be configured in the web portal using instructions in the README.md.")
            raise RuntimeError(f"There are {len(missing_topics)} required topics missing.")
        self.r_print("All required topics are found.")
        
        data_flow_timeout_s = 120
        data_flow_test(self, topic="/scan", timeout_s=data_flow_timeout_s)
        dock_status_data = data_flow_test(self, topic="/dock_status", timeout_s=data_flow_timeout_s)
        
        self.is_docked = True
        self.battery_percentage = 0
        self.hazard_detected_int = -1


        self.node_subscriber_ = self.create_subscription(
            msg_type=input_msg_type,
            topic=relative_input_topic,
            callback=self.subscriber_callback,
            qos_profile=qos
            )
        
        # self.node_publisher_ = self.create_publisher(
        #     msg_type = output_msg_type, 
        #     topic = relative_output_topic,
        #     qos_profile = qos
        #     )
        
    def subscriber_callback(self, input_msg: input_msg_type):
        def print_kv(status):
            for kv in status.values:      # kv is a KeyValue
                key = kv.key
                value = kv.value
                self.r_print(f'  {key}: {value}')
        
        for status in input_msg.status:  # status is a DiagnosticStatus
            level = status.level          # byte: 0=OK, 1=WARN, 2=ERROR, 3=STALE
            name = status.name            # str: component name, e.g. "imu"
            message = status.message      # str: human-readable summary
            hardware_id = status.hardware_id  # str: hardware identifier

            if level == 2:
                self.r_print(f'{name} [ERROR]: {message} (hw: {hardware_id})')
                print_kv(status)

            if name == "/Turtlebot4/Create3/Battery/turtlebot4_diagnostics: Battery Percentage":
                kv = status.values[0]
                value = kv.value
                print(f"Battery Percentage: {value}")
            

def main(args=None):
    rclpy.init(args=args)
    node = monitor_node_class()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()