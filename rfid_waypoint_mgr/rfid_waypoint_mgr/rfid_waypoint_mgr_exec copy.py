#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovarianceStamped

import time

node_name = 'rfid_waypoint_mgr_node'
input_msg_type = String
pose_msg_type = PoseWithCovarianceStamped
output_msg_type = PoseStamped

relative_input_topic = 'input'
pose_topic_input = '/pose'
relative_output_topic = 'output'

qos = 10

class rfid_waypoint_mgr_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')
        
        self.declare_parameter('wait_time_s', 5) # declare parameters with default values, if any

        self.wait_time_s = self.get_parameter('wait_time_s').value

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

        self.current_pose: PoseStamped | None = None
        self.create_subscription(
            pose_msg_type,
            pose_topic_input,
            self.pose_callback,
            qos
        )
        
    def subscriber_callback(self, input_msg: input_msg_type):
        self.get_logger().info(f'Input: {str(input_msg)}')
        output_msg = self.get_robot_pose()
        if output_msg is None:
            self.get_logger().error('Could not get robot pose, not publishing')
            return
        time.sleep(self.wait_time_s)
        self.node_publisher_.publish(output_msg)

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose
        self.current_pose = pose

    def get_robot_pose(self) -> PoseStamped | None:
        if self.current_pose is None:
            self.get_logger().warn('No pose received yet on /pose')
        return self.current_pose

def main(args=None):
    rclpy.init(args=args)
    node = rfid_waypoint_mgr_node_class()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()