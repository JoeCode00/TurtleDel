#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class RFIDFinder(Node):
    def __init__(self):
        super().__init__("rfid_finder_node")
        self.rfid_subscriber_ = self.create_subscription(String, "/rfid", self.rfid_callback, 10)   # Type, Topic, Callback, Buffer size
        self.rfid_publisher_ = self.create_publisher(String, "/rfid_dif", 10)
        # self.subscription
        self.dec_current = 0
        self.dec_previous = 0

    def rfid_callback(self, msg):
        rfid_ping = msg.data
        rfid_dec = int(rfid_ping, 16)
        if (rfid_dec != self.dec_current):
            self.dec_previous = self.dec_current
            self.dec_current = rfid_dec
            self.get_logger().info(str(self.dec_current))
            difference = self.dec_current - self.dec_previous
            if (difference < 0):
                self.get_logger().info("Closer! difference = " + str(difference))
            elif (difference > 0):
                self.get_logger().info("Further! difference = " + str(difference))

            msg.data = str(difference)
            self.rfid_publisher_.publish(msg)
        # else:
        #     self.get_logger().info("No difference")
    
def main(args=None):
    rclpy.init(args=args)
    node = RFIDFinder()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()