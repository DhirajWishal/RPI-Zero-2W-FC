import os
import sys
from control import run_control_loop


def check_hardware_and_software():
    # For non-Windows systems, ensure the I2C device exists.
    if os.name != 'nt' and not os.path.exists("/dev/i2c-1"):
        print("Error: /dev/i2c-1 not found. Ensure that I2C is enabled on this system.")
        sys.exit(1)

    # Optionally, verify that we're running on a Raspberry Pi.
    model_file = "/proc/device-tree/model"
    if os.path.exists(model_file):
        try:
            with open(model_file, "r") as f:
                model = f.read().strip()
            if "Raspberry Pi" not in model:
                print(
                    "Warning: This device does not appear to be a Raspberry Pi. Behavior may differ in simulation mode.")
        except Exception as e:
            print("Warning: Unable to determine device model:", e)
    else:
        print(
            "Warning: Device model file not found. Proceeding without model verification.")


def main():
    check_hardware_and_software()
    run_control_loop()


if __name__ == '__main__':
    main()
