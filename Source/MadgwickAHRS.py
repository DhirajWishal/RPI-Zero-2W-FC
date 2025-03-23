import numpy as np


class MadgwickAHRS:
    def __init__(self, beta=0.1):
        self.beta = beta
        self.q = np.array([1.0, 0.0, 0.0, 0.0])  # initial quaternion

    def updateIMU(self, gx, gy, gz, ax, ay, az, dt):
        # Convert gyroscope readings from degrees/sec to radians/sec
        gyro = np.radians(np.array([gx, gy, gz]))
        # Normalize accelerometer measurement
        accel = np.array([ax, ay, az])
        norm_acc = np.linalg.norm(accel)
        if norm_acc == 0:
            return  # avoid division by zero
        accel = accel / norm_acc

        q = self.q
        q1, q2, q3, q4 = q

        # Auxiliary variables to reduce repeated calculations
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4
        _4q1 = 4.0 * q1
        _4q2 = 4.0 * q2
        _4q3 = 4.0 * q3
        _8q2 = 8.0 * q2
        _8q3 = 8.0 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4

        # Gradient descent algorithm corrective step
        s1 = _4q1 * q3q3 + _2q3 * accel[0] + _4q1 * q2q2 - _2q2 * accel[1]
        s2 = _4q2 * q4q4 - _2q4 * accel[0] + 4.0 * q1q1 * q2 - _2q1 * \
            accel[1] - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * accel[2]
        s3 = 4.0 * q1q1 * q3 + _2q1 * accel[0] + _4q3 * q4q4 - _2q4 * \
            accel[1] - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * accel[2]
        s4 = 4.0 * q2q2 * q4 - _2q2 * \
            accel[0] + 4.0 * q3q3 * q4 - _2q3 * accel[1]
        s = np.array([s1, s2, s3, s4])
        norm_s = np.linalg.norm(s)
        if norm_s == 0:
            return
        s = s / norm_s

        # Compute rate of change of quaternion
        qDot = 0.5 * np.array([
            -q2 * gyro[0] - q3 * gyro[1] - q4 * gyro[2],
            q1 * gyro[0] + q3 * gyro[2] - q4 * gyro[1],
            q1 * gyro[1] - q2 * gyro[2] + q4 * gyro[0],
            q1 * gyro[2] + q2 * gyro[1] - q3 * gyro[0]
        ]) - self.beta * s

        # Integrate to yield new quaternion using the measured dt
        q = q + qDot * dt
        # Normalize quaternion
        self.q = q / np.linalg.norm(q)

    def getEulerAngles(self):
        q = self.q
        q1, q2, q3, q4 = q
        roll = np.arctan2(2*(q1*q2 + q3*q4), 1 - 2*(q2*q2 + q3*q3))
        pitch = np.arcsin(2*(q1*q3 - q4*q2))
        yaw = np.arctan2(2*(q1*q4 + q2*q3), 1 - 2*(q3*q3 + q4*q4))
        return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)
