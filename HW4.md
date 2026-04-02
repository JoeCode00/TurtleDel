# HW4 Workflow
Connect to turtlebot-hub-5g

Run each command in a new Ubuntu terminal (if needed password turtlebot4)
If at any point the center light goes red, the create 3 or pi is reporting an error. Read the diagnostics at
```bash
ros2 topic echo /diagnostics_agg --once
```

If that doesnt show much, try
```bash
ssh ubuntu@192.168.1.3 "sudo systemctl restart turtlebot4.service"
```

If the camera crashes, run
```bash
ssh ubuntu@192.168.1.3 "source /opt/ros/humble/setup.bash && ros2 service call /oakd/start_camera std_srvs/srv/Trigger {}"
```

0) Time sync
```bash
ssh ubuntu@192.168.1.3 "sudo date -s '$(date -u "+%Y-%m-%d %H:%M:%S")' && sudo systemctl restart chrony"
```

1) Undock the robot
```bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock {}
```

2) Listen for /scan /odom once, you may need to nudge the bot to get /odom. Repeat this command until /odom is published.
```bash
ros2 topic echo /scan --once && ros2 topic echo /odom --once
```

3) Start the /scan masking node
```bash
ros2 launch scan_mask scan_mask.launch.py
```

4) To start reading rfid tags, run the rfid launcher
```bash
ssh ubuntu@192.168.1.3 'source /opt/ros/humble/setup.bash && cd ~/TurtleDel && source install/setup.bash && ros2 launch rfid rfid.launch.py'
```

5) Listen to /rfid continuous
```bash
ros2 topic echo /rfid
```

Move a tag near the bot to see the ID

6) Oakd camera watch
```bash
ros2 run rqt_image_view rqt_image_view /oakd/rgb/preview/image_raw
```

7) Lauch teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Move the robot with i, j, k , l

8) Start Rviz
```bash
ros2 launch turtlebot4_viz view_robot.launch.py
```

9) Start SLAM
```bash
ros2 launch turtlebot4_navigation slam.launch.py
```

10) Go back to the teleop shell and move the bot, show Rviz map

11) Save the map
```bash
ros2 run nav2_map_server map_saver_cli -f ~/hw4_map
```

12) Drive back toward the dock and dock the robot
```bash
ros2 action send_goal /dock irobot_create_msgs/action/Dock {}
```

13) Localize on saved map 
```bash
ros2 launch turtlebot4_navigation localization.launch.py map:=$HOME/hw4_map.yaml
```

Use 2d pose estimate to initially place the robot.