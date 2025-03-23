import numpy as np
import RPi.GPIO as GPIO
import sys


class MotorController:
    def __init__(self, motor_pins):
        try:
            GPIO.setmode(GPIO.BCM)
        except Exception as e:
            print("Error: Unable to initialize RPi.GPIO. Exception:", e)
            sys.exit(1)
        self.motor_pins = motor_pins
        self.pwm = []
        for pin in motor_pins:
            GPIO.setup(pin, GPIO.OUT)
            p = GPIO.PWM(pin, 50)  # 50 Hz for ESC control
            p.start(0)
            self.pwm.append(p)

    def set_motor_speeds(self, speeds):
        speeds = np.clip(np.array(speeds), 0, 100)
        for p, speed in zip(self.pwm, speeds):
            p.ChangeDutyCycle(float(speed))

    def cleanup(self):
        for p in self.pwm:
            p.stop()
        GPIO.cleanup()
