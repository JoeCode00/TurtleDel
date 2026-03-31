# TurtleDel
## TurtleBot 4 Lite
All packages should be written first in Python, then optimizied if really necessary in C++.

All parameters and topic names (input and outputs) should be specified in the launch file. This is opposed to storing parameters inside the node, .env file, or passing setup info from a topic.

## Sensors
https://turtlebot.github.io/turtlebot4-user-manual/software/sensors.html
/scan topic contains
header	
std_msgs/Header	Includes a stamp (acquisition time of the first ray) and frame_id (usually "laser").
angle_min	float32	Start angle of the scan in radians (typically -π for 360° scans).
angle_max	float32	End angle of the scan in radians (typically π for 360° scans).
angle_increment	float32	Angular distance between each measurement in radians.
time_increment	float32	Time between individual measurements in seconds.
scan_time	float32	Total time between the start of one scan and the next.
range_min	float32	Minimum reliable detection distance in meters (e.g., 0.15m).
range_max	float32	Maximum detection distance in meters (varies by model, e.g., 12m–25m).
ranges	float32[]	Array of distance measurements in meters. Values outside range_min and range_max should be discarded.
intensities	float32[]	Array of device-specific intensity values (often empty if not supported).

## Robot Connection
<!-- 
## WIFI hosted by Turtlebot
In ubuntu connect to Turtlebot4 with password Turtlebot4

On the Ubuntu PC, run:
```
ssh ubuntu@10.42.0.1
```

If prompted, answer yes
SSH password is turtlebot4

Turtlebot-specific settings can be changed in turtlebot4-setup, including setting wifi from Access Point to Client (dangerous, could lock us out!)

Now you can run the following command to get onto the Turtlebot4:
```
nmcli connection up id "Turtlebot4" && ssh ubuntu@10.42.0.1
```

SSH password is turtlebot4
Exit the ssh py pressing ctrl+D. 
-->
## Pi setup


The turtlebot is configured to connect to the Netgear router on turtlebot-hub-5G.
Plug in the router.
Connect Ubuntu to turtlebot-hub-5G, the password is **turtlebot4**.
Turn on the turtlebot by placing it on the charger.
Wait 30 seconds and then attempt to SSH into the pi at

```bash
ssh ubuntu@192.168.1.3
```
If the connection does not work, the IP may have changed. Connected to turtlebot-hub-5G, go to http://192.168.1.1 and input the following:
Username: **admin**
Password: **turtlebot4PW!**
(Answers to security questions are also turtlebot4PW!)
Go to Attached Devices and look for UBUNTU.

If the router got reset, the Pi will continue to blindly look for turtlebot-hub-5G and the Create 3 will blindly look for turtlebot-hub both with password turtlebot4. Configure the router to these SSID and password to recover their IPs then reserve those IPs.

In the rest of this document, I assume that the IP of the Pi will be 192.168.1.3 and the IP of the Create 3 will be 192.168.1.4, as it is reserved in the router.

to SSH into the Pi, use
```bash
ssh ubuntu@192.168.1.3
```
the password is turtlebot4

To use the Create 3 web portal, on the Ubuntu PC use a browser to go to 
```
192.168.1.3:8080
```

### Pi time sync setup (one-time)
Add the PC as the preferred NTP source on the Pi:
```bash
ssh ubuntu@192.168.1.3
```
```bash
sudo sed -i 's/^pool ntp.ubuntu.com.*/server 192.168.1.2 iburst prefer\n&/' /etc/chrony/chrony.conf
sudo systemctl restart chrony
```
Exit SSH with ctrl+D.

If there are timestamp errors (e.g. slam_toolbox dropping /scan messages), check Pi sync:
```bash
ssh ubuntu@192.168.1.3 'chronyc sources'
```
You should see `^* 192.168.1.2` with a non-zero Reach value.

If needed, force a manual time set on the Pi:
```bash
ssh ubuntu@192.168.1.3 "sudo date -s '$(date -u "+%Y-%m-%d %H:%M:%S")'"
ssh ubuntu@192.168.1.3 'sudo systemctl restart chrony'
```

### Create 3 time sync setup (one-time)
On the Ubuntu PC web browser go to
```bash
http://192.168.1.3:8080/beta-ntp-conf
```

At the top of the document, add 
```
server 192.168.1.2 iburst prefer
```
Save the file using the button.

In the top banner, hover "Beta Features", then click "Restart ntpd".

This will allow timestamped topics to be published.

## Time sync
The Pi has no internet access and no RTC battery, so it loses its clock on reboot. The PC (192.168.1.2) acts as an NTP server using chrony, and the Pi syncs from it on boot.

This is already configured. The Pi will sync within ~10 seconds of booting as long as the PC is on first.


## PC Packages
```bash
sudo apt update && sudo apt install ros-humble-turtlebot4-desktop -y
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-turtlebot4-msgs -y
sudo apt install ros-humble-teleop-twist-keyboard -y
sudo apt-get install ros-humble-turtlebot4-viz -y
sudo apt-get install ros-humble-turtlebot4-navigation -y
sudo apt install -y chrony
sudo apt install -y ros-humble-teleop-twist-keyboard
sudo systemctl disable --now systemd-timesyncd
```



### PC chrony setup (one-time)
Allow the local subnet to query the PC:
```bash
echo 'allow 192.168.1.0/24' | sudo tee -a /etc/chrony/chrony.conf
sudo systemctl restart chrony
```

If ufw is enabled, allow NTP replies:
```bash
sudo ufw allow 123/udp
sudo ufw reload
```

Verify the PC is serving:
```bash
sudo chronyc clients
```
You should see 192.168.1.3 in the list.

## Simple discovery server setup
On the Ubuntu PC, run:
```bash
sudo apt update
sudo apt install -y ros-humble-rmw-cyclonedds-cpp
sudo mkdir /etc/turtlebot4/
sudo touch /etc/turtlebot4/setup.bash
sudo nano /etc/turtlebot4/setup.bash
```

add the following lines
```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=/etc/turtlebot4/cyclonedds_pc.xml
```

save and exit the file (ctrl+s, ctrl+x)
On the Ubuntu PC, run:
```bash
wget https://raw.githubusercontent.com/turtlebot/turtlebot4_setup/galactic/conf/cyclonedds_pc.xml && sudo mv cyclonedds_pc.xml /etc/turtlebot4/
source /etc/turtlebot4/setup.bash
source /opt/ros/humble/setup.bash
```



### Discovery server test:
On the TurtleBot4, run:
```bash
ros2 topic list
```
You should see something like:
/battery_state
/cmd_vel
...
/tf_static
/wheel_status

Exit the ssh via ctrl+D.
On the Ubuntu PC, run:
```bash
source /etc/turtlebot4/setup.bash
ros2 topic list
```

You should see the exact same list.

## Simple TeleOp
The robot will not respond to /cmd_vel if it thinks it is docked.
Check the docked status with the value of is_docked in:
```bash
ros2 topic echo /dock_status --once
```

Undock the robot. It will back up and rotate CW 180 degrees.
```bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock {}
```

Run the keyboard teleoperation node. Be careful, there is a >1 second motion delay.
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

If it is not responding to this, try directly publishing to /cmd_vel:
```bash
ros2 topic pub --rate 15 --qos-reliability best_effort /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 2.0}}"
```

Dock the robot
```bash
ros2 action send_goal /dock irobot_create_msgs/action/Dock {}
```

## Scan
The relevant parts of https://turtlebot.github.io/turtlebot4-user-manual/software/sensors.html#rplidar-a1m8

Check if the PC can hear /scan.
```bash
ros2 topic echo /scan
```

If /scan does not have data within 5 seconds, run:
```bash
ros2 topic info /scan
```

If there are no publishers, check if the node /rplidar_composition is listed.
```bash
ros2 topic list
```

If /rplidar_composition is not listed, SSH into the Pi and launch the rplidar.
```bash
ssh ubuntu@192.168.1.3
```
the password is turtlebot4
```bash
ros2 launch turtlebot4_bringup rplidar.launch.py
```
Exit SSH with ctrl+D.
Retstart this section to check if the PC can see /scan

## SLAM Mapping
Relevant sections of https://turtlebot.github.io/turtlebot4-user-manual/tutorials/generate_map.html#generating-a-map

Make sure that the PC can see /odom (may take up to a minute to get data)
```bash
ros2 topic echo /odom
```
If there is no data or topic, go back to the section on Create 3 time setup, as there may be a desync.

On the Ubuntu PC, Create /map via slam.launch.py that subscribes to /scan
```bash
ros2 launch turtlebot4_navigation slam.launch.py
```

Visualize /map via rviz
```bash
ros2 launch turtlebot4_viz view_robot.launch.py
```

## Saving the Map
Once you are happy with your map, you can save it with the following command:
```bash
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name:
  {data: 'map_name'}}"
```
**Note:**  
If you are using namespacing, you will need to call the map saver tool directly:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/src/TurtleDel/map_name
```
or generally
```bash
ros2 run nav2_map_server map_saver_cli -f "map_name" --ros-args -p map_subscribe_transient_local:=true -r __ns:=/namespace
```
**What gets generated?**  
The command creates two files in your current directory:
- `"map_name".pgm`: The actual image of the map (Occupancy Grid), which can be viewed in an image editor. Black = Obstacles, White = Free Space, Gray = Unknown.
- `"map_name".yaml`: The metadata containing the resolution (m/pixel) and origin. You can edit this file to adjust the map parameters

**Troubleshooting**  
- If the map is not saving, ensure that the ```bash /slam_toolbox/save_map ``` service is active by running ```bash ros2 service list ```

- If your map is empty, check if you have sourced your ROS 2 environment ( ```bash source /opt/ros/humble/setup.bash ```).

**Reusing for Navigation**  
- To use this map again later for navigation, you will pass the path of the YAML file to the Nav2 map server, typically by adding `map:=$HOME/my_new_map.yaml` as an argument when starting your TurtleBot4's navigation launch file.

## Using Your Saved Map
**1. Close your SLAM Terminals**    
- You cannot run the SLAM node and the Navigation/Localization nodes at the same time on the same map topic. Make sure to kill the `slam.launch.py` process first.
**2. Launch Navigation with your Map**
    
- Open a terminal and run the navigation launch file with the `turtlebot4_navigation` package. You must pass the **absolute path** to your `.yaml` file.
```bash
ros2 launch turtlebot4_navigation nav_stack.launch.py map:=$HOME/your_map_name.yaml
```
- Note: The exact launch file name might be `nav2.launch.py` depending on your specific workspace setup, but `nav_stack` is standard for the TurtleBot4.
**3. Launch the Visualization**
    
- On your workstation, bring up Rviz so you can see the robot on the static map:
```bash
ros2 launch turtlebot4_viz view_navigation.launch.py
```
**4. 2D Pose Estimate**  

- When the map loads, the TB will likely be "lost" -> its internal coordinate system may not line up with the static map yet
  - In Rviz2, click the **2D Pose Estimate** button at the top
  - Click and drag on the map at the robot's **actual physical location** to tell it which way it's facing
  - You'll see a cloud of green arrows (the particle filter) appear around the robot
**5. Localize the Robot**
      
- Drive the robot around manually for a few seconds. This allows the sensors to match the laser scans to the walls on your saved `.pgm` image.
- Once all the green arrows collapse into a tight cluster, the robot is localized
**6. Send a Navigation Goal**
  
- Now you can use the Nav2 Goal button in Rviz. Click anywhere on the map, and the robot will calculate a path and drive their autonomously. 
  
