# Using Google Cartographer on Turtlebot 4 Lite

The Turtlebot 4 Lite runs on ROS 2 (typically Humble or Galactic). By default, it uses `slam_toolbox` for mapping. To use Google Cartographer instead, follow these steps:

---

## 1. Install Cartographer for ROS 2

1. **Open an SSH session** into your Turtlebot 4's Raspberry Pi (or run this on your local PC if running the SLAM node locally).
2. **Install the required binaries:**

   ```bash
   sudo apt update
   sudo apt install ros-humble-cartographer ros-humble-cartographer-ros
   ```

---

## 2. Running Cartographer

1. **Start the Robot:**
   Ensure your Turtlebot 4 is turned on and the standard background bringup is running (publishing TF, LIDAR `/scan`, and `/odom`).

2. **Launch Cartographer:**

   ```bash
   ros2 launch tb4_cartographer cartographer.launch.py
   ```

3. **Open RViz (on your PC):**

   ```bash
   ros2 run rviz2 rviz2
   ```
   - Add the `/map` topic, `/scan` topic, and TF to visualize the map being built.
   - Change the fixed frame to `map`.

4. **Drive the Robot:**
   Use the teleop node to drive the robot around your environment:

   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```

5. **Save the Map:**
   Once satisfied with the map, save it using the `nav2_map_server`:

   ```bash
   ros2 run nav2_map_server map_saver_cli -f ~/my_new_map
   ```