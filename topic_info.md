# /battery_state
```
sensor_msgs/msg/BatteryState


# Constants are chosen to match the enums in the linux kernel
# defined in include/linux/power_supply.h as of version 3.7
# The one difference is for style reasons the constants are
# all uppercase not mixed case.

# Power supply status constants
uint8 POWER_SUPPLY_STATUS_UNKNOWN = 0
uint8 POWER_SUPPLY_STATUS_CHARGING = 1
uint8 POWER_SUPPLY_STATUS_DISCHARGING = 2
uint8 POWER_SUPPLY_STATUS_NOT_CHARGING = 3
uint8 POWER_SUPPLY_STATUS_FULL = 4

# Power supply health constants
uint8 POWER_SUPPLY_HEALTH_UNKNOWN = 0
uint8 POWER_SUPPLY_HEALTH_GOOD = 1
uint8 POWER_SUPPLY_HEALTH_OVERHEAT = 2
uint8 POWER_SUPPLY_HEALTH_DEAD = 3
uint8 POWER_SUPPLY_HEALTH_OVERVOLTAGE = 4
uint8 POWER_SUPPLY_HEALTH_UNSPEC_FAILURE = 5
uint8 POWER_SUPPLY_HEALTH_COLD = 6
uint8 POWER_SUPPLY_HEALTH_WATCHDOG_TIMER_EXPIRE = 7
uint8 POWER_SUPPLY_HEALTH_SAFETY_TIMER_EXPIRE = 8

# Power supply technology (chemistry) constants
uint8 POWER_SUPPLY_TECHNOLOGY_UNKNOWN = 0
uint8 POWER_SUPPLY_TECHNOLOGY_NIMH = 1
uint8 POWER_SUPPLY_TECHNOLOGY_LION = 2
uint8 POWER_SUPPLY_TECHNOLOGY_LIPO = 3
uint8 POWER_SUPPLY_TECHNOLOGY_LIFE = 4
uint8 POWER_SUPPLY_TECHNOLOGY_NICD = 5
uint8 POWER_SUPPLY_TECHNOLOGY_LIMN = 6

std_msgs/Header  header
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
float32 voltage          # Voltage in Volts (Mandatory)
float32 temperature      # Temperature in Degrees Celsius (If unmeasured NaN)
float32 current          # Negative when discharging (A)  (If unmeasured NaN)
float32 charge           # Current charge in Ah  (If unmeasured NaN)
float32 capacity         # Capacity in Ah (last full capacity)  (If unmeasured NaN)
float32 design_capacity  # Capacity in Ah (design capacity)  (If unmeasured NaN)
float32 percentage       # Charge percentage on 0 to 1 range  (If unmeasured NaN)
uint8   power_supply_status     # The charging status as reported. Values defined above
uint8   power_supply_health     # The battery health metric. Values defined above
uint8   power_supply_technology # The battery chemistry. Values defined above
bool    present          # True if the battery is present

float32[] cell_voltage   # An array of individual cell voltages for each cell in the pack
                         # If individual voltages unknown but number of cells known set each to NaN
float32[] cell_temperature # An array of individual cell temperatures for each cell in the pack
                           # If individual temperatures unknown but number of cells known set each to NaN
string location          # The location into which the battery is inserted. (slot number or plug)
string serial_number     # The best approximation of the battery serial number

```
------------------------------
# /cmd_vel
```
geometry_msgs/msg/Twist

# This expresses velocity in free space broken into its linear and angular parts.

Vector3  linear
        float64 x
        float64 y
        float64 z
Vector3  angular
        float64 x
        float64 y
        float64 z

```
------------------------------
# /diagnostics
```
diagnostic_msgs/msg/DiagnosticArray

# This message is used to send diagnostic information about the state of the robot.
std_msgs/Header header # for timestamp
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
DiagnosticStatus[] status # an array of components being reported on
        byte OK=0
        byte WARN=1
        byte ERROR=2
        byte STALE=3
        byte level
        string name
        string message
        string hardware_id
        KeyValue[] values
                string key
                string value

```
------------------------------
# /diagnostics_agg
```
diagnostic_msgs/msg/DiagnosticArray

# This message is used to send diagnostic information about the state of the robot.
std_msgs/Header header # for timestamp
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
DiagnosticStatus[] status # an array of components being reported on
        byte OK=0
        byte WARN=1
        byte ERROR=2
        byte STALE=3
        byte level
        string name
        string message
        string hardware_id
        KeyValue[] values
                string key
                string value

```
------------------------------
# /diagnostics_toplevel_state
```
diagnostic_msgs/msg/DiagnosticStatus

# This message holds the status of an individual component of the robot.

# Possible levels of operations.
byte OK=0
byte WARN=1
byte ERROR=2
byte STALE=3

# Level of operation enumerated above.
byte level
# A description of the test/component reporting.
string name
# A description of the status.
string message
# A hardware unique string.
string hardware_id
# An array of values associated with the status.
KeyValue[] values
        string key
        string value


```
------------------------------
# /dock_status
```
irobot_create_msgs/msg/DockStatus

# This message contains information about whether the robot is docked or sees the dock in its sensors.

std_msgs/Header header  # Header stamp is when dock info was queried.
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
bool dock_visible       # Whether robot sees dock in its sensors used for docking
bool is_docked          # Whether the robot is docked

```
------------------------------
# /function_calls
```
std_msgs/msg/String

# This was originally provided as an example message.
# It is deprecated as of Foxy
# It is recommended to create your own semantically meaningful message.
# However if you would like to continue using this please use the equivalent in example_msgs.

string data

```
------------------------------
# /hazard_detection
```
irobot_create_msgs/msg/HazardDetectionVector

# This message contains a vector of detected hazards.

std_msgs/Header header
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
irobot_create_msgs/HazardDetection[] detections
        uint8 BACKUP_LIMIT=0
        uint8 BUMP=1
        uint8 CLIFF=2
        uint8 STALL=3
        uint8 WHEEL_DROP=4
        uint8 OBJECT_PROXIMITY=5
        std_msgs/Header header
                builtin_interfaces/Time stamp
                        int32 sec
                        uint32 nanosec
                string frame_id
        uint8 type

```
------------------------------
# /hmi/buttons
```
turtlebot4_msgs/msg/UserButton

# This message relays the state of the user buttons
# Each button is represented with a boolean, were True indicates the button is pressed

bool[4] button

```
------------------------------
# /hmi/display
```
turtlebot4_msgs/msg/UserDisplay

# This message represents the header and 5 entries
# that are displayed on the Turtlebot4 display
# selected_entry indicates which menu entry is currently selected

string ip
string battery
string[5] entries
int32 selected_entry

```
------------------------------
# /hmi/display/message
```
std_msgs/msg/String

# This was originally provided as an example message.
# It is deprecated as of Foxy
# It is recommended to create your own semantically meaningful message.
# However if you would like to continue using this please use the equivalent in example_msgs.

string data

```
------------------------------
# /hmi/led
```
turtlebot4_msgs/msg/UserLed

# This message sets the state of the user LEDs
# Blink period is the time in milliseconds during which the ON/OFF cycle occurs
# The duty cycle represents the percentage of the blink period that the LED is ON
# A duty cycle of 1.0 would set the LED to always be ON, whereas a duty cycle of 0.0 is always OFF
# A blink period of 1000ms with a duty cycle of 0.6 will have the LED turn ON for 600ms,
# then OFF for 400ms

# Available LEDs
uint8 USER_LED_1 = 0
uint8 USER_LED_2 = 1

# Available colors
uint8 COLOR_OFF = 0
uint8 COLOR_GREEN = 1
uint8 COLOR_RED = 2
uint8 COLOR_YELLOW = 3


# Which available LED to use
uint8 led

# Which color to set the LED to
uint8 color

# Blink period in ms
uint32 blink_period

# Duty cycle (0.0 to 1.0)
float64 duty_cycle

```
------------------------------
# /imu
```
sensor_msgs/msg/Imu

# This is a message to hold data from an IMU (Inertial Measurement Unit)
#
# Accelerations should be in m/s^2 (not in g's), and rotational velocity should be in rad/sec
#
# If the covariance of the measurement is known, it should be filled in (if all you know is the
# variance of each measurement, e.g. from the datasheet, just put those along the diagonal)
# A covariance matrix of all zeros will be interpreted as "covariance unknown", and to use the
# data a covariance will have to be assumed or gotten from some other source
#
# If you have no estimate for one of the data elements (e.g. your IMU doesn't produce an
# orientation estimate), please set element 0 of the associated covariance matrix to -1
# If you are interpreting this message, please check for a value of -1 in the first element of each
# covariance matrix, and disregard the associated estimate.

std_msgs/Header header
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id

geometry_msgs/Quaternion orientation
        float64 x 0
        float64 y 0
        float64 z 0
        float64 w 1
float64[9] orientation_covariance # Row major about x, y, z axes

geometry_msgs/Vector3 angular_velocity
        float64 x
        float64 y
        float64 z
float64[9] angular_velocity_covariance # Row major about x, y, z axes

geometry_msgs/Vector3 linear_acceleration
        float64 x
        float64 y
        float64 z
float64[9] linear_acceleration_covariance # Row major x, y z

```
------------------------------
# /interface_buttons
```
irobot_create_msgs/msg/InterfaceButtons

# This message is the status of the 3 interface buttons on the Create faceplate
std_msgs/Header header # Header stamp is time at which information was collected
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
irobot_create_msgs/Button button_1     # Left button on faceplate marked with 1 dot
        std_msgs/Header header                            #
                builtin_interfaces/Time stamp
                        int32 sec
                        uint32 nanosec
                string frame_id
        bool is_pressed                                   #
        builtin_interfaces/Time last_start_pressed_time   #
                int32 sec
                uint32 nanosec
        builtin_interfaces/Duration last_pressed_duration #
                int32 sec
                uint32 nanosec
irobot_create_msgs/Button button_power # Center Power button on faceplate
        std_msgs/Header header                            #
                builtin_interfaces/Time stamp
                        int32 sec
                        uint32 nanosec
                string frame_id
        bool is_pressed                                   #
        builtin_interfaces/Time last_start_pressed_time   #
                int32 sec
                uint32 nanosec
        builtin_interfaces/Duration last_pressed_duration #
                int32 sec
                uint32 nanosec
irobot_create_msgs/Button button_2     # Right button on faceplate marked with 2 dots
        std_msgs/Header header                            #
                builtin_interfaces/Time stamp
                        int32 sec
                        uint32 nanosec
                string frame_id
        bool is_pressed                                   #
        builtin_interfaces/Time last_start_pressed_time   #
                int32 sec
                uint32 nanosec
        builtin_interfaces/Duration last_pressed_duration #
                int32 sec
                uint32 nanosec

```
------------------------------
# /ip
```
std_msgs/msg/String

# This was originally provided as an example message.
# It is deprecated as of Foxy
# It is recommended to create your own semantically meaningful message.
# However if you would like to continue using this please use the equivalent in example_msgs.

string data

```
------------------------------
# /joint_states
```
sensor_msgs/msg/JointState

# This is a message that holds data to describe the state of a set of torque controlled joints.
#
# The state of each joint (revolute or prismatic) is defined by:
#  * the position of the joint (rad or m),
#  * the velocity of the joint (rad/s or m/s) and
#  * the effort that is applied in the joint (Nm or N).
#
# Each joint is uniquely identified by its name
# The header specifies the time at which the joint states were recorded. All the joint states
# in one message have to be recorded at the same time.
#
# This message consists of a multiple arrays, one for each part of the joint state.
# The goal is to make each of the fields optional. When e.g. your joints have no
# effort associated with them, you can leave the effort array empty.
#
# All arrays in this message should have the same size, or be empty.
# This is the only way to uniquely associate the joint name with the correct
# states.

std_msgs/Header header
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id

string[] name
float64[] position
float64[] velocity
float64[] effort

```
------------------------------
# /joy
```
sensor_msgs/msg/Joy

# Reports the state of a joystick's axes and buttons.

# The timestamp is the time at which data is received from the joystick.
std_msgs/Header header
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id

# The axes measurements from a joystick.
float32[] axes

# The buttons measurements from a joystick.
int32[] buttons

```
------------------------------
# /joy/set_feedback
```
sensor_msgs/msg/JoyFeedbackArray

# This message publishes values for multiple feedback at once.
JoyFeedback[] array
        uint8 TYPE_LED    = 0
        uint8 TYPE_RUMBLE = 1
        uint8 TYPE_BUZZER = 2
        uint8 type
        uint8 id
        float32 intensity

```
------------------------------
# /mouse
```
irobot_create_msgs/msg/Mouse

# This message contains a mouse raw measurement.

std_msgs/Header header    # Header stamp should be acquisition time of mouse measure.
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
float32 integrated_x      # Motions in the X dimension in meters.
float32 integrated_y      # Motions in the Y dimension in meters.
uint32 frame_id           # Value incremented every time mouse stops tracking
uint8 last_squal          # Surface quality level. It's proportional to the number of valid features visible by the sensor.

```
------------------------------
# /oakd/rgb/preview/image_raw
```
sensor_msgs/msg/Image

# This message contains an uncompressed image
# (0, 0) is at top-left corner of image

std_msgs/Header header # Header timestamp should be acquisition time of image
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
                             # Header frame_id should be optical frame of camera
                             # origin of frame should be optical center of cameara
                             # +x should point to the right in the image
                             # +y should point down in the image
                             # +z should point into to plane of the image
                             # If the frame_id here and the frame_id of the CameraInfo
                             # message associated with the image conflict
                             # the behavior is undefined

uint32 height                # image height, that is, number of rows
uint32 width                 # image width, that is, number of columns

# The legal values for encoding are in file src/image_encodings.cpp
# If you want to standardize a new string format, join
# ros-users@lists.ros.org and send an email proposing a new encoding.

string encoding       # Encoding of pixels -- channel meaning, ordering, size
                      # taken from the list of strings in include/sensor_msgs/image_encodings.hpp

uint8 is_bigendian    # is this data bigendian?
uint32 step           # Full row length in bytes
uint8[] data          # actual matrix data, size is (step * rows)

```
------------------------------
# /parameter_events
```
rcl_interfaces/msg/ParameterEvent

# This message contains a parameter event.
# Because the parameter event was an atomic update, a specific parameter name
# can only be in one of the three sets.

# The time stamp when this parameter event occurred.
builtin_interfaces/Time stamp
        int32 sec
        uint32 nanosec

# Fully qualified ROS path to node.
string node

# New parameters that have been set for this node.
Parameter[] new_parameters
        string name
        ParameterValue value
                uint8 type
                bool bool_value
                int64 integer_value
                float64 double_value
                string string_value
                byte[] byte_array_value
                bool[] bool_array_value
                int64[] integer_array_value
                float64[] double_array_value
                string[] string_array_value

# Parameters that have been changed during this event.
Parameter[] changed_parameters
        string name
        ParameterValue value
                uint8 type
                bool bool_value
                int64 integer_value
                float64 double_value
                string string_value
                byte[] byte_array_value
                bool[] bool_array_value
                int64[] integer_array_value
                float64[] double_array_value
                string[] string_array_value

# Parameters that have been deleted during this event.
Parameter[] deleted_parameters
        string name
        ParameterValue value
                uint8 type
                bool bool_value
                int64 integer_value
                float64 double_value
                string string_value
                byte[] byte_array_value
                bool[] bool_array_value
                int64[] integer_array_value
                float64[] double_array_value
                string[] string_array_value

```
------------------------------
# /robot_description
```
std_msgs/msg/String

# This was originally provided as an example message.
# It is deprecated as of Foxy
# It is recommended to create your own semantically meaningful message.
# However if you would like to continue using this please use the equivalent in example_msgs.

string data

```
------------------------------
# /rosout
```
rcl_interfaces/msg/Log

##
## Severity level constants
##
## These logging levels follow the Python Standard
## https://docs.python.org/3/library/logging.html#logging-levels
## And are implemented in rcutils as well
## https://github.com/ros2/rcutils/blob/35f29850064e0c33a4063cbc947ebbfeada11dba/include/rcutils/logging.h#L164-L172
## This leaves space for other standard logging levels to be inserted in the middle in the future,
## as well as custom user defined levels.
## Since there are several other logging enumeration standard for different implementations,
## other logging implementations may need to provide level mappings to match their internal implementations.
##

# Debug is for pedantic information, which is useful when debugging issues.
byte DEBUG=10

# Info is the standard informational level and is used to report expected
# information.
byte INFO=20

# Warning is for information that may potentially cause issues or possibly unexpected
# behavior.
byte WARN=30

# Error is for information that this node cannot resolve.
byte ERROR=40

# Information about a impending node shutdown.
byte FATAL=50

##
## Fields
##

# Timestamp when this message was generated by the node.
builtin_interfaces/Time stamp
        int32 sec
        uint32 nanosec

# Corresponding log level, see above definitions.
uint8 level

# The name representing the logger this message came from.
string name

# The full log message.
string msg

# The file the message came from.
string file

# The function the message came from.
string function

# The line in the file the message came from.
uint32 line

```
------------------------------
# /scan
```
sensor_msgs/msg/LaserScan

# Single scan from a planar laser range-finder
#
# If you have another ranging device with different behavior (e.g. a sonar
# array), please find or create a different message, since applications
# will make fairly laser-specific assumptions about this data

std_msgs/Header header # timestamp in the header is the acquisition time of
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
                             # the first ray in the scan.
                             #
                             # in frame frame_id, angles are measured around
                             # the positive Z axis (counterclockwise, if Z is up)
                             # with zero angle being forward along the x axis

float32 angle_min            # start angle of the scan [rad]
float32 angle_max            # end angle of the scan [rad]
float32 angle_increment      # angular distance between measurements [rad]

float32 time_increment       # time between measurements [seconds] - if your scanner
                             # is moving, this will be used in interpolating position
                             # of 3d points
float32 scan_time            # time between scans [seconds]

float32 range_min            # minimum range value [m]
float32 range_max            # maximum range value [m]

float32[] ranges             # range data [m]
                             # (Note: values < range_min or > range_max should be discarded)
float32[] intensities        # intensity data [device-specific units].  If your
                             # device does not provide intensities, please leave
                             # the array empty.

```
------------------------------
# /tf
```
tf2_msgs/msg/TFMessage

geometry_msgs/TransformStamped[] transforms
        #
        #
        std_msgs/Header header
                builtin_interfaces/Time stamp
                        int32 sec
                        uint32 nanosec
                string frame_id
        string child_frame_id
        Transform transform
                Vector3 translation
                        float64 x
                        float64 y
                        float64 z
                Quaternion rotation
                        float64 x 0
                        float64 y 0
                        float64 z 0
                        float64 w 1

```
------------------------------
# /tf_static
```
tf2_msgs/msg/TFMessage

geometry_msgs/TransformStamped[] transforms
        #
        #
        std_msgs/Header header
                builtin_interfaces/Time stamp
                        int32 sec
                        uint32 nanosec
                string frame_id
        string child_frame_id
        Transform transform
                Vector3 translation
                        float64 x
                        float64 y
                        float64 z
                Quaternion rotation
                        float64 x 0
                        float64 y 0
                        float64 z 0
                        float64 w 1

```
------------------------------
# /wheel_status
```
irobot_create_msgs/msg/WheelStatus

# This message contains status on the wheels

std_msgs/Header header              # Header stamp should be acquisition time of measure.
        builtin_interfaces/Time stamp
                int32 sec
                uint32 nanosec
        string frame_id
int16 current_ma_left               # Current measurement for left wheel in milliamps
int16 current_ma_right              # Current measurement for right wheel in milliamps
int16 pwm_left                      # PWM % duty cycle measurement (where int16::max is +100%) for left wheel
int16 pwm_right                     # PWM % duty cycle measurement (where int16::max is +100%) for right wheel
bool wheels_enabled                 # Whether wheels are enabled or disabled (disabled when E-Stopped)
```