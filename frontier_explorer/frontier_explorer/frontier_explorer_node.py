#!/usr/bin/env python3

# Import necessary libraries for mathematical operations, data structures, and ROS2 functionality
import math
from collections import deque

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

# Import message and action types for navigation and geometry
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose

# Import TF2 libraries for handling transformations
from tf2_ros import Buffer, TransformListener, LookupException, ConnectivityException, ExtrapolationException

class FrontierExplorer(Node):
    """
    A ROS2 node for autonomous exploration using frontier-based exploration.
    This node subscribes to a map topic, detects frontiers, and sends navigation goals to explore unknown areas.
    """
    def __init__(self):
        super().__init__('frontier_explorer')

        # Declare and retrieve parameters for the node
        self.declare_parameter('map_topic', '/map')
        self.declare_parameter('goal_timeout_sec', 90.0)
        self.declare_parameter('min_frontier_size', 5)
        self.declare_parameter('planner_frame', 'map')
        self.declare_parameter('robot_frame', 'base_link')

        map_topic = self.get_parameter('map_topic').get_parameter_value().string_value
        self.goal_timeout_sec = self.get_parameter('goal_timeout_sec').get_parameter_value().double_value
        self.min_frontier_size = self.get_parameter('min_frontier_size').get_parameter_value().integer_value
        self.planner_frame = self.get_parameter('planner_frame').get_parameter_value().string_value
        self.robot_frame = self.get_parameter('robot_frame').get_parameter_value().string_value

        # Initialize variables for map data, goal handling, and exploration state
        self.map_msg = None
        self.current_goal_handle = None
        self.current_goal_sent_time = None
        self.exploring = False

        # Subscribe to the map topic to receive occupancy grid updates
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            map_topic,
            self.map_callback,
            10
        )

        # Create an action client for sending navigation goals
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Set up a TF2 buffer and listener for retrieving robot pose
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create a timer to periodically execute the exploration cycle
        self.timer = self.create_timer(3.0, self.explore_cycle)

        self.get_logger().info('Frontier explorer node started.')

    def map_callback(self, msg):
        """
        Callback function for the map subscription.
        Stores the received occupancy grid message for processing.
        """
        self.map_msg = msg

    def explore_cycle(self):
        """
        Main exploration cycle executed periodically by the timer.
        Detects frontiers and sends navigation goals to explore unknown areas.
        """
        if self.map_msg is None:
            self.get_logger().info('Waiting for map...')
            return

        if not self.nav_to_pose_client.wait_for_server(timeout_sec=0.5):
            self.get_logger().info('Waiting for Nav2 action server...')
            return

        if self.exploring:
            return

        # Get the current robot pose
        robot_pose = self.get_robot_pose()
        if robot_pose is None:
            self.get_logger().warn('Could not get robot pose.')
            return

        # Detect frontiers in the map
        frontiers = self.detect_frontiers(self.map_msg)
        if not frontiers:
            self.get_logger().info('No frontiers found. Exploration complete.')
            return

        # Select the best frontier goal and send it
        goal = self.select_frontier_goal(frontiers, robot_pose)
        if goal is None:
            self.get_logger().warn('No valid frontier goal selected.')
            return

        self.send_goal(goal)

    def get_robot_pose(self):
        """
        Retrieve the current robot pose using the TF2 buffer.
        Returns the (x, y) position of the robot or None if the pose cannot be determined.
        """
        try:
            transform = self.tf_buffer.lookup_transform(
                self.planner_frame,
                self.robot_frame,
                rclpy.time.Time()
            )
            x = transform.transform.translation.x
            y = transform.transform.translation.y
            return (x, y)
        except (LookupException, ConnectivityException, ExtrapolationException):
            return None

    def detect_frontiers(self, map_msg):
        """
        Detect frontiers in the occupancy grid map.
        A frontier is a boundary between known and unknown areas.
        Returns a list of clusters, where each cluster is a list of (x, y) cells.
        """
        width = map_msg.info.width
        height = map_msg.info.height
        data = list(map_msg.data)

        def idx(x, y):
            return y * width + x

        def in_bounds(x, y):
            return 0 <= x < width and 0 <= y < height

        def is_free(x, y):
            return data[idx(x, y)] == 0

        def is_unknown(x, y):
            return data[idx(x, y)] == -1

        frontier_cells = set()

        # Identify frontier cells by checking neighbors of free cells
        for y in range(height):
            for x in range(width):
                if not is_free(x, y):
                    continue
                for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                    if in_bounds(nx, ny) and is_unknown(nx, ny):
                        frontier_cells.add((x, y))
                        break

        visited = set()
        clusters = []

        # Group frontier cells into clusters using breadth-first search
        for cell in frontier_cells:
            if cell in visited:
                continue

            cluster = []
            q = deque([cell])
            visited.add(cell)

            while q:
                cx, cy = q.popleft()
                cluster.append((cx, cy))

                for nx, ny in [
                    (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1),
                    (cx+1, cy+1), (cx-1, cy-1), (cx+1, cy-1), (cx-1, cy+1)
                ]:
                    if (nx, ny) in frontier_cells and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        q.append((nx, ny))

            if len(cluster) >= self.min_frontier_size:
                clusters.append(cluster)

        return clusters

    def select_frontier_goal(self, frontiers, robot_pose):
        """
        Select the best frontier goal based on distance and cluster size.
        Returns the (x, y) position of the selected goal in world coordinates.
        """
        best_goal = None
        best_score = float('inf')

        for cluster in frontiers:
            wx, wy = self.cluster_centroid_to_world(cluster, self.map_msg)
            dist = math.hypot(wx - robot_pose[0], wy - robot_pose[1])

            # Score is based on distance and cluster size
            score = dist - 0.2 * len(cluster)

            if score < best_score:
                best_score = score
                best_goal = (wx, wy)

        return best_goal

    def cluster_centroid_to_world(self, cluster, map_msg):
        """
        Convert the centroid of a cluster from map coordinates to world coordinates.
        Returns the (x, y) position in world coordinates.
        """
        mx = sum(c[0] for c in cluster) / len(cluster)
        my = sum(c[1] for c in cluster) / len(cluster)

        origin_x = map_msg.info.origin.position.x
        origin_y = map_msg.info.origin.position.y
        resolution = map_msg.info.resolution

        wx = origin_x + (mx + 0.5) * resolution
        wy = origin_y + (my + 0.5) * resolution
        return wx, wy

    def send_goal(self, goal_xy):
        """
        Send a navigation goal to the Nav2 action server.
        """
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = self.planner_frame
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = goal_xy[0]
        goal_msg.pose.pose.position.y = goal_xy[1]
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.exploring = True
        self.get_logger().info(f'Sending goal to x={goal_xy[0]:.2f}, y={goal_xy[1]:.2f}')

        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        """
        Callback for receiving feedback from the navigation action server.
        Currently not implemented.
        """
        pass

    def goal_response_callback(self, future):
        """
        Callback for handling the response to a sent goal.
        Logs whether the goal was accepted or rejected.
        """
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected.')
            self.exploring = False
            return

        self.get_logger().info('Goal accepted.')
        self.current_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        """
        Callback for handling the result of a completed goal.
        Logs whether the goal succeeded or failed.
        """
        try:
            result = future.result()
            self.get_logger().info('Goal finished.')
        except Exception as e:
            self.get_logger().error(f'Goal failed: {e}')
        self.exploring = False

def main(args=None):
    """
    Main entry point for the FrontierExplorer node.
    Initializes the ROS2 system, creates the node, and starts spinning.
    """
    rclpy.init(args=args)
    node = FrontierExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()