#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtledel_ui', #(1/7)
            executable='ui_exec_terminal', #(2/7)
            name='ui_node', #(3/7)
            namespace='',  #(4/7)
            parameters=[{
                'basic_param': 'basic_value', #(5/7)
						    #fill with dict of parameters
            }],
            remappings=[
                ('input', 'ui_input'), #(6/7) the world sees /ui_input -> this node sees /input
                ('output', 'ui_output'), #(7/7) this node sees /output -> the world sees /ui_output                
            ],
            output='screen' # or 'log' if the node should not output
        ),
    ])
