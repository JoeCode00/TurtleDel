#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import tf2_ros
from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped, PoseWithCovarianceStamped

node_name = 'rfid_joseph'
qos = 10

class rfid_joseph_node_class(Node):
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # self.rfid_pose: dict[str, PoseWithCovarianceStamped] = {
        #     'rfid0': self.make_pose(-1.0, 0.0, 0.0),
        #     'rfid1': self.make_pose(-2.0, 0.0, 0.0),
        # }
        self.pose_subscriber = self.create_subscription(
            msg_type=PoseWithCovarianceStamped,
            topic='/pose',
            callback=self.pose_callback,
            qos_profile=qos
        )

        self.rfid_subscriber = self.create_subscription(
            msg_type=String,
            topic='/rfid',
            callback=self.rfid_callback,
            qos_profile=qos
        )
        
        self.current_pose = self.make_pose()
        self.pose_dict = {}

        self.create_timer(0.1, self.broadcast_poses)

    def rfid_callback(self, input_msg: String):
        id = input_msg.data
        self.pose_dict[id] = [self.current_pose]
            
    def pose_callback(self, input_msg: PoseWithCovarianceStamped):
        # self.get_logger().info(f'Input: {str(input_msg)}')
        self.current_pose = input_msg

    def make_pose(self) -> PoseWithCovarianceStamped:
        rfid_pose = PoseWithCovarianceStamped()
        rfid_pose.header.frame_id = 'map'
        rfid_pose.pose.pose.position.x = 0.0
        rfid_pose.pose.pose.position.y = 0.0
        rfid_pose.pose.pose.position.z = 0.0
        rfid_pose.pose.pose.orientation.w = 1.0
        return rfid_pose

    def broadcast_poses(self):
        # for frame_id, pose in self.rfid_pose.items():
        for i, id in enumerate(self.pose_dict.keys()):
            pose = self.pose_dict[id][0]
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'map'
            t.child_frame_id = f"rfid{i}"
            t.transform.translation.x = pose.pose.pose.position.x
            t.transform.translation.y = pose.pose.pose.position.y
            t.transform.translation.z = pose.pose.pose.position.z
            t.transform.rotation = pose.pose.pose.orientation
            self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = rfid_joseph_node_class()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()