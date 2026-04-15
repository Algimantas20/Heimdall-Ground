import serial

class SerialComm:
    def __init__(self, port: str, baud: int):
        self.ser = serial.Serial(port, baud, timeout=0)
        self.buffer = bytearray()

    def read(self):
        return self.ser.read(1024)

    def write(self, data: bytes):
        self.ser.write(data)

    def close(self):
        self.ser.close()