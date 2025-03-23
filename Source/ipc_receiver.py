import socket
import threading
import sys


class IPCReceiver(threading.Thread):
    def __init__(self, host='0.0.0.0', port=5005):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.daemon = True
        self.control_inputs = {'throttle': 0, 'roll': 0, 'pitch': 0, 'yaw': 0}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((self.host, self.port))
        except Exception as e:
            print("Error: Unable to bind UDP socket on port",
                  self.port, "Exception:", e)
            sys.exit(1)

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            try:
                decoded = data.decode('utf-8').strip()
                parts = decoded.split(',')
                if len(parts) == 4:
                    self.control_inputs['throttle'] = float(parts[0])
                    self.control_inputs['roll'] = float(parts[1])
                    self.control_inputs['pitch'] = float(parts[2])
                    self.control_inputs['yaw'] = float(parts[3])
            except Exception as e:
                print("Error parsing IPC data:", e)
