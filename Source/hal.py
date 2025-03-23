import os
import time

if os.name == 'nt':
    print("Running in simulation mode (Windows). Using dummy hardware interfaces.")

    class IMU:
        def __init__(self, calibration_samples=200):
            print("Simulated IMU initialized (calibration skipped).")
        def get_accel_data(self):
            # Return dummy accelerometer data: device is level (0, 0, 1)
            return (0.0, 0.0, 1.0)
        def get_gyro_data(self):
            # Return dummy gyroscope data: no rotation
            return (0.0, 0.0, 0.0)

    class MotorController:
        def __init__(self, motor_pins):
            self.motor_pins = motor_pins
            self.last_log_time = 0  # Track last log time
            print(f"Simulated MotorController initialized on pins {motor_pins}.")
        def set_motor_speeds(self, speeds):
            current_time = time.time()
            # Log only if at least one second has passed since the last log.
            if current_time - self.last_log_time >= 1.0:
                print(f"Simulated setting motor speeds to: {speeds}")
                self.last_log_time = current_time
        def cleanup(self):
            print("Simulated MotorController cleanup.")

    class IPCReceiver:
        def __init__(self, host='0.0.0.0', port=5005):
            self.control_inputs = {'throttle': 50, 'roll': 0, 'pitch': 0, 'yaw': 0}
            print("Simulated IPCReceiver created.")
        def start(self):
            print("Simulated IPCReceiver started.")
        def run(self):
            # In simulation mode, you might update control_inputs periodically.
            pass

else:
    # On non-Windows (e.g., Linux on Raspberry Pi), use the real implementations.
    from mpu6050 import MPU6050 as IMU
    from motor_controller import MotorController
    from ipc_receiver import IPCReceiver
