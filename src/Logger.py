import csv
import os

class Logger:
    def __init__(self, log_file: str, header: str = None):
        self.log_file = log_file

        self.file = open(log_file, "a", newline="", buffering=1)
        self.writer = csv.writer(self.file)

        if header:
            self._write_header(header)

    def _write_header(self, header: str):
        if os.stat(self.log_file).st_size == 0:
            self.writer.writerow(header.split(","))

    def log_dict(self, packet: dict):
        self.writer.writerow([
            packet["time"],
            packet["temp"],
            packet["bar"],
            *packet["acc"],
            *packet["gyr"],
            *packet["mag"],
        ])

    def log(self, message: str):
        self.file.write(message + "\n")

    def close(self):
        self.file.close()