#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import tf2_ros
from geometry_msgs.msg import TransformStamped, PoseWithCovarianceStamped

node_name = 'rfid_faker_node'
qos = 10

class rfid_faker_node_class(Node):
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.rfid_pose: dict[str, PoseWithCovarianceStamped] = {
            'rfid0': self.make_pose(-1.0, 0.0, 0.0),
            'rfid1': self.make_pose(-2.0, 0.0, 0.0),
        }

        self.create_timer(0.1, self.broadcast_pose)

    def make_pose(self, x: float, y: float, z: float) -> PoseWithCovarianceStamped:
        rfid_pose = PoseWithCovarianceStamped()
        rfid_pose.header.frame_id = 'map'
        rfid_pose.pose.pose.position.x = x
        rfid_pose.pose.pose.position.y = y
        rfid_pose.pose.pose.position.z = z
        rfid_pose.pose.pose.orientation.w = 1.0
        return rfid_pose

    def broadcast_pose(self):
        for frame_id, pose in self.rfid_pose.items():
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'map'
            t.child_frame_id = frame_id
            t.transform.translation.x = pose.pose.pose.position.x
            t.transform.translation.y = pose.pose.pose.position.y
            t.transform.translation.z = pose.pose.pose.position.z
            t.transform.rotation = pose.pose.pose.orientation
            self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = rfid_faker_node_class()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()