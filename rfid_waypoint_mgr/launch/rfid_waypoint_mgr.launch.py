#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rfid_waypoint_mgr', #(1/7)
            executable='rfid_waypoint_mgr_exec', #(2/7)
            name='rfid_waypoint_mgr_node', #(3/7)
            namespace='',  #(4/7)
            parameters=[{}], #(5/7)
            remappings=[
                ('input', 'rfid_goal'), #(6/7) the world sees /rfid_goal -> this node sees /input
                ('output', 'goal_pose'), #(7/7) this node sees /output -> the world sees /goal_pose                
            ],
            output='screen' # or 'log' if the node should not output
        ),
        # Node(
        #     package='rfid_waypoint_mgr', #(1/7)
        #     executable='rfid_faker', #(2/7)
        #     name='rfid_faker_node', #(3/7)
        #     namespace='',  #(4/7)
        #     parameters=[{}], #(5/7)
        #     remappings=[], #(6/7) #(7/7)
        #     output='screen' # or 'log' if the node should not output
        # ),
        Node(
            package='rfid_waypoint_mgr', #(1/7)
            executable='rfid_joseph', #(2/7)
            name='rfid_joseph_node', #(3/7)
            namespace='',  #(4/7)
            parameters=[{}], #(5/7)
            remappings=[], #(6/7) #(7/7)
            output='screen' # or 'log' if the node should not output
        ),
    ])
