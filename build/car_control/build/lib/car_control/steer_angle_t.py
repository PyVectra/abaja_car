#!/usr/bin/env python3

import time
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class AutonSteeringController(Node):
    def __init__(self):
        super().__init__('auton_steering_controller')

        # 1:181 Gear Ratio multiplier.
        # Set to 181.0 if MCU expects motor shaft degrees.
        # Set to 1.0 if MCU already accounts for gear reduction internally.
        self.gear_ratio = 181.0

        # Publisher: Sends target angle commands to Microcontroller
        self.cmd_publisher = self.create_publisher(Float32, '/steering_angle', 10)

        # Subscriber: Receives actual position state feedback from Microcontroller
        self.state_subscriber = self.create_subscription(
            Float32,
            '/steering_state',
            self.state_callback,
            10
        )

        self.current_angle = 0.0
        self.target_angle = 0.0
        self.is_moving = False
        self.feedback_received = False

        self.get_logger().info('Autonomous Steering Interface Online.')

    def state_callback(self, msg: Float32):
        """Triggered whenever the Microcontroller publishes its position feedback."""
        self.current_angle = msg.data
        self.feedback_received = True
        self.get_logger().info(f' [STATE FEEDBACK] Motor Position: {self.current_angle:.2f}°')

        # Tolerance check (adjust 0.2 if gear reduction makes feedback steps larger/smaller)
        if abs(self.current_angle - self.target_angle) <= 0.2:
            self.is_moving = False

    def send_target_angle(self, output_angle_deg: float, apply_gear_ratio: bool = True):
        """Publishes target angle to ROS 2 topic, scaled by gear ratio."""
        effective_angle = output_angle_deg * self.gear_ratio if apply_gear_ratio else output_angle_deg
        
        self.target_angle = effective_angle
        self.is_moving = True

        msg = Float32()
        msg.data = float(effective_angle)
        self.cmd_publisher.publish(msg)
        self.get_logger().info(
            f' [COMMAND SENT] Desired Output: {output_angle_deg:.1f}° | Target Command: {effective_angle:.1f}°'
        )

    def wait_for_completion(self, timeout_sec: float = 15.0, fallback_delay: float = 5.0):
        """Blocks until position feedback confirms target is reached, or falls back to time delay."""
        start_time = time.time()
        time.sleep(0.2)  # Short delay for state subscriber updates

        # Fallback if MCU is not publishing state feedback on /steering_state
        if not self.feedback_received:
            self.get_logger().info(f'No state feedback detected. Sleeping for {fallback_delay}s for movement...')
            time.sleep(fallback_delay)
            self.is_moving = False
            return

        while self.is_moving and (time.time() - start_time) < timeout_sec:
            time.sleep(0.1)

        if self.is_moving:
            self.get_logger().warn('Timeout reached before position state was confirmed.')
            self.is_moving = False


def main(args=None):
    rclpy.init(args=args)
    node = AutonSteeringController()

    # Spin ROS 2 callbacks in background thread
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    TOTAL_CYCLES = 10
    ONE_REV_DEG = 360.0  # Output shaft target

    try:
        time.sleep(1.0)  # Wait for publishers/subscribers to connect

        for cycle in range(1, TOTAL_CYCLES + 1):
            print(f"\n================ CYCLE {cycle} / {TOTAL_CYCLES} ================")

            # Step 1: 1 Revolution Clockwise (+360° output = +65,160° motor)
            node.get_logger().info(f'Cycle {cycle}: Rotating 1 Revolution Clockwise (+360°)')
            node.send_target_angle(ONE_REV_DEG, apply_gear_ratio=True)
            node.wait_for_completion(timeout_sec=20.0, fallback_delay=5.0)

            time.sleep(1.0)  # Pause between direction changes

            # Step 2: 1 Revolution Counter-Clockwise (Back to 0° output)
            node.get_logger().info(f'Cycle {cycle}: Rotating 1 Revolution Counter-Clockwise (0°)')
            node.send_target_angle(0.0, apply_gear_ratio=True)
            node.wait_for_completion(timeout_sec=20.0, fallback_delay=5.0)

            time.sleep(1.0)  # Pause before next cycle

        print("\nAll 10 revolution cycles completed successfully.")

    except KeyboardInterrupt:
        print("\nExecution canceled by user.")
    finally:
        print("Shutting down steering controller...")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()