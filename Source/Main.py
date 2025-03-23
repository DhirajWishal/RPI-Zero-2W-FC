import os
import sys
import time

from pid import PID
from madgwick import MadgwickAHRS

# Import hardware interfaces from the HAL
from hal import IMU, MotorController, IPCReceiver


def check_hardware_and_software():
    # On Raspberry Pi, verify that the I2C bus exists.
    if os.name != 'nt' and not os.path.exists("/dev/i2c-1"):
        print("Error: /dev/i2c-1 not found. Ensure that I2C is enabled and available on this system.")
        sys.exit(1)
    # Optionally, check device model if available.
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


def main():
    check_hardware_and_software()

    # Initialize hardware (either real or simulated)
    mpu = IMU(calibration_samples=200)
    madgwick = MadgwickAHRS(beta=0.1)
    motor_pins = [17, 18, 27, 22]  # Adjust as needed.
    motors = MotorController(motor_pins)
    ipc_receiver = IPCReceiver(port=5005)
    ipc_receiver.start()

    pid_roll = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_pitch = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_yaw = PID(Kp=1.0, Ki=0.0, Kd=0.05)

    last_update = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_update
            last_update = current_time

            ax, ay, az = mpu.get_accel_data()
            gx, gy, gz = mpu.get_gyro_data()

            madgwick.updateIMU(gx, gy, gz, ax, ay, az, dt)
            roll_angle, pitch_angle, _ = madgwick.getEulerAngles()

            set_throttle = ipc_receiver.control_inputs['throttle']
            set_roll = ipc_receiver.control_inputs['roll']
            set_pitch = ipc_receiver.control_inputs['pitch']
            set_yaw = ipc_receiver.control_inputs['yaw']

            pid_roll.setpoint = set_roll
            pid_pitch.setpoint = set_pitch
            pid_yaw.setpoint = set_yaw

            roll_correction = pid_roll.update(roll_angle)
            pitch_correction = pid_pitch.update(pitch_angle)
            # Using gyro Z for yaw correction
            yaw_correction = pid_yaw.update(gz)

            motor_outputs = [
                set_throttle + pitch_correction + roll_correction - yaw_correction,
                set_throttle + pitch_correction - roll_correction + yaw_correction,
                set_throttle - pitch_correction + roll_correction + yaw_correction,
                set_throttle - pitch_correction - roll_correction - yaw_correction
            ]

            motors.set_motor_speeds(motor_outputs)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        motors.cleanup()


if __name__ == '__main__':
    main()
