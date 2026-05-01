# Turtle Delivery - Application Overview

A manufacturing and test site for high-assurance RF avionics equipment is used an example usecase for our system. In this example, products follow pipelines of fabrication, assembly, and test carried out in distinct cells distributed across a large campus. Because some cells can be a 15‑minute walk apart and each process step has variable duration and overlaps with other pipelines, the campus forms a non-trivial web of delivery routes.

This repo simulates a single instance of a larger fleet of delivery robots that are assigned routes on demand to move parts and assemblies between cells. Robots can accept deliveries in either direction to advance units through the pipeline or return units for rework based on test results. Using delivery robots reduces technician travel, shortens turnaround time, and increases throughput and operational efficiency.

## LRA9100 Example

Our implementation of this repo simulates an example pipeline for the LRA9100, a low-range altimeter product. The implementation demonstrates custom robot delivery routing between cells representing different stages in the unit pipeline.

### Pipeline Cell Mapping

- Cell0 — Robot Docking  
  Docking, charging, and robot staging.

- Cell1 — Fabrication  
  DSP PCBs are fabricated.

- Cell2 — Software Load & Verification  
  DSP PCBs are flashed with firmware and validated.

- Cell3 — Assembly & Test  
  DSP PCB is mechanically integrated with the control PCB to form the LRA9100; the completed unit undergoes final functional testing.

- Cell4 — Packing & Shipping  
  Units that pass final test are packaged and prepared for shipment.

- Cell5 — Rework  
  Units that fail testing are sent here for troubleshooting and corrective work.

---

## Architecture Overview

The TurtleDel system is built on **ROS 2** (Robot Operating System 2) and runs on a **TurtleBot 4 Lite** mobile robot platform. The architecture is modular, with specialized packages handling different aspects of the delivery system.

### Hardware Platform

- **Robot Base**: TurtleBot 4 Lite with Create 3 differential drive platform
- **Primary Sensor**: 2D LIDAR for mapping, localization, and obstacle detection
- **Communication**: Ethernet over Netgear router (turtlebot-hub-5G)

### ROS 2 System Architecture

The system uses a publisher-subscriber model with the following key components:

#### Core Navigation & Mapping
- **SLAM Toolbox (tb4_cartographer)**: SLAM (Simultaneous Localization and Mapping) for real-time map generation and robot localization
- **Nav2**: Navigation framework for autonomous path planning and control
- **TF2**: Transform framework for managing coordinate systems (base_link, odom, map)

#### Delivery & Waypoint Management
- **RFID (rfid)**: RFID reader integration for identifying delivery cells and tracking packages
- **RFID Waypoint Manager (rfid_waypoint_mgr)**: Manages delivery waypoints and routes between pipeline cells
- **Frontier Explorer (frontier_explorer)**: Autonomous exploration using frontier-based exploration for unknown environments

#### Sensor Processing & Safety
- **Scan Mask (scan_mask)**: Filters LIDAR scan data to mask unreliable or irrelevant regions for safer navigation

#### User Interface & Monitoring
- **TurtleDel UI (turtledel_ui)**: DearPyGui-based graphical interface for system monitoring and control
- **TurtleBot Monitor (turtlebot_monitor)**: Real-time monitoring of robot diagnostics and sensor status

### ROS 2 Communication Topics

Key topics include:
- `/scan` — LIDAR sensor data (LaserScan messages)
- `/cmd_vel` — Velocity commands for robot motion control (Twist messages)
- `/battery_state` — Battery voltage, charge percentage, and health status
- `/diagnostics` — System-wide diagnostics and health monitoring
- `/odom` — Odometry measurements from wheel encoders
- `/map` — Occupancy grid map from SLAM Toolbox
- `/tf`, `/tf_static` — Transform tree for coordinate frame relationships

### Deployment Model

All packages are written primarily in **Python** for rapid development and maintainability.

Configuration approach:
- All parameters and topic names are specified in **launch files** (not hardcoded in nodes)
- Centralized configuration in YAML files (`slam.yaml`, `nav2.yaml`, `localization.yaml`)
- Launch files coordinate multi-node orchestration and namespace management

### Development Environment

- **Build System**: Ament (ROS 2's build system)
- **Package Format**: Python-based packages using ament_python
- **Version Control**: Git repository at https://github.com/JoeCode00/TurtleDel

