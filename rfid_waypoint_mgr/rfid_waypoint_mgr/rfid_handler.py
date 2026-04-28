#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import tf2_ros
from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import time
import pickle
import os

PKL_PATH = os.path.join(os.path.dirname(__file__), 'rfid.pkl')

pose_translation_threshold = 0.005
pose_rotation_threshold = 0.005
rfid_min_signals = 10

node_name = 'rfid_handler_node'

qos = 10

qos_best_effort = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE
)

class rfid_handler_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        try:
            with open(PKL_PATH, 'rb') as f:
                self.best_pose = pickle.load(f)
        except Exception:
            self.best_pose = {}
        self.reset_flag = False

        # RFID
        self.rfid_save = None
        self.rfid_prev = None
        self.time_prev = None
        self.deltas_t = []

        # Pose
        self.y_set = None
        self.x_set = None
        self.w_set = None

        self.x_prev = None
        self.y_prev = None
        self.z_prev = None

        self.rfid_goal_subscriber = self.create_subscription(
            msg_type=String,
            topic="/rfid_goal",
            callback=self.subscriber_callback,
            qos_profile=qos_best_effort
            )
        
        self.rfid_subscriber = self.create_subscription(
            msg_type=String,
            topic="/rfid",
            callback=self.rfid_callback,
            qos_profile=qos
            )
        
        self.pose_subscriber = self.create_subscription(
            msg_type=Odometry,
            topic="/odom",
            callback=self.pose_callback,
            qos_profile=qos_best_effort
            )
        
        self.goal_pose_publisher = self.create_publisher(
            msg_type=PoseStamped, 
            topic="/goal_pose",
            qos_profile=qos
            )
        
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.create_timer(0.1, self.broadcast_poses)

    def broadcast_poses(self):
        for i, id in enumerate(self.best_pose.keys()):
            name = self.best_pose[id]["name"]
            pose = self.best_pose[id]["pose"]
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'map'
            t.child_frame_id = f"rfid_{name}" #rfid_ prefix required by UI node to pick out RFID transforms from all of the transforms on /tf.
            t.transform.translation.x = pose.pose.pose.position.x
            t.transform.translation.y = pose.pose.pose.position.y
            t.transform.translation.z = pose.pose.pose.position.z
            t.transform.rotation = pose.pose.pose.orientation
            self.tf_broadcaster.sendTransform(t)

    def reset(self, pose_set: Odometry):
        rfid_to_save = self.rfid_save if self.rfid_save else self.rfid_prev

        try:
            transform = self.tf_buffer.lookup_transform(
                'map', 'base_link',
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.5)
            )
            map_pose = Odometry()
            map_pose.header.frame_id = 'map'
            map_pose.pose.pose.position.x = transform.transform.translation.x
            map_pose.pose.pose.position.y = transform.transform.translation.y
            map_pose.pose.pose.position.z = transform.transform.translation.z
            map_pose.pose.pose.orientation = transform.transform.rotation
            pose_set = map_pose
        except Exception as e:
            self.get_logger().warn(f'Could not look up map→base_link TF; skipping pose save: {e}')
            rfid_to_save = None

        if rfid_to_save:
            ave = 100.0 # practically infinity
            if len(self.deltas_t) >= rfid_min_signals:
                self.deltas_t.pop() # remove last time delta so as not to skew the average
                ave = sum(self.deltas_t) / len(self.deltas_t)
        
            if rfid_to_save not in self.best_pose:
                pose_set_x = pose_set.pose.pose.position.x
                pose_set_y = pose_set.pose.pose.position.y
                pose_set_z = pose_set.pose.pose.position.z
                name = input(f"Please name the RFID at ({round(pose_set_x, 1)}, {round(pose_set_y, 1)}, {round(pose_set_z, 1)}): ")
                self.best_pose[rfid_to_save] = {"time_period": ave, "pose": pose_set, "name": name}
                # print("\n\nNEW RFID")
                # for k, v in self.best_pose.items():    
                #     print(f"{k}:")    
                #     if isinstance(v, dict):        
                #         for ik, iv in v.items():            
                #             print(f"  {ik}: {iv}")    
                #     else:        
                #         print(f"  {v}")
            else:
                if ave < self.best_pose[rfid_to_save]["time_period"]:
                    self.best_pose[rfid_to_save] = {"time_period": ave, "pose": pose_set, "name": self.best_pose[rfid_to_save]["name"]}
                    # print("\n\nBetter Pose found for RFID = " + str(rfid_to_save))
                    # for k, v in self.best_pose.items():    
                    #     print(f"{k}:")    
                    #     if isinstance(v, dict):        
                    #         for ik, iv in v.items():            
                    #             print(f"  {ik}: {iv}")    
                    #     else:        
                    #         print(f"  {v}")
        
        self.x_set = pose_set.pose.pose.position.x
        self.y_set = pose_set.pose.pose.position.y
        self.w_set = pose_set.pose.pose.orientation.w
        self.x_prev = None
        self.y_prev = None
        self.z_prev = None
        self.rfid_save = None
        self.deltas_t = []
        self.reset_flag = False

    def pose_callback(self, msg: Odometry):
        if self.x_prev is not None and self.y_prev is not None and self.w_prev is not None:
            x_diff = abs(msg.pose.pose.position.x - self.x_prev)
            y_diff = abs(msg.pose.pose.position.y - self.y_prev)
            w_diff = abs(msg.pose.pose.orientation.w - self.w_prev)
            # print(w_diff)

            if (x_diff > pose_translation_threshold): self.reset_flag = True
            if (y_diff > pose_translation_threshold): self.reset_flag = True
            if (w_diff > pose_rotation_threshold): self.reset_flag = True

        if self.reset_flag:
            # print("\nPose Changed\n")
            x_diff = 0
            y_diff = 0
            w_diff = 0
            self.reset(msg)
            
        self.x_prev = msg.pose.pose.position.x
        self.y_prev = msg.pose.pose.position.y
        self.w_prev = msg.pose.pose.orientation.w

    def rfid_callback(self, msg: String):
        now = time.time()
        # rfid_ping = msg.data
        # msg.data = str(rfid_ping)

        if self.time_prev is not None:
            delta = now - self.time_prev
            self.deltas_t.append(delta)

            if self.rfid_prev != msg.data:
                self.reset_flag = True
                self.rfid_save = self.rfid_prev
            # print("\nRFID = " + msg.data)
            # len_delta_arr = len(self.deltas_t) - 1
            # print("Delta t" + str(len_delta_arr) + " = " + str(self.deltas_t[len_delta_arr]))
        
        self.time_prev = now
        self.rfid_prev = msg.data
        
    def subscriber_callback(self, input_msg: String):
        frame_id = input_msg.data
        self.get_logger().info(f'Input: {frame_id}')
        try:
            transform = self.tf_buffer.lookup_transform(
                'map', 
                f"rfid_{frame_id}",
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
        self.goal_pose_publisher.publish(output_msg)

def main(args=None):
    try:
        rclpy.init(args=args)
        node = rfid_handler_node_class()
        rclpy.spin(node)
        rclpy.shutdown()
    except:
        pass
    print(f"poses: {node.best_pose}")
    with open(PKL_PATH, 'wb') as f:
        pickle.dump(node.best_pose, f)
    
if __name__ == '__main__':
    main()