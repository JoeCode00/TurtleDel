#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rfid', #(1/7)
            executable='rfid_exec', #(2/7)
            name='rfid_node', #(3/7)
            namespace='',  #(4/7)
            parameters=[{
                # 'basic_param': 'basic_value', #(5/7)
						    #fill with dict of parameters
            }],
            remappings=[
                ('output', 'rfid'), #(7/7) this node sees /output -> the world sees /rfid                
            ],
            output='screen' # or 'log' if the node should not output
        ),
    ])
