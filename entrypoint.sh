#!/bin/bash
set -e

# 1. Source ROS 2 base
source /opt/ros/jazzy/setup.bash

# 2. Source the pre-built dependency underlay
if [ -f "/opt/ros_deps_ws/install/setup.bash" ]; then
    source "/opt/ros_deps_ws/install/setup.bash"
fi

# 3. Source your main workspace overlay (if built)
if [ -f "/home/${USERNAME}/${WS_NAME}/install/setup.bash" ]; then
    source "/home/${USERNAME}/${WS_NAME}/install/setup.bash"
fi

exec "$@"