import serial
import time
# Configure the serial port
# Replace 'COM1' with your actual serial port (e.g., '/dev/ttyUSB0' on Linux)
# Set the baudrate to match your device's configuration
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=38400,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0  # Read timeout in seconds
)
# start_time = time.time()
# reads_in_second = 0
try:
    # Open the serial port
    try:
        ser.open()
    except Exception as e:
        False
    ser.write(bytes([0x0A, 0x4E, 0x31, 0x2C, 0x31, 0x41, 0x0D]))
    while True:
        time.sleep(0.05)
        ser.write(bytes([0x0A, 0x55, 0x30, 0x2C, 0x52, 0x31, 0x2C, 0x30, 0x2C, 0x31, 0x0D]))

        data = ser.readall()
        data.replace(b'\r\r', b'').replace(b'\n\n', b'')
        cleaned = data.replace(b'\nU\r\n', b'').replace(b'\nX\r\n', b'')
        if cleaned not in [b'', b'\r', b'\n', b'U', b'X', b'\r\n', b'\nU', b'\nX', b'U\r\n', b'X\r\n', b'X\r', b'U\r', b'\nU\r', b'\nX\r']:
            data_packet = cleaned.split(b',')
            if len(data_packet) == 2:
                if len(data_packet[0]) == 34 and len(data_packet[1]) == 7:
                    u_response = data_packet[0].split(b'E')
                    marker_uid = u_response[1].decode('utf-8')
                    # reads_in_second += 1
        
        # print(f"Reads in the last second: {reads_in_second}") 
        # if time.time() - start_time >= 1:
        #     reads_in_second = 0
        #     start_time = time.time()

except serial.SerialException as e:
    print(f"Error: {e}")

finally:
    # Close the serial port when done
    if ser.is_open:
        ser.close()
        print(f"Serial port {ser.port} closed.")