#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

import tf2_ros

node_name = 'rfid_waypoint_mgr_node'
input_msg_type = String
output_msg_type = PoseStamped

relative_input_topic = 'input'
relative_output_topic = 'output'

qos = 10

class rfid_waypoint_mgr_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

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
        
    def subscriber_callback(self, input_msg: input_msg_type):
        frame_id = input_msg.data
        self.get_logger().info(f'Input: {frame_id}')
        try:
            transform = self.tf_buffer.lookup_transform(
                'map', 
                frame_id,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=1.0)
            )
        except Exception as e:
            self.get_logger().error(f'Could not look up TF frame "{frame_id}": {e}')
            return

        output_msg = PoseStamped()
        output_msg.header.stamp = self.get_clock().now().to_msg()
        output_msg.header.frame_id = 'map'
        output_msg.pose.position.x = transform.transform.translation.x
        output_msg.pose.position.y = transform.transform.translation.y
        output_msg.pose.position.z = transform.transform.translation.z
        output_msg.pose.orientation = transform.transform.rotation
        self.node_publisher_.publish(output_msg)

def main(args=None):
    rclpy.init(args=args)
    node = rfid_waypoint_mgr_node_class()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()