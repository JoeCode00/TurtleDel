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
                'mask_min_range_m': 0.2,
                'mask_max_range_m': 5,
                'range_inf_to_range_0': True,
                'intensity_0_to_range_0': True, #(5/7)
						    #fill with dict of parameters
            }],
            remappings=[
                ('input', '/scan'), #(6/7) the world sees /scan -> this node sees /input
                ('output', '/scan_masked'), #(7/7) this node sees /output -> the world sees /scan_masked                
            ],
            output='screen' # or 'log' if the node should not output
        ),
    ])
