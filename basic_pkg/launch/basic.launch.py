#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='basic_pkg', #(1/7)
            executable='basic_exec', #(2/7)
            name='basic_node', #(3/7)
            namespace='basic_ns',  #(4/7)
            parameters=[{
                'basic_param': 'basic_value', #(5/7)
						    #fill with dict of parameters
            }],
            remappings=[
                ('input', 'echo_input'), #(6/7) the world sees /basic_ns/echo_input -> this node sees /input
                ('output', 'echo_output'), #(7/7) this node sees /output -> the world sees /basic_ns/echo_output                
            ],
            output='screen' # or 'log' if the node should not output
        ),
    ])
