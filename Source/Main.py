#!/usr/bin/env python3
import time
import os
import sys

import PID
import MPU6050
import MotorController
import IPCReceiver
import MadgwickAHRS


# ------------------------------
# Preliminary Hardware/Software Check
# ------------------------------
def check_hardware_and_software():
    # Check if the I2C device file exists (required for MPU6050 communication)
    if not os.path.exists("/dev/i2c-1"):
        print("Error: /dev/i2c-1 not found. Ensure that I2C is enabled and available on this system.")
        sys.exit(1)

    # Optionally, check if the device appears to be a Raspberry Pi by reading the model file.
    model_file = "/proc/device-tree/model"
    if os.path.exists(model_file):
        try:
            with open(model_file, "r") as f:
                model = f.read().strip()
            if "Raspberry Pi" not in model:
                print(
                    "Warning: This device does not appear to be a Raspberry Pi. Flight controller may not work as expected.")
        except Exception as e:
            print("Warning: Unable to determine device model:", e)
    else:
        print(
            "Warning: Device model file not found. Proceeding without model verification.")


# ------------------------------
# Main Flight Controller Loop
# ------------------------------
def main():
    # Perform hardware/software checks before proceeding
    check_hardware_and_software()

    # Initialize MPU6050 with calibration
    mpu = MPU6050(calibration_samples=200)
    # Initialize Madgwick filter (50 Hz sample period)
    madgwick = MadgwickAHRS(sample_period=0.02, beta=0.1)
    # Define motor GPIO pins (adjust as needed)
    # [Front Left, Front Right, Rear Left, Rear Right]
    motor_pins = [17, 18, 27, 22]
    motors = MotorController(motor_pins)
    # Start IPC receiver thread (UDP on port 5005)
    ipc_receiver = IPCReceiver(port=5005)
    ipc_receiver.start()
    # Create PID controllers for roll, pitch, and yaw stabilization
    pid_roll = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_pitch = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_yaw = PID(Kp=1.0, Ki=0.0, Kd=0.05)

    try:
        while True:
            # Read sensor data
            ax, ay, az = mpu.get_accel_data()
            gx, gy, gz = mpu.get_gyro_data()

            # Update the Madgwick filter with current IMU data
            madgwick.updateIMU(gx, gy, gz, ax, ay, az)
            roll_angle, pitch_angle, _ = madgwick.getEulerAngles()

            # Get desired control setpoints from IPC
            set_throttle = ipc_receiver.control_inputs['throttle']
            set_roll = ipc_receiver.control_inputs['roll']
            set_pitch = ipc_receiver.control_inputs['pitch']
            set_yaw = ipc_receiver.control_inputs['yaw']

            # Update PID setpoints
            pid_roll.setpoint = set_roll
            pid_pitch.setpoint = set_pitch
            pid_yaw.setpoint = set_yaw

            # Compute PID corrections
            roll_correction = pid_roll.update(roll_angle)
            pitch_correction = pid_pitch.update(pitch_angle)
            yaw_correction = pid_yaw.update(gz)  # using gyro Z for yaw

            # Motor mixing for an "X" configuration quadcopter:
            # Front Left  = throttle + pitch + roll - yaw
            # Front Right = throttle + pitch - roll + yaw
            # Rear Left   = throttle - pitch + roll + yaw
            # Rear Right  = throttle - pitch - roll - yaw
            motor_outputs = [
                set_throttle + pitch_correction + roll_correction - yaw_correction,
                set_throttle + pitch_correction - roll_correction + yaw_correction,
                set_throttle - pitch_correction + roll_correction + yaw_correction,
                set_throttle - pitch_correction - roll_correction - yaw_correction
            ]

            motors.set_motor_speeds(motor_outputs)
            time.sleep(0.02)  # 50 Hz loop

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        motors.cleanup()


if __name__ == '__main__':
    main()
