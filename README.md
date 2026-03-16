# TurtleDel
## TurtleBot 4 Lite
b

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

## PC Packages
```
sudo apt update && sudo apt install ros-humble-turtlebot4-desktop -y
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=0
sudo apt install ros-humble-teleop-twist-keyboard -y
sudo apt-get install ros-humble-turtlebot4-viz -y
sudo apt-get install ros-humble-turtlebot4-navigation -y
```
1-liner
```
sudo apt update && sudo apt install ros-humble-turtlebot4-desktop -y && source /opt/ros/humble/setup.bash && export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp && export ROS_DOMAIN_ID=0 && sudo apt install ros-humble-teleop-twist-keyboard -y && sudo apt-get install ros-humble-turtlebot4-viz -y && sudo apt-get install ros-humble-turtlebot4-navigation -y
```

## Simple discovery server setup
On the Ubuntu PC, run:
```
sudo apt update
sudo apt install -y ros-humble-rmw-cyclonedds-cpp
sudo mkdir /etc/turtlebot4/
sudo touch /etc/turtlebot4/setup.bash
sudo nano /etc/turtlebot4/setup.bash
```

add the following lines

source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=/etc/turtlebot4/cyclonedds_pc.xml

save and exit the file (ctrl+s, ctrl+x)
On the Ubuntu PC, run:
```
wget https://raw.githubusercontent.com/turtlebot/turtlebot4_setup/galactic/conf/cyclonedds_pc.xml && sudo mv cyclonedds_pc.xml /etc/turtlebot4/
source /etc/turtlebot4/setup.bash
source /opt/ros/humble/setup.bash
```
Connect to the TurtleBot4
```
nmcli connection up id "Turtlebot4" && ssh ubuntu@10.42.0.1
```
SSH password is turtlebot4
In a web browser, go to 10.42.0.1:8080
In the top bar, got to Application and then Configuration
If the "Enable Fast DDS discovery server?" box is checked, uncheck the box, press save, and restart the application.

Now we are in the robot, run:
```
turtlebot4-setup
```
ROS Setup (enter) -> Discovery Server (enter)
If Enabled is [True], set it as [False]
esc 3 times to exit to terminal.


### Discovery server test:
On the TurtleBot4, run:
```
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
```
source /etc/turtlebot4/setup.bash
ros2 topic list
```

You should see the exact same list.
