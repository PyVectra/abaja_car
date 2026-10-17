#!/usr/bin/env python3

import time
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class AutonBrakeController(Node):
    def __init__(self):
        super().__init__('auton_brake_controller')

        # Stepper Motor Specs (1.8° per step -> 200 steps/rev)
        self.STEP_ANGLE = 1.8
        self.STEPS_PER_REV = 360.0 / self.STEP_ANGLE  # 200 steps

        # Flag: Set True if MCU expects angle in degrees (5400°),
        # or False if MCU expects step pulse counts (3000 steps).
        self.PUBLISH_DEGREES = True

        # Ramping parameters
        self.STEP_SIZE_DEG = 1.80   # Increment per step in degrees (10 motor steps)
        self.STEP_INTERVAL = 0.05   # Delay between steps in seconds (50ms)

        # Publisher: Sends brake position commands to Microcontroller
        self.cmd_publisher = self.create_publisher(Float32, '/brake_command', 10)

        # Subscriber: Receives actual position state feedback from MCU
        self.state_subscriber = self.create_subscription(
            Float32,
            '/brake_state',
            self.state_callback,
            10
        )

        self.current_pos_deg = 0.0
        self.target_pos_deg = 0.0
        self.actual_state = 0.0
        self.feedback_received = False

        # Ramping thread handles
        self.ramping_thread = None
        self.is_ramping = False
        self._ramp_lock = threading.Lock()

        self.get_logger().info('Autonomous Brake Stepper Controller Online.')

    def state_callback(self, msg: Float32):
        """Callback for feedback state from microcontroller."""
        self.actual_state = msg.data
        self.feedback_received = True

    def set_target_angle(self, target_deg: float):
        """Sets new target position in degrees and initiates step ramping."""
        self.target_pos_deg = target_deg

        with self._ramp_lock:
            if not self.is_ramping:
                self.is_ramping = True
                self.ramping_thread = threading.Thread(target=self._ramp_process, daemon=True)
                self.ramping_thread.start()

    def _ramp_process(self):
        """Ramps current_pos_deg towards target_pos_deg in smooth increments."""
        while rclpy.ok() and abs(self.current_pos_deg - self.target_pos_deg) > 0.01:
            if self.current_pos_deg < self.target_pos_deg:
                self.current_pos_deg = min(self.current_pos_deg + self.STEP_SIZE_DEG, self.target_pos_deg)
            else:
                self.current_pos_deg = max(self.current_pos_deg - self.STEP_SIZE_DEG, self.target_pos_deg)

            # Convert to motor steps if required by MCU
            pub_val = self.current_pos_deg if self.PUBLISH_DEGREES else (self.current_pos_deg / self.STEP_ANGLE)

            msg = Float32()
            msg.data = float(pub_val)
            self.cmd_publisher.publish(msg)

            unit_str = "°" if self.PUBLISH_DEGREES else " steps"
            self.get_logger().info(f' [BRAKE STEP] Published: {pub_val:.1f}{unit_str}')
            time.sleep(self.STEP_INTERVAL)

        self.is_ramping = False

    def wait_for_completion(self, timeout_sec: float = 30.0):
        """Blocks main loop execution until ramping is complete."""
        start_time = time.time()
        while self.is_ramping and (time.time() - start_time) < timeout_sec:
            time.sleep(0.1)


def main(args=None):
    rclpy.init(args=args)
    node = AutonBrakeController()

    # Spin ROS 2 background thread for async callbacks
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    TOTAL_CYCLES = 6
    REVOLUTIONS = 1
    TARGET_DEG = REVOLUTIONS * 360.0 
    try:
        time.sleep(1.0)  # Wait for publishers/subscribers to connect

        for cycle in range(1, TOTAL_CYCLES + 1):
            print(f"\n================ CYCLE {cycle} / {TOTAL_CYCLES} ================")

            # Step 1: Rotate 5 Revolutions Clockwise (+5400° / +3000 steps)
            node.get_logger().info(
                f'Cycle {cycle}: Rotating 5 Revs Clockwise (+{TARGET_DEG:.0f}° / +{int(TARGET_DEG / 1.8)} steps)'
            )
            node.set_target_angle(TARGET_DEG)
            node.wait_for_completion(timeout_sec=30.0)

            time.sleep(1.0)  # Pause between direction changes

            # Step 2: Rotate 5 Revolutions Counter-Clockwise (0°)
            node.get_logger().info(f'Cycle {cycle}: Rotating 5 Revs Counter-Clockwise (0°)')
            node.set_target_angle(0.0)
            node.wait_for_completion(timeout_sec=30.0)

            time.sleep(1.0)  # Pause before next cycle

        print("\nAll 10 cycle iterations completed successfully.")

    except KeyboardInterrupt:
        print("\nExecution canceled by user.")
    finally:
        print("Shutting down brake controller...")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()