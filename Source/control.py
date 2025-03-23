import time
from pid import PID
from madgwick import MadgwickAHRS
from hal import IMU, MotorController, IPCReceiver

def run_control_loop():
    # Initialize hardware interfaces
    mpu = IMU(calibration_samples=200)
    madgwick = MadgwickAHRS(beta=0.1)
    # Define motor GPIO pins (adjust as needed)
    motor_pins = [17, 18, 27, 22]
    motors = MotorController(motor_pins)
    ipc_receiver = IPCReceiver(port=5005)
    ipc_receiver.start()

    # Create PID controllers for each axis
    pid_roll = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_pitch = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_yaw = PID(Kp=1.0, Ki=0.0, Kd=0.05)

    last_update = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_update
            last_update = current_time

            # Get sensor data
            ax, ay, az = mpu.get_accel_data()
            gx, gy, gz = mpu.get_gyro_data()
            
            # Update orientation using the Madgwick filter with the measured dt
            madgwick.updateIMU(gx, gy, gz, ax, ay, az, dt)
            roll_angle, pitch_angle, _ = madgwick.getEulerAngles()

            # Read control inputs (e.g., throttle, roll, pitch, yaw)
            set_throttle = ipc_receiver.control_inputs['throttle']
            set_roll = ipc_receiver.control_inputs['roll']
            set_pitch = ipc_receiver.control_inputs['pitch']
            set_yaw = ipc_receiver.control_inputs['yaw']

            # Set PID setpoints
            pid_roll.setpoint = set_roll
            pid_pitch.setpoint = set_pitch
            pid_yaw.setpoint = set_yaw

            # Compute PID corrections
            roll_correction = pid_roll.update(roll_angle)
            pitch_correction = pid_pitch.update(pitch_angle)
            yaw_correction = pid_yaw.update(gz)  # using gyro Z for yaw correction

            # Motor mixing for an "X" configuration quadcopter
            motor_outputs = [
                set_throttle + pitch_correction + roll_correction - yaw_correction,
                set_throttle + pitch_correction - roll_correction + yaw_correction,
                set_throttle - pitch_correction + roll_correction + yaw_correction,
                set_throttle - pitch_correction - roll_correction - yaw_correction
            ]

            motors.set_motor_speeds(motor_outputs)

    except KeyboardInterrupt:
        print("Shutting down control loop...")
    finally:
        motors.cleanup()
