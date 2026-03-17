import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class SpiralDraw(Node):
    def __init__(self):
        super().__init__('spiral_draw') 
        self.vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.vel_bot_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.echo_pub = self.create_publisher(Twist, 'spiral_output', 10) # globally visible on /spiral_ns/spiral_echo_output
        self.vel = Twist()
        self.linear_velocity = 2.0 
        #^^ Only how fast circle is drawn, not how tight the spiral is. 
        # The tighter the spiral, the faster the angular velocity changes, but the linear velocity can stay constant.

        #Radius variables
        self.start_radius = 2.5
        self.end_radius = 0.5
        self.current_radius = self.start_radius

        #Theta Variables
        self.total_revolutions = 4.0
        self.max_angle = self.total_revolutions * 2 * math.pi #Radians for 4 revolutions
        self.current_angle = 0.0
        
        # Archimedes Spiral: r = a + b * theta
        # r is the radius at any angle theta, a is the starting radius, and b controls how tightly the spiral winds.
        # if b is negative, the spiral will wind inward, which is what we want
        # We calculate the decay rate (b) required to reach end_radius at max_angle
        # 0.5 = 2.5 + b * (8 * pi)  ->  b = (0.5 - 2.5) / (8 * pi)
        self.radius_decay_rate = (self.end_radius - self.start_radius) / self.max_angle
        
        # Create a timer with a publish rate
        self.timer_period = 0.1 # seconds
        self.timer = self.create_timer(self.timer_period, self.publish)

    def publish(self):
        # Check to see if spiral is complete
        if self.current_radius >= self.end_radius:
            #keep going in spiral
            # Set angular velocity based on the current radius
            angular_velocity = self.linear_velocity / self.current_radius
            
            # Publish velocities for turtlesim
            self.vel.linear.x = self.linear_velocity
            self.vel.angular.z = angular_velocity
            self.vel_pub.publish(self.vel)
            self.vel_bot_pub.publish(self.vel)
            # Echo the velocity values to the 'spiral_output' topic
            self.echo_pub.publish(self.vel)

            # theta new = theta old + angular_velocity * time
            self.current_angle += angular_velocity * self.timer_period
            # radius new = a + b * theta
            self.current_radius = self.start_radius + self.radius_decay_rate * self.current_angle

        else:
            #spiral is done
            # Stop the turtle once the spiral is complete
            self.vel.linear.x = 0.0
            self.vel.angular.z = 0.0
            self.vel_pub.publish(self.vel)
            self.vel_bot_pub.publish(self.vel)
            self.echo_pub.publish(self.vel)

def main(args=None):
    rclpy.init(args=args)
    node = SpiralDraw()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:#This gets rid of the ctrl+c error when you stop the node
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()