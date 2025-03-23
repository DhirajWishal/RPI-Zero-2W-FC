import numpy as np
import smbus
import time
import sys

class MPU6050:
    def __init__(self, address=0x68, bus_num=1, calibration_samples=200):
        try:
            self.bus = smbus.SMBus(bus_num)
        except Exception as e:
            print("Error: Unable to open I2C bus. Ensure that I2C is enabled. Exception:", e)
            sys.exit(1)
        self.address = address
        # Wake up the MPU6050 (it starts in sleep mode)
        self.bus.write_byte_data(self.address, 0x6B, 0)
        self.accel_offsets = np.zeros(3)
        self.gyro_offsets = np.zeros(3)
        self.calibrate(calibration_samples)
    
    def read_raw_data(self, addr):
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr+1)
        value = (high << 8) | low
        if value > 32767:
            value = value - 65536
        return value

    def calibrate(self, samples=200):
        print("Calibrating MPU6050...")
        ax_sum = 0
        ay_sum = 0
        az_sum = 0
        gx_sum = 0
        gy_sum = 0
        gz_sum = 0
        for _ in range(samples):
            ax_sum += self.read_raw_data(0x3B)
            ay_sum += self.read_raw_data(0x3D)
            az_sum += self.read_raw_data(0x3F)
            gx_sum += self.read_raw_data(0x43)
            gy_sum += self.read_raw_data(0x45)
            gz_sum += self.read_raw_data(0x47)
        avg_ax = ax_sum / samples / 16384.0
        avg_ay = ay_sum / samples / 16384.0
        avg_az = az_sum / samples / 16384.0
        # Assume sensor is level: expected ax,ay=0 and az=+1g
        self.accel_offsets = np.array([avg_ax, avg_ay, avg_az - 1.0])
        self.gyro_offsets = np.array([gx_sum, gy_sum, gz_sum]) / samples / 131.0
        print("Calibration complete.")
        print("Accelerometer offsets:", self.accel_offsets)
        print("Gyro offsets:", self.gyro_offsets)

    def get_accel_data(self):
        raw_ax = self.read_raw_data(0x3B)
        raw_ay = self.read_raw_data(0x3D)
        raw_az = self.read_raw_data(0x3F)
        Ax = raw_ax / 16384.0 - self.accel_offsets[0]
        Ay = raw_ay / 16384.0 - self.accel_offsets[1]
        Az = raw_az / 16384.0 - self.accel_offsets[2]
        return Ax, Ay, Az

    def get_gyro_data(self):
        raw_gx = self.read_raw_data(0x43)
        raw_gy = self.read_raw_data(0x45)
        raw_gz = self.read_raw_data(0x47)
        Gx = raw_gx / 131.0 - self.gyro_offsets[0]
        Gy = raw_gy / 131.0 - self.gyro_offsets[1]
        Gz = raw_gz / 131.0 - self.gyro_offsets[2]
        return Gx, Gy, Gz
