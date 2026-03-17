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
        Node(
            package='spiral_pattern', #(1/7)
            executable='spiral_node', #(2/7)
            name='spiral_draw', #(3/7)
            namespace='spiral_ns', #(4/7)
            parameters=[{
                'spiral_param': 'spiral_value', #(5/7)
            }],
            remappings=[
                ('spiral_input', 'spiral_echo_input'), #(6/7)
                ('spiral_output', 'spiral_echo_output'), #(7/7)
            ],
            output='screen'
        ),
        Node(
            package='turtlesim', #(1/7)
            executable='turtlesim_node', #(2/7)
            name='turtlesim', #(3/7)
            namespace='', #(4/7)
            output='screen' #(5/7)
        ),
    ])
