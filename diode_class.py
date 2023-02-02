import re
class diode:
    def __init__(self, usb_port):
        self.port = usb_port
    def read(self):
        diode_data = self.port.readline().decode().strip()
        return re.findall( r'\d+\.*\d*', diode_data)

