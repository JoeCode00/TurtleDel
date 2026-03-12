# TurtleDel
## TurtleBot 4 Lite
https://turtlebot.github.io/turtlebot4-user-manual/mechanical/turtlebot4_lite.html
All ROS2 packages will be built for Jazzy, as this is what the TurtleBot 4 lite uses. This runs best on Ubuntu 24.04.
docs.ros.org/en/humble/Releases/Release-Jazzy-Jalisco.html
https://ubuntu.com/download/desktop

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
