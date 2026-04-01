# System File Changes

Backups are stored alongside originals with a `.bak` extension.

---

## `/opt/ros/humble/share/turtlebot4_navigation/launch/slam.launch.py`

**Backup:** `slam.launch.py.bak`

**Change:** Remapped `/scan` to `scan_masked` so SLAM toolbox subscribes to the masked scan topic instead of raw lidar.

```python
# Before
('/scan', 'scan'),

# After
('/scan', 'scan_masked'),
```

---

## `/opt/ros/humble/share/turtlebot4_navigation/config/slam.yaml`

**Backup:** `slam.yaml.bak`

**Changes:** Disabled scan matching and loop closure so the `map` → `odom` transform is never corrected. The odom frame is fully locked to the map origin; pose is driven entirely by wheel odometry.

```yaml
# Before
use_scan_matching: true
do_loop_closing: true

# After
use_scan_matching: false
do_loop_closing: false
```

---

## `/opt/ros/humble/share/turtlebot4_navigation/config/slam.yaml` (occupancy confidence)

**Backup:** `slam.yaml.bak` (same backup as above — original already captured)

**Changes:** Added `min_pass_through` and `occupancy_threshold` so cells require multiple scan ray passes before being classified, and a higher hit fraction to be marked occupied.

```yaml
# Added (turtlebot4 slam.yaml previously relied on slam_toolbox defaults)
min_pass_through: 5       # default 2 — require 5 ray passes before classifying a cell
occupancy_threshold: 0.25 # default 0.1 — require 25% hit ratio to mark a cell occupied
```
