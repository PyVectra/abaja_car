# Autonomous DBW Controller - ROS 2 Jazzy

This repository contains the ROS 2 Drive-by-Wire (DBW) control system and Micro-ROS agent interface for autonomous vehicle steering and braking actuators powered by an ESP32 microcontroller.

---

## Prerequisites
Ensure your host machine has Docker installed and proper serial device permissions set up.

1. **Install Docker Engine:**
   * Linux: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
   * Windows / Mac: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Configure USB/Serial Permissions (Linux Users):**
   Grant your local user access to serial ports (`/dev/ttyUSB*`) and Docker without requiring `sudo`:
   ```bash
   sudo usermod -aG dialout $USER
   sudo usermod -aG docker $USER
   ```
## Getting started 
### Step 1 : Clone the Repository
#### Option A: Clone Directly
   ```bash
   git clone --recurse-submodule https://github.com/VaishnaviPasumarthi9/abaja_car.git
   cd car
  ```
#### Option B: Fork it first (preferred)
```bash
git clone --recurse-submodule https://github.com/VaishnaviPasumarthi9/abaja_car.git
cd car
  ```
### Step 2 : Run the Dockerfile
```bash
docker compose up -d --build
  ```
To run/restart the container remove the --build tag from the command

### Step 3 : Attaching to the Container
```bash
docker exec -it my_ros_env /bin/bash
```

### Step 4 : Running the nodes 
```bash
cd car/src/car_control
ros2 launch car_control dbw_bringup.launch.py
```














