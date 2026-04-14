import struct
import threading
import queue
import utility

from Logger import Logger
from SerialComm import SerialComm

# ---------------- CONFIG ----------------
PORT = "COM9"
BAUD = 115200

HEADER = 0xABCD
HEADER_BYTES = struct.pack("<H", HEADER)

TELEMETRY_FORMAT = "<Ifffffffffff"
TELEMETRY_SIZE = struct.calcsize(TELEMETRY_FORMAT)

csv_header = "time_s,temp,bar,accX,accY,accZ,gyrX,gyrY,gyrZ,magX,magY,magZ"
# ----------------------------------------

cmd_queue = queue.Queue()
print_queue = queue.Queue()

# -------- Parsers --------

def parse_telemetry(data: bytes):
    unpacked = struct.unpack(TELEMETRY_FORMAT, data)

    return {
        "type": "telemetry",
        "time": unpacked[0] / 1000.0,
        "temp": unpacked[1],
        "bar": unpacked[2],
        "acc": unpacked[3:6],
        "gyr": unpacked[6:9],
        "mag": unpacked[9:12],
    }


def parse_response(data: bytes):
    return {
        "type": "response",
        "msg": data.decode(errors="ignore").strip()
    }


PACKET_TYPES = {
    0x01: parse_telemetry,
    0x02: parse_response
}

# -------- Threads --------

def input_thread():
    while True:
        cmd = input("> ").strip()
        if cmd:
            cmd_queue.put(cmd)


def printer_thread():
    while True:
        msg = print_queue.get()
        print(msg, flush=True)


@utility.time_function
def serial_loop(ser, logger):
    while True:
        packet = ser.read_packet(HEADER_BYTES, TELEMETRY_SIZE, PACKET_TYPES)

        if packet is None:
            continue

        if packet["type"] == "telemetry":
            logger.log_dict(packet)
        else:
            print_queue.put(f"[RX] {packet['msg']}")


def command_loop(ser):
    while True:
        cmd = cmd_queue.get()
        data = (cmd + "\n").encode("utf-8")
        ser.write(data)

# -------- Main --------

def main():
    ser = SerialComm(PORT, BAUD)
    logger = Logger("log.csv", csv_header)

    try:
        threading.Thread(target=input_thread, daemon=True).start()
        threading.Thread(target=command_loop, args=(ser,), daemon=True).start()
        threading.Thread(target=printer_thread, daemon=True).start()

        serial_loop(ser, logger)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        ser.close()
        logger.close()


if __name__ == "__main__":
    main()