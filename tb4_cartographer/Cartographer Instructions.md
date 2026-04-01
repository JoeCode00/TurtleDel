# Using Google Cartographer on Turtlebot 4 Lite

The Turtlebot 4 Lite runs on ROS 2 (typically Humble or Galactic). By default, it uses `slam_toolbox` for mapping. To use Google Cartographer instead, follow these steps:

---

## 1. Install Cartographer for ROS 2

1. **Open an SSH session** to the robot, or run locally on your PC if you are running SLAM there.
2. **Install the required binaries:**

   ```bash
   sudo apt update
   sudo apt install ros-humble-cartographer ros-humble-cartographer-ros
   ```

3. **(Optional) Install map saver tool if not already present:**

   ```bash
   sudo apt install ros-humble-nav2-map-server
   ```

---

## 2. Build and Source the Workspace Overlay

If `ros2 launch tb4_cartographer cartographer.launch.py` says package not found, your overlay is not sourced (or the package was not built yet).

1. From your workspace root (example: `~/TurtleDel`), build the package:

   ```bash
   cd ~/TurtleDel
   source /opt/ros/humble/setup.bash
   colcon build --packages-select tb4_cartographer
   ```

2. Source both ROS and your workspace overlay in every new terminal:

   ```bash
   source /opt/ros/humble/setup.bash
   source ~/TurtleDel/install/setup.bash
   ```

3. Verify ROS can see the package:

   ```bash
   ros2 pkg prefix tb4_cartographer
   ```

   Expected output should be similar to:

   ```text
   /home/<user>/TurtleDel/install/tb4_cartographer
   ```

---

## 3. Running Cartographer

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
   ros2 run nav2_map_server map_saver_cli -f ~/src/TurtleDel/map_name
   ```

---

## 4. Quick Troubleshooting

- If package is not found, run:

   ```bash
   source /opt/ros/humble/setup.bash
   source ~/TurtleDel/install/setup.bash
   ros2 pkg list | grep -x tb4_cartographer
   ```

- If that prints nothing, rebuild:

   ```bash
   cd ~/TurtleDel
   source /opt/ros/humble/setup.bash
   colcon build --packages-select tb4_cartographer
   source ~/TurtleDel/install/setup.bash
   ```