#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='scan_mask', #(1/7)
            executable='scan_mask_exec', #(2/7)
            name='scan_mask_node', #(3/7)
            namespace='',  #(4/7)
            parameters=[{
                'mask_angle_mid_deg': 90,
                'mask_angle_width_deg': 20,
                'mask_min_range_m': 0.075, # changing this to match the LIDAR blind spot
                'mask_max_range_m': 3, # increasing this bc 2m is way too close imo
                'range_inf_to_range_0': False, # changing this to match the logic from the slam.yaml file
                'intensity_0_to_range_0': False, #(5/7) # pretty sure if surface is too dark to reutn an intensity signal, we dont wanna mark it as a hit
						    #fill with dict of parameters
            }],
            remappings=[
                ('input', '/scan'), #(6/7) the world sees /scan -> this node sees /input
                ('output', '/scan_masked'), #(7/7) this node sees /output -> the world sees /scan_masked                
            ],
            output='screen' # or 'log' if the node should not output
        ),
    ])
