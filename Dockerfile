FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive

# Generic build arguments (overridden dynamically via docker-compose / .env)
ARG USERNAME=devuser
ARG UID=1000
ARG GID=1000
ARG WS_NAME=car
ARG TMUXP_CONF=tmuxp.yaml
ARG ENTRYPOINT=entrypoint.sh

ENV USERNAME=${USERNAME}
ENV WS_NAME=${WS_NAME}

# Set up locale generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Install additional developer utilities and Qt XCB display dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    gnupg2 \
    sudo \
    software-properties-common \
    lsb-release \
    build-essential \
    python3-full \
    python3-pip \
    python-is-python3 \
    ros-dev-tools \
    tmux \
    tmuxp \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Update rosdep definitions
RUN rosdep update || true

# Set up non-root user matching host UID/GID
RUN if getent passwd ${UID} >/dev/null 2>&1; then userdel -f $(getent passwd ${UID} | cut -d: -f1); fi \
    && if ! getent group ${GID} >/dev/null 2>&1; then groupadd --gid ${GID} ${USERNAME}; fi \
    && useradd -s /bin/bash --uid ${UID} --gid ${GID} -m ${USERNAME} \
    && mkdir -p /home/${USERNAME}/.config \
    && chown -R ${UID}:${GID} /home/${USERNAME}/.config \
    && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && usermod -aG video,plugdev ${USERNAME}
# Create an underlay workspace for global dependencies
# Build micro_ros_msgs into a system underlay
RUN mkdir -p /opt/ros_deps_ws/src && \
    cd /opt/ros_deps_ws/src && \
    git clone -b jazzy https://github.com/micro-ROS/micro_ros_msgs.git && \
    . /opt/ros/jazzy/setup.sh && \
    cd /opt/ros_deps_ws && \
    colcon build --merge-install && \
    rm -rf build log
      
USER ${USERNAME}
WORKDIR /home/${USERNAME}/${WS_NAME}

# Copy configuration files into user workspace

COPY --chown=${UID}:${GID} ./${ENTRYPOINT} /home/${USERNAME}/${WS_NAME}/entrypoint.sh

RUN chmod +x /home/${USERNAME}/${WS_NAME}/entrypoint.sh

# Automate ROS 2 workspace environment sourcing
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/${USERNAME}/.bashrc && \
    echo "if [ -f /home/${USERNAME}/${WS_NAME}/install/local_setup.bash ]; \
        then source /home/${USERNAME}/${WS_NAME}/install/local_setup.bash; \
        fi" >> /home/${USERNAME}/.bashrc && \
    echo "export DISABLE_AUTO_TITLE='true'" >> /home/${USERNAME}/.bashrc

CMD [ "sleep", "infinity" ]