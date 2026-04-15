import struct


class Packet:
    def __init__(self, header: int, payload_format: str):
        self.header = header
        self.header_bytes = struct.pack("<H", header)
        self.header_len = len(self.header_bytes)

        self.format = payload_format
        self.size = struct.calcsize(payload_format)