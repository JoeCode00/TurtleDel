# HW4 Workflow
Run each command in a new Ubuntu terminal (if needed password turtlebot4)


1) To start reading rfid tags, run the rfid launcher
```bash
ssh ubuntu@192.168.1.3 'source /opt/ros/humble/setup.bash && cd ~/TurtleDel && source install/setup.bash && ros2 launch rfid rfid.launch.py'
```