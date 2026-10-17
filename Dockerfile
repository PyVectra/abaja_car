FROM ros:jazzy-ros-base

WORKDIR /car

# 1. Install required build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p src && \
    /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build"

# 3. Copy your project code into the workspace
COPY . /car/

# 4. Auto-source ROS 2 and micro-ROS on startup
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "source /car/install/setup.bash" >> /root/.bashrc

CMD ["bash"]