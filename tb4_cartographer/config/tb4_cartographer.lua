-- Include map builder and trajectory builder configurations
include "map_builder.lua"
include "trajectory_builder.lua"

-- Options table containing configuration parameters
options = {
  map_builder = MAP_BUILDER,  -- Reference to the map builder configuration
  trajectory_builder = TRAJECTORY_BUILDER,  -- Reference to the trajectory builder configuration
  map_frame = "map",  -- Frame ID for the map
  tracking_frame = "base_link",  -- Frame ID for the robot base to track
  published_frame = "odom",  -- Frame Cartographer reads the TF chain from (odom→base_link→laser)
  odom_frame = "odom",  -- Frame ID for odometry data
  provide_odom_frame = false,  -- Whether to provide an odometry frame
  publish_frame_projected_to_2d = true,  -- Whether to project the published frame to 2D
  publish_to_tf = false,  -- Do NOT let Cartographer write map→odom to TF; the static publisher owns that
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
TRAJECTORY_BUILDER_2D.max_range = 2  -- Maximum range for the rangefinder (in meters)
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 8.5  -- Length of rays for missing data (in meters)
TRAJECTORY_BUILDER_2D.use_imu_data = false  -- Disable IMU requirement when IMU topic is unavailable

-- More definite map cells: default hit=0.55/miss=0.49 requires many passes to
-- commit a cell. Raising hit and lowering miss makes obstacles appear crisply
-- after fewer scans and free space clears faster.
TRAJECTORY_BUILDER_2D.submaps.range_data_inserter.probability_grid_range_data_inserter.hit_probability = 0.7
TRAJECTORY_BUILDER_2D.submaps.range_data_inserter.probability_grid_range_data_inserter.miss_probability = 0.35
-- Disable the correlative (brute-force window search) scan matcher.
-- This runs BEFORE ceres and can relocate the pose regardless of ceres weights.
-- With it off, LIDAR is used only to paint the map, not to correct position.
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = false

-- Odom-locked mode: ceres odom prior weights set to 1e9 (effectively infinite).
-- The occupied_space residual (LIDAR) weight is 1 by default, so odom wins by
-- a factor of 1,000,000,000. The pose will not deviate from odom at all.
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 1e9
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 1e9

-- Disable global pose graph optimization (loop closures) entirely.
-- map→odom transform is never updated; /odom is locked to the world origin.
POSE_GRAPH.optimize_every_n_nodes = 0

return options