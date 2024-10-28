from PyQt5.QtCore import pyqtSignal, QThread

# from PyQt5.QtCore import Qt
from src.ultilities import LogEvent
import serial
from datetime import datetime


class Serial_Thread(QThread):
    data_received = pyqtSignal(bytes)
    error_signal = pyqtSignal()

    def __init__(self, port, baudrate, timeout=0.009):
        super(Serial_Thread, self).__init__()
        self.is_running = False
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def connect_serial(self):
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            self.is_running = True
        except Exception as E:
            print(f"Connect Serial {self.port} Error")

    def send_signal_serial_port(self, data: str):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(data.strip())

    def run(self):
        try:
            self.connect_serial()
            while self.is_running:
                if self.serial_port and self.serial_port.is_open:
                    data_plc = self.serial_port.readline()
                    if len(data_plc) > 0:
                        self.data_received.emit(data_plc)
        except Exception as E:
            self.error_signal.emit()

            now = datetime.now()
            timeLog = now.strftime("%d/%m/%Y %H:%M:%S")
            LogEvent(
                "["
                + timeLog
                + "] --- "
                + f"Connect Serial {self.port} Error"
                + " ---> "
                + "ERROR",
                "DT",
                "info",
            )

    def stop(self):
        self.is_running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
