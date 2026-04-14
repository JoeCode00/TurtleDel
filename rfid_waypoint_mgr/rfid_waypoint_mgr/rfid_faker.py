#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import tf2_ros
from geometry_msgs.msg import TransformStamped, PoseStamped

node_name = 'rfid_faker_node'
qos = 10

class rfid_faker_node_class(Node):
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.rfid_frames: dict[str, PoseStamped] = {
            'rfid0': self.make_pose(-1.0, 0.0, 0.0),
            'rfid1': self.make_pose(-2.0, 0.0, 0.0),
        }

        self.create_timer(0.1, self.broadcast_frames)

    def make_pose(self, x: float, y: float, z: float) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = 1.0
        return pose

    def broadcast_frames(self):
        for frame_id, pose in self.rfid_frames.items():
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'map'
            t.child_frame_id = frame_id
            t.transform.translation.x = pose.pose.position.x
            t.transform.translation.y = pose.pose.position.y
            t.transform.translation.z = pose.pose.position.z
            t.transform.rotation = pose.pose.orientation
            self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = rfid_faker_node_class()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()