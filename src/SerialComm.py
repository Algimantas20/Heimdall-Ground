import serial
import struct

class SerialComm:
    def __init__(self, port: str, baud: int):
        self.ser = serial.Serial(port, baud, timeout=0)
        self.buffer = bytearray()

    def read_packet(self, header_bytes: bytes, size: int, parse_packet):
        header_len = len(header_bytes)

        data = self.ser.read(1024)

        if data:
            self.buffer.extend(data)

        packet = self._extract_packet(header_bytes, header_len, size, parse_packet)

        return packet
    
    def write(self, data: bytes):
        self.ser.write(data)
    
    def close(self):
        self.ser.close()

    def _extract_packet(self, header_bytes, header_len, size, parse_map):
        idx = self.buffer.find(header_bytes)

        if idx == -1:
            return None

        if idx > 0:
            self.buffer = self.buffer[idx:]

        # need header + type + len
        if len(self.buffer) < header_len + 2:
            return None

        packet_type = self.buffer[header_len]
        length = self.buffer[header_len + 1]

        parser = parse_map.get(packet_type)

        if parser is None:
            self.buffer = self.buffer[header_len + 2:]
            return None

        total_size = header_len + 2 + length

        if len(self.buffer) < total_size:
            return None

        start = header_len + 2
        end = start + length

        packet_bytes = self.buffer[start:end]

        try:
            packet = parser(packet_bytes)
        except struct.error:
            self.buffer = self.buffer[header_len + 1:]
            return None

        self.buffer = self.buffer[end:]
        return packet
