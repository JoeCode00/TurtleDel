-- Include map builder and trajectory builder configurations
include "map_builder.lua"
include "trajectory_builder.lua"

-- Options table containing configuration parameters
options = {
  map_builder = MAP_BUILDER,  -- Reference to the map builder configuration
  trajectory_builder = TRAJECTORY_BUILDER,  -- Reference to the trajectory builder configuration
  map_frame = "map",  -- Frame ID for the map
  tracking_frame = "base_link",  -- Frame ID for the robot base to track
  published_frame = "odom",  -- Frame ID for publishing poses
  odom_frame = "odom",  -- Frame ID for odometry data
  provide_odom_frame = false,  -- Whether to provide an odometry frame
  publish_frame_projected_to_2d = true,  -- Whether to project the published frame to 2D
  use_odometry = true,  -- Whether to use odometry data
  use_nav_sat = false,  -- Whether to use GPS data
  use_landmarks = false,  -- Whether to use landmarks for localization
  num_laser_scans = 1,  -- Number of single echo laser scans
  num_multi_echo_laser_scans = 0,  -- Number of multi-echo laser scans
  num_subdivisions_per_laser_scan = 1,  -- Number of subdivisions per laser scan
  num_point_clouds = 0,  -- Number of point clouds
  lookup_transform_timeout_sec = 0.2,  -- Timeout for looking up transforms (in seconds)
  submap_publish_period_sec = 0.3,  -- Period for publishing submaps (in seconds)
  pose_publish_period_sec = 5e-3,  -- Period for publishing poses (in seconds)
  trajectory_publish_period_sec = 30e-3,  -- Period for publishing trajectories (in seconds)
  rangefinder_sampling_ratio = 1.,  -- Sampling ratio for rangefinder data
  odometry_sampling_ratio = 1.,  -- Sampling ratio for odometry data
  fixed_frame_pose_sampling_ratio = 1.,  -- Sampling ratio for fixed frame poses
  imu_sampling_ratio = 1.,  -- Sampling ratio for IMU data
  landmarks_sampling_ratio = 1.,  -- Sampling ratio for landmarks
}

-- Enable 2D trajectory builder in the map builder
MAP_BUILDER.use_trajectory_builder_2d = true

-- Configure 2D trajectory builder parameters
TRAJECTORY_BUILDER_2D.min_range = 0.12  -- Minimum range for the rangefinder (in meters)
TRAJECTORY_BUILDER_2D.max_range = 8.0  -- Maximum range for the rangefinder (in meters)
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 8.5  -- Length of rays for missing data (in meters)
TRAJECTORY_BUILDER_2D.use_imu_data = true  -- Whether to use IMU data
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true  -- Enable online correlative scan matching
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.linear_search_window = 0.1  -- Linear search window for scan matching (in meters)
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.translation_delta_cost_weight = 10.  -- Weight for translation delta cost
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.rotation_delta_cost_weight = 1e-1  -- Weight for rotation delta cost

return options