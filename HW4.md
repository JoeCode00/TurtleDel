# HW4 Workflow
Connect to turtlebot-hub-5g

Run each command in a new Ubuntu terminal (if needed password turtlebot4)
If at any point the center light goes red, the create 3 or pi is reporting an error. Read the diagnostics at
```bash
ros2 topic echo /diagnostics_agg --once
```

0) Time sync
```bash
ssh ubuntu@192.168.1.3 "sudo date -s '$(date -u "+%Y-%m-%d %H:%M:%S")' && sudo systemctl restart chrony"
```

1) To start reading rfid tags, run the rfid launcher
```bash
ssh ubuntu@192.168.1.3 'source /opt/ros/humble/setup.bash && cd ~/TurtleDel && source install/setup.bash && ros2 launch rfid rfid.launch.py'
```

2) Undock the robot
```bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock {}
```

3) Listen for /scan /odom once, you may need to nudge the bot to get /odom
```bash
ros2 topic echo /scan --once && ros2 topic echo /odom --once
```

4) Start the /scan masking node
```bash
ros2 launch scan_mask scan_mask.launch.py
```

5) Listen to /rfid continuous
```bash
ros2 topic echo /rfid
```

Move a tag near the bot to see the ID

6) Lauch teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Move the robot with i, j, k , l

7) Start Rviz
```bash
ros2 launch turtlebot4_viz view_robot.launch.py
```

8) Start SLAM
```bash
ros2 launch turtlebot4_navigation slam.launch.py
```

9) Go back to the teleop shell and move the bot, show Rviz map

10) Save the map
```bash
ros2 run nav2_map_server map_saver_cli -f ~/hw4_map
```

11) Drive back toward the dock and dock the robot
```bash
ros2 action send_goal /dock irobot_create_msgs/action/Dock {}
```