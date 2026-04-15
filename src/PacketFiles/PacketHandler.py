import struct
from PacketFiles.Packet import Packet, Response, Telemetry

class PacketHandler:
    MAX_PACKET_SIZE = 256

    def __init__(self, payload_format: str, header: int):
        self.packet = Packet(header, payload_format)
        self.buffer = bytearray()

        self.packet_types = {
            0x01: self._parse_telemetry,
            0x02: self._parse_response
        }

    def read_packet(self, data: bytes):
        self.buffer.extend(data)
        return self._parse_packet()

    def _parse_packet(self):
        header = self.packet.header_bytes
        header_len = self.packet.header_len

        idx = self.buffer.find(header)

        if idx == -1:
            return None

        if idx > 0:
            del self.buffer[:idx]

        if len(self.buffer) < header_len + 2:
            return None

        packet_type = self.buffer[header_len]
        length = self.buffer[header_len + 1]

        parser = self.packet_types.get(packet_type)
        if parser is None:
            del self.buffer[:1]
            return None

        if length > self.MAX_PACKET_SIZE:
            del self.buffer[:1]
            return None

        total_size = header_len + 2 + length

        if len(self.buffer) < total_size:
            return None

        payload = self.buffer[header_len + 2: total_size]

        try:
            result = parser(payload)
        except struct.error:
            del self.buffer[:1]
            return None

        del self.buffer[:total_size]

        return result
    
    def _parse_response(self, data: bytes):

        return Response(data.decode(errors="ignore").strip())

    def _parse_telemetry(self, data: bytes):
        if len(data) != self.packet.size:
            raise struct.error("Invalid telemetry size")

        unpacked = struct.unpack(self.packet.format, data)

        return Telemetry(
            time=unpacked[0] / 1000.0,
            temp=unpacked[1],
            bar=unpacked[2],
            acc=unpacked[3:6],
            gyr=unpacked[6:9],
            mag=unpacked[9:12],
        )