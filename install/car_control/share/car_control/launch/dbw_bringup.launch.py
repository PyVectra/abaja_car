import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # 1. Micro-ROS Agent (Connects to ESP32 over USB Serial)
    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        output='screen',
        arguments=['serial', '--dev', '/dev/ttyACM0', '-b', '115200']
    )

    # 2. Steering Controller Node
    steer_node = Node(
        package='car_control',
        executable='steer_angle_t_node',
        name='steer_angle_t_node',
        output='screen'
    )

    # 3. Brake Controller Node
    brake_node = Node(
        package='car_control',
        executable='brake_node',
        name='brake_node',
        output='screen'
    )

    return LaunchDescription([
        micro_ros_agent,
        steer_node,
        brake_node
    ])