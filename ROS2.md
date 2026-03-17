# Set up a Workspace


```bash
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get install nano -y
cd ~
mkdir ros2_ws
cd ros2_ws/
mkdir src
colcon build --symlink
```

Should see “Summary: 0 packages finished” if build was successful. 

```bash
ls
```

Building made build, install, and log folders next to src.

```bash
cd install/
ls
```

Need to source setup.bash

```bash
nano ~/.bashrc
```

add this line to the end of .bashrc

```bash
source ~/ros2_ws/install/setup.bash
```

Save .bashrc. (ctr+s, ctr+x)


# Variables used in this document 
| Variable            | Used In                                                                               | Example          |
| :---                | :---:                                                                                 | ---:             |
| <package_name>      | ros2 pkg create  <package_name><br>~/ros2_ws/src/<package_name>/setup.py (setup)      | basic_pkg        |
| <launcher_name>     | ~/ros2_ws/src/<package_name>/launch/<launcher_name>.launch.py (launcher)              | basic            |
| <excecutable_name>  | launcher <br> ~/ros2_ws/src/<package_name>/scripts/<excecutable_name>.py (executable) | basic_exec       |
| <node_name>         | launcher <br> executable                                                              | basic_node       |
| <node_class>        | executable                                                                            | basic_node_class |
| <python_dependency> | executable <br> ~/ros2_ws/src/<package_name>/package.xml                              | time             |
| \<namespace>        | launcher                                                                              | basic_ns         |  
| <paramater_name>    | launcher <br> executable                                                              | basic_param      |
| <default_value>     | executable                                                                            | basic_default    |
| <parameter_value>   | launcher                                                                              | basic_value      |
| <relative_input>    | launcher <br> executable                                                              | input            |
| <namespace_input>   | launcher                                                                              | echo_input       |
| <relative_output>   | launcher <br> executable                                                              | output           |
| <namespace_output>  | launcher                                                                              | echo_output      |

ROS2 package variables at the start of executables should be set statically, no need to pass them as parameters. Don't change after the 'as', so it can be used in multiple subscribers or publishers.

```python
from input_message_package.input_message_class import input_message_subclass as input_message_subclass
from output_message_package.output_message_class import output_message_subclass as output_message_subclass
```

# Create a Python Package
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python --dependencies rclpy --license Apache-2.0 <package_name>
```

Edit setup.py to add launch file support

```bash
cd ~/ros2_ws/src/<package_name>/
code setup.py
```

```python
import os
from setuptools import setup
from glob import glob

package_name = '<package_name>' #(1/2)

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), 
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='',
    maintainer_email='',
    description='', #(2/2)
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
          
        ],
    },
)

```

Create a launch folder and file for any <launcher_name>

```python
mkdir ~/ros2_ws/src/<package_name>/launch
cd ~/ros2_ws/src/<package_name>/launch
touch __init__.py
touch <launcher_name>.launch.py
code <launcher_name>.launch.py
```

```python
#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='<package_name>', #(1/7)
            executable='<excecutable_name>', #(2/7)
            name='<node_name>', #(3/7)
            namespace='<namespace>',  #(4/7)
            parameters=[{
                '<paramater_name>': <parameter_value>, #(5/7)
						    #fill with dict of parameters
            }],
            remappings=[
                ('<relative_input>', '<namespace_input>'), #(6/7) the world sees /<namespace>/<namespace_input> -> this node sees /<relative_input>
                ('<relative_output>', '<namespace_output>'), #(7/7) this node sees /<relative_output> -> the world sees /<namespace>/<namespace_output>
            ],
            output='screen' # or 'log' if the node should not output
        ),
    ])

```

# Build the Blank Package
cd ~/ros2_ws/
colcon build --symlink-install

# Create a Node
```bash
cd ~/ros2_ws/src/<package_name>
mkdir scripts/
cd scripts/
touch <excecutable_name>.py
chmod +x <excecutable_name>.py
```

Open vscode at workspace source

```bash
cd ~/ros2_ws/src/
code .
```

In vscode open /src/<package_name>/<package_name>/<excecutable_name>.py

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from input_message_package.input_message_class import input_message_subclass as input_message_subclass
from output_message_package.output_message_class import output_message_subclass as output_message_subclass

import <python_dependency>

node_name = <node_name>
input_msg_type = input_message_subclass
output_msg_type = output_message_subclass

relative_input_topic = <relative_input>
relative_output_topic = <relative_output>

qos = 10

class basic_node_class(Node): # change node class name to <node_class>
    def __init__(self):
        super().__init__(node_name)
        self.get_logger().info(f'init {node_name}')
        
        self.declare_parameter('<paramater_name>', '<default_value>') # declare parameters with default values, if any

        self.<paramater_name> = str(self.get_parameter('<paramater_name>').value)

        self.node_subscriber_ = self.create_subscription(
            msg_type=input_msg_type,
            topic=relative_input_topic,
            callback=self.subscriber_callback,
            qos_profile=qos
            )
        
        self.node_publisher_ = self.create_publisher(
            msg_type = output_msg_type, 
            topic = relative_output_topic,
            qos_profile = qos
            )
        
    def subscriber_callback(self, input_msg: input_msg_type):
        self.get_logger().info(f'Input: {str(input_msg)}')
        output_msg = output_msg_type()
        output_msg.data = str(input_msg)
        self.node_publisher_.publish(output_msg)
        self.get_logger().info(f'Output: {str(output_msg)}')

def main(args=None):
    rclpy.init(args=args)
    node = basic_node_class()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
```

# Install a Node (Handle Python Dependencies)
Navigate to package.xml

```bash
cd ~/ros2_ws/src/<package_name>/
code package.xml
```

Add a executable dependency to the package

```xml
<exec_depend>python_dependency</exec_depend>
```
like
```xml
<exec_depend>numpy</exec_depend>
```

# Build a Package
```bash
cd ~/ros2_ws/
colcon build --symlink-install --packages-select <package_name>
source ~/.bashrc
```

# Launch a Package
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch <package_name> <launcher_name>.launch.py
```