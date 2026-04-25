#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import UInt16MultiArray as input_message_subclass 
from std_msgs.msg import UInt16MultiArray as output_message_subclass 

import time

node_name = 'basic_node'
input_msg_type = input_message_subclass
output_msg_type = output_message_subclass

relative_input_topic = 'input'
relative_output_topic = 'output'

qos = 10

class basic_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')
        
        self.declare_parameter('basic_param', 'basic_default') # declare parameters with default values, if any

        self.basic_param = str(self.get_parameter('basic_param').value)

        name = input("test: ")
        self.get_logger().info(f'out: {name}')
        self.get_logger().info('after input')

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
        
    def subscriber_callback(self, input_msg: input_msg_type):
        self.get_logger().info(f'Input: {str(input_msg)}')
        output_msg = output_msg_type()
        output_msg.data = str(input_msg)
        self.node_publisher_.publish(output_msg)
        self.get_logger().info(f'Output: {str(output_msg)}')

def main(args=None):
    rclpy.init(args=args)
    node = basic_node_class()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()