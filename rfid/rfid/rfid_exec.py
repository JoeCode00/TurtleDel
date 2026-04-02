#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String as output_message_subclass 

import time
import serial

node_name = 'rfid_node'
output_msg_type = output_message_subclass

relative_output_topic = 'output'

qos = 10

class rfid_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        try:
            super().__init__(node_name)
            self.get_logger().info(f'init {node_name}')
            
            self.ser = serial.Serial(
                port='/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0',
                baudrate=38400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0  # Read timeout in seconds
            )
            
            # self.declare_parameter('basic_param', 'basic_default') # declare parameters with default values, if any

            # self.basic_param = str(self.get_parameter('basic_param').value)
            
            self.node_publisher_ = self.create_publisher(
                msg_type = output_msg_type, 
                topic = relative_output_topic,
                qos_profile = qos
                )
            
            output_msg = output_msg_type()

            self.ser.write(bytes([0x0A, 0x4E, 0x31, 0x2C, 0x31, 0x41, 0x0D])) # Max gain
            while True:
                time.sleep(0.05)
                self.ser.write(bytes([0x0A, 0x55, 0x30, 0x2C, 0x52, 0x31, 0x2C, 0x30, 0x2C, 0x31, 0x0D])) # Asks if any tags can be read

                data = self.ser.readall()
                data.replace(b'\r\r', b'').replace(b'\n\n', b'')
                cleaned = data.replace(b'\nU\r\n', b'').replace(b'\nX\r\n', b'')
                if cleaned in [b'', b'\r', b'\n', b'U', b'X', b'\r\n', b'\nU', b'\nX', b'U\r\n', b'X\r\n', b'X\r', b'U\r', b'\nU\r', b'\nX\r']:
                    continue
                data_packet = cleaned.split(b',')
                if len(data_packet) != 2:
                    continue

                if len(data_packet[0]) != 34 or len(data_packet[1]) != 7:
                    continue

                u_response = data_packet[0].split(b'E')
                marker_uid = u_response[1].decode('utf-8')
                output_msg.data = str(marker_uid)
                self.node_publisher_.publish(output_msg)
                self.get_logger().info(f'Output: {str(output_msg)}')
        except Exception as e:
            self.get_logger().info(f'Error: {str(e)}')
            # raise e
def main(args=None):
    rclpy.init(args=args)
    while True:
        try:
            node = rfid_node_class()
            rclpy.spin(node)
        except KeyboardInterrupt:
            break
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
