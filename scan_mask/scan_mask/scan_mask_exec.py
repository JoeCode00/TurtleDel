#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan as message_subclass 

import time
import math
import numpy as np

node_name = 'scan_mask_node'
input_msg_type = message_subclass
output_msg_type = message_subclass

relative_input_topic = 'input'
relative_output_topic = 'output'

qos = 10

class scan_mask_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self._last_stamp_ns = None  # tracks last published timestamp for monotonicity enforcement
        self.get_logger().info(f'init {node_name}')
        
        self.declare_parameter('mask_angle_mid_deg', 90) # declare parameters with default values, if any
        self.declare_parameter('mask_angle_width_deg', 20)
        self.declare_parameter('mask_min_range_m', 0.2)
        self.declare_parameter('mask_max_range_m', 1)
        self.declare_parameter('range_inf_to_range_0', True)
        self.declare_parameter('intensity_0_to_range_0', True)
        
        self.mask_angle_mid_deg = self.get_parameter('mask_angle_mid_deg').value
        self.mask_angle_width_deg = self.get_parameter('mask_angle_width_deg').value
        self.mask_min_range_m = self.get_parameter('mask_min_range_m').value
        self.mask_max_range_m = self.get_parameter('mask_max_range_m').value
        self.range_inf_to_range_0 = self.get_parameter('range_inf_to_range_0').value
        self.intensity_0_to_range_0 = self.get_parameter('intensity_0_to_range_0').value

        self.mask_angle_min_deg = self.mask_angle_mid_deg - self.mask_angle_width_deg / 2
        self.mask_angle_max_deg = self.mask_angle_mid_deg + self.mask_angle_width_deg / 2
        self.mask_angle_min_rad = np.deg2rad(self.mask_angle_min_deg)
        self.mask_angle_max_rad = np.deg2rad(self.mask_angle_max_deg)

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
        output_msg = output_msg_type()

        output_msg.header.frame_id = input_msg.header.frame_id

        # Enforce strictly monotonic timestamps. The Pi's clock has microsecond-level
        # NTP jitter that causes consecutive scans to occasionally arrive with a slightly
        # reversed timestamp. Cartographer drops any scan where stamp[n] <= stamp[n-1].
        stamp_ns = input_msg.header.stamp.sec * 1_000_000_000 + input_msg.header.stamp.nanosec
        if self._last_stamp_ns is not None and stamp_ns <= self._last_stamp_ns:
            stamp_ns = self._last_stamp_ns + 1  # advance by 1 ns to satisfy strict ordering
        self._last_stamp_ns = stamp_ns
        output_msg.header.stamp.sec = stamp_ns // 1_000_000_000
        output_msg.header.stamp.nanosec = stamp_ns % 1_000_000_000

        output_msg.angle_min = input_msg.angle_min
        output_msg.angle_max = input_msg.angle_max
        output_msg.angle_increment = input_msg.angle_increment

        output_msg.time_increment = input_msg.time_increment
        output_msg.scan_time = input_msg.scan_time

        num_points = len(input_msg.ranges)
        angles = list(np.linspace(input_msg.angle_min, input_msg.angle_max, num_points))

        ranges = list(input_msg.ranges)
        intensities = list(input_msg.intensities)

        for index, (angle, r, intensity) in enumerate(zip(angles, ranges, intensities)):
            # Hard mask: robot body blocks these angles, or reading is noise
            if self.mask_angle_min_rad < angle < self.mask_angle_max_rad:
                ranges[index] = 0.0
                intensities[index] = 0.0
                
            # No-return readings (0 or inf): replace with range_max so SLAM
            # raytraces free space instead of ignoring the ray entirely
            elif r == 0.0 or math.isinf(r) or math.isnan(r):
                ranges[index] = float('inf') # Changing this to let SLAM handle the raytracing distance
           
            # Too-close noise
            elif r < self.mask_min_range_m:
                ranges[index] = 0.0
                intensities[index] = 0.0
            
            # Too-far readings: treat as no-return so SLAM raytraces free space
            elif r > self.mask_max_range_m:
                ranges[index] = float('inf') # changing this to inf to treat as free space
            # Valid readings: pass through unchanged

        output_msg.ranges = ranges

        output_msg.range_min = float(self.mask_min_range_m)
        output_msg.range_max = float(input_msg.range_max)

        output_msg.intensities = intensities
    
        self.node_publisher_.publish(output_msg)

def main(args=None):
    rclpy.init(args=args)
    node = scan_mask_node_class()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()