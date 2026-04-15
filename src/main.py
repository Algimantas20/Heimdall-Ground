import struct
import threading
import queue

from PacketFiles.Packet import Response, Telemetry
from PacketFiles.PacketHandler import PacketHandler
from SerialComm import SerialComm
from Logger import Logger

stop_event = threading.Event()

PORT = "COM9"
BAUD = 115200

HEADER = 0xABCD
HEADER_BYTES = struct.pack("<H", HEADER)

TELEMETRY_FORMAT = "<Ifffffffffff"

cmd_queue = queue.Queue()
print_queue = queue.Queue()
telemetry_queue = queue.Queue()


def input_thread():
    while not stop_event.is_set():
        cmd = input("> ").strip()
        if cmd:
            cmd_queue.put(cmd)
            
def command_thread(ser: SerialComm):
    while not stop_event.is_set():
        try:
            cmd = cmd_queue.get(timeout=0.5)

            ser.write((cmd + "\n").encode())
        except queue.Empty:
            continue

def printer_thread():
    while not stop_event.is_set():
        print(print_queue.get(), flush=True)

def serial_thread(ser: SerialComm, logger: Logger, handler: PacketHandler):
    while not stop_event.is_set():
        data = ser.read()

        packet: Telemetry | Response = handler.read_packet(data)

        if packet is None:
            continue

        if isinstance(packet, Telemetry):
            logger.log_dict(packet)
            telemetry_queue.put(packet)

        elif isinstance(packet, Response):
            print_queue.put(f"[RX] {packet.message}")

def main():
    ser = SerialComm(PORT, BAUD)
    logger = Logger("log.csv", "time_s,temp,bar,accX,accY,accZ,gyrX,gyrY,gyrZ,magX,magY,magZ")

    handler = PacketHandler(TELEMETRY_FORMAT, HEADER)

    try:
        threading.Thread(target=input_thread, daemon=True).start()
        threading.Thread(target=command_thread, args=(ser,), daemon=True).start()
        threading.Thread(target=printer_thread, daemon=True).start()

        serial_thread(ser, logger, handler)
    
    except KeyboardInterrupt:
        print("Stopping ...")
        stop_event.set()

    finally:
        ser.close()
        logger.close()


if __name__ == "__main__":
    main()