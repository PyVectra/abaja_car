import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'car_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # ◄─ THIS LINE INSTALLS LAUNCH FILES
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vaishu',
    maintainer_email='vaishu@todo.todo',
    description='Drive-by-wire control package',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'steer_angle_t_node = car_control.steer_angle_t:main',
            'brake_node = car_control.braking_angle_t:main',
        ],
    },
)