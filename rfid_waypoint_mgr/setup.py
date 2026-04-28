#!/usr/bin/env python3

import os
from setuptools import setup
from glob import glob

package_name = 'rfid_waypoint_mgr' #(1/2)

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
    maintainer='joseph',
    maintainer_email='joe.t.hill00@gmail.com',
    description='A basic package with launching', #(2/2)
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
          "rfid_waypoint_mgr_exec = rfid_waypoint_mgr.rfid_waypoint_mgr_exec:main",
        #   "rfid_faker = rfid_waypoint_mgr.rfid_faker:main",
          "rfid_joseph = rfid_waypoint_mgr.rfid_joseph:main",
          "rfid_finder_node = rfid_waypoint_mgr.rfid_finder:main",
          "rfid_handler_node = rfid_waypoint_mgr.rfid_handler:main"
        ],
    },
)
