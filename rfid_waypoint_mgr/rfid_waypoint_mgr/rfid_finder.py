#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import tf2_ros
from std_msgs.msg import String
from geometry_msgs.msg import TransformStamped, PoseWithCovarianceStamped
import time

pose_translation_threshold = 0.005
pose_rotation_threshold = 0.005
rfid_min_signals = 10

class RFIDFinder(Node):
    def __init__(self):
        super().__init__("rfid_finder_node")
        self.get_logger().info('init rfid_finder_node')
        self.rfid_subscriber_ = self.create_subscription(String, "/rfid", self.rfid_callback, 10)
        self.pose_subscriber_ = self.create_subscription(PoseWithCovarianceStamped, "/pose", self.pose_callback, 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.create_timer(0.1, self.broadcast_poses)
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


    def broadcast_poses(self):
        for i, id in enumerate(self.best_pose.keys()):
            name = i
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

    def reset(self, pose_set):
        rfid_to_save = self.rfid_save if self.rfid_save else self.rfid_prev

        if rfid_to_save:
            ave = 100.0 # practically infinity
            if len(self.deltas_t) >= rfid_min_signals:
                self.deltas_t.pop() # remove last time delta so as not to skew the average
                ave = sum(self.deltas_t) / len(self.deltas_t)
        
            if self.rfid_save not in self.best_pose:
                self.best_pose[rfid_to_save] = {"time_period": ave, "pose": pose_set}
                print("\n\nNEW RFID")
                for k, v in self.best_pose.items():    
                    print(f"{k}:")    
                    if isinstance(v, dict):        
                        for ik, iv in v.items():            
                            print(f"  {ik}: {iv}")    
                    else:        
                        print(f"  {v}")
            else:
                if ave < self.best_pose[rfid_to_save]["time_period"]:
                    self.best_pose[rfid_to_save] = {"time_period": ave, "pose": pose_set}
                    print("\n\nBetter Pose found for RFID = " + str(rfid_to_save))
                    for k, v in self.best_pose.items():    
                        print(f"{k}:")    
                        if isinstance(v, dict):        
                            for ik, iv in v.items():            
                                print(f"  {ik}: {iv}")    
                        else:        
                            print(f"  {v}")
        
        self.x_set = pose_set.pose.pose.position.x
        self.y_set = pose_set.pose.pose.position.y
        self.w_set = pose_set.pose.pose.orientation.w
        self.x_prev = None
        self.y_prev = None
        self.z_prev = None
        self.rfid_save = None
        self.deltas_t = []
        self.reset_flag = False

    def pose_callback(self, msg):
        if self.x_prev is not None and self.y_prev is not None:
            x_diff = abs(msg.pose.pose.position.x) - abs(self.x_prev)
            y_diff = abs(msg.pose.pose.position.y) - abs(self.y_prev)
            w_diff = abs(msg.pose.pose.orientation.w) - abs(self.w_prev)

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

    def rfid_callback(self, msg):
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
    
def main(args=None):
    rclpy.init(args=args)
    node = RFIDFinder()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()