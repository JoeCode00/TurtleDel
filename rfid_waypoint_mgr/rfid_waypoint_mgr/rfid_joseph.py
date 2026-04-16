#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import tf2_ros
from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped, PoseWithCovarianceStamped

import numpy as np
import math

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
        
        self.current_pose = None
        self.pose_dict = {}

        self.create_timer(0.1, self.broadcast_poses)

    def rfid_callback(self, input_msg: String):
        id = input_msg.data
        if self.current_pose is None:
            return

        if id not in self.pose_dict.keys():
            sample_count = 1
            updated_pose = self.current_pose
        else:
            old_pose = self.pose_dict[id][0]
            sample_count = self.pose_dict[id][1] + 1
            updated_pose = self.average_pose(old_pose, self.current_pose, sample_count)
        
        self.pose_dict[id] = [updated_pose, sample_count]

    def pose_callback(self, input_msg: PoseWithCovarianceStamped):
        # self.get_logger().info(f'Input: {str(input_msg)}')
        self.current_pose = input_msg

    def make_pose(self, px=0, py=0, pz=0, qx=0, qy=0, qz=0, qw=1) -> PoseWithCovarianceStamped:
        rfid_pose = PoseWithCovarianceStamped()
        rfid_pose.header.frame_id = 'map'
        rfid_pose.pose.pose.position.x = float(px)
        rfid_pose.pose.pose.position.y = float(py)
        rfid_pose.pose.pose.position.z = float(pz)
        rfid_pose.pose.pose.orientation.x = float(qx)
        rfid_pose.pose.pose.orientation.y = float(qy)
        rfid_pose.pose.pose.orientation.z = float(qz)
        rfid_pose.pose.pose.orientation.w = float(qw)
        return rfid_pose
    
    import numpy as np

    def unit_vector(self, data, axis=None, out=None) -> np.ndarray:
        """Return ndarray normalized by length, i.e. Euclidean norm, along axis.
        """
        if out is None:
            data = np.array(data, dtype=np.float64, copy=True)
            if data.ndim == 1:
                data /= math.sqrt(np.dot(data, data))
                return data
        else:
            if out is not data:
                out[:] = np.array(data, copy=False)
            data = out
        length = np.atleast_1d(np.sum(data*data, axis))
        np.sqrt(length, length)
        if axis is not None:
            length = np.expand_dims(length, axis)
        data /= length
        if out is None:
            return data

    def quaternion_slerp(self, quat0, quat1, mu) -> np.ndarray:
        """Return spherical linear interpolation between two quaternions
        @param quat0: quaternion (4x1 numpy array)
        @param quat1: quaternion (4x1 numpy array)
        @param levels: number of levels for interpolation
        @return all_q: all interpolated quaternions (list of quaternions)
        """
        q0 = self.unit_vector(quat0[:4])
        q1 = self.unit_vector(quat1[:4])
        d = np.clip(np.dot(q0.flatten(), q1.flatten()), -1.0, 1.0)
        angle = math.acos(d)

        if abs(angle) < 1e-10:
            return q0

        q_slerp = (np.sin((1 - mu) * angle) / np.sin(angle)) * q0 + (np.sin(mu * angle) / np.sin(angle)) * q1

        for i in range(4):
            if np.isnan(q_slerp[i]):
                raise ValueError(f"q_slerp {q_slerp} has a nan, quat0 = {quat0}, quat1 = {quat1}, mu = {mu}, q0 = {q0}, q1 = {q1}, d = {d},  angle = {angle}")

        return q_slerp

    def average_pose(self, old_pose:PoseWithCovarianceStamped, new_pose:PoseWithCovarianceStamped, sample_count:int|float):
        mu = 1/sample_count
        p_old = np.array([old_pose.pose.pose.position.x, old_pose.pose.pose.position.y, old_pose.pose.pose.position.z])
        p_new = np.array([new_pose.pose.pose.position.x, new_pose.pose.pose.position.y, new_pose.pose.pose.position.z])
        p_updated = (p_new-p_old)*mu+p_old

        quat_old = np.array([old_pose.pose.pose.orientation.x, old_pose.pose.pose.orientation.y, old_pose.pose.pose.orientation.z, old_pose.pose.pose.orientation.w]).transpose()
        quat_new = np.array([new_pose.pose.pose.orientation.x, new_pose.pose.pose.orientation.y, new_pose.pose.pose.orientation.z, new_pose.pose.pose.orientation.w]).transpose()
        
        
        q_updated = self.quaternion_slerp(quat_old, quat_new, mu).flatten().tolist()
        
        return self.make_pose(px=p_updated[0], py=p_updated[1], pz=p_updated[2], qx=q_updated[0], qy=q_updated[1], qz=q_updated[2], qw=q_updated[3])

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