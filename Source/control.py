import os
import sys
import time
from pid import PID
from madgwick import MadgwickAHRS
from hal import IMU, MotorController, IPCReceiver
from server import flight_status

def check_hardware_and_software():
    # On Raspberry Pi (non-Windows), verify that the I2C bus exists.
    if os.name != 'nt' and not os.path.exists("/dev/i2c-1"):
        print("Error: /dev/i2c-1 not found. Ensure that I2C is enabled on this system.")
        sys.exit(1)
    # Optionally, check for device model
    model_file = "/proc/device-tree/model"
    if os.path.exists(model_file):
        try:
            with open(model_file, "r") as f:
                model = f.read().strip()
            if "Raspberry Pi" not in model:
                print("Warning: This device does not appear to be a Raspberry Pi. Flight controller may not work as expected.")
        except Exception as e:
            print("Warning: Unable to determine device model:", e)
    else:
        print("Warning: Device model file not found. Proceeding without model verification.")

def run_control_loop():
    check_hardware_and_software()
    
    # Initialize the IMU (real or simulated) with calibration.
    mpu = IMU(calibration_samples=200)
    # Initialize the Madgwick filter.
    madgwick = MadgwickAHRS(beta=0.1)
    # Set up motor controller (pins as defined for your quadcopter).
    motor_pins = [17, 18, 27, 22]
    motors = MotorController(motor_pins)
    # Start the IPC receiver for control setpoints.
    ipc_receiver = IPCReceiver(port=5005)
    ipc_receiver.start()
    
    # Create PID controllers for stabilization.
    pid_roll = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_pitch = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    pid_yaw = PID(Kp=1.0, Ki=0.0, Kd=0.05)
    
    last_update = time.time()

    while True:
        current_time = time.time()
        dt = current_time - last_update
        last_update = current_time
        
        # Read sensor data.
        ax, ay, az = mpu.get_accel_data()
        gx, gy, gz = mpu.get_gyro_data()
        
        # Update sensor fusion filter.
        madgwick.updateIMU(gx, gy, gz, ax, ay, az, dt)
        roll_angle, pitch_angle, yaw_angle = madgwick.getEulerAngles()
        
        # Read desired control inputs from IPC.
        set_throttle = ipc_receiver.control_inputs['throttle']
        set_roll     = ipc_receiver.control_inputs['roll']
        set_pitch    = ipc_receiver.control_inputs['pitch']
        set_yaw      = ipc_receiver.control_inputs['yaw']
        
        # Update PID setpoints.
        pid_roll.setpoint = set_roll
        pid_pitch.setpoint = set_pitch
        pid_yaw.setpoint = set_yaw
        
        # Calculate PID corrections.
        roll_correction  = pid_roll.update(roll_angle)
        pitch_correction = pid_pitch.update(pitch_angle)
        yaw_correction   = pid_yaw.update(gz)  # Using gyro Z for yaw
        
        # Mix motor outputs for an "X" configuration.
        motor_outputs = [
            set_throttle + pitch_correction + roll_correction - yaw_correction,
            set_throttle + pitch_correction - roll_correction + yaw_correction,
            set_throttle - pitch_correction + roll_correction + yaw_correction,
            set_throttle - pitch_correction - roll_correction - yaw_correction
        ]
        
        # Update the motors.
        motors.set_motor_speeds(motor_outputs)
        
        # Update the global flight status for the web server.
        flight_status["motor_outputs"] = motor_outputs
        flight_status["accelerometer"] = {"ax": ax, "ay": ay, "az": az}
        flight_status["gyroscope"] = {"gx": gx, "gy": gy, "gz": gz}
        flight_status["orientation"] = {"roll": roll_angle, "pitch": pitch_angle, "yaw": yaw_angle}
        
        # Append a log entry (limit logs to 100 entries).
        flight_status["logs"].append(
            "Update at {:.2f}: Roll {:.2f}, Pitch {:.2f}, Yaw {:.2f}".format(time.time(), roll_angle, pitch_angle, yaw_angle)
        )
        if len(flight_status["logs"]) > 100:
            flight_status["logs"].pop(0)

def run_control_loop_wrapper():
    try:
        run_control_loop()
    except KeyboardInterrupt:
        print("Control loop interrupted. Exiting.")
