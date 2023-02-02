import time
import re

class heater:
    def __init__(self, usb_port):
        self.port = usb_port
    def data_format(self, temp_data):
        data = re.findall( r'\d+\.\d+', temp_data)
        return [float(data[0]), float(data[1])]
    
    def read(self):
        heat_meas = []
        for i in range(4):
            string = 'mon? {0}\r\n'.format(i)
            self.port.write(bytes(string, 'utf-8'))
            temp_data = self.port.readline().decode().strip()
            print(temp_data)
            heat_meas.append(self.data_format(temp_data))
            time.sleep(0.1)
        for i in range(1,6):
            string = 'lph? {0}\r\n'.format(i)
            self.port.write(bytes(string, 'utf-8'))
            temp_data = self.port.readline().decode().strip()
            heat_meas.append(temp_data)
            time.sleep(0.1)
        
        time.sleep(0.1)
        return [element for nestedlist in heat_meas for element in nestedlist]
    
    def write(self, channel, scale, LPH = False):
        if LPH == True:
            string = 'LPH {0} {1}\r\n'.format(channel, scale) #0-255 @ 4.5V supposed to be 5V...
            self.port.write(bytes(string, encoding='utf8'))
        elif LPH == False:
            if scale == 'r':
                string = 'reset {0}\r\n'.format(channel, scale)
                self.port.write(bytes(string, encoding='utf8'))
            elif channel == 'r':
                for i in range(4):
                    string = 'reset {0}\r\n'.format(i)
                    self.port.write(bytes(string, encoding='utf8'))
                    temp_data = self.port.readlines()
                return temp_data
            else:
                string = 'I {0} {1}\r\n'.format(channel, scale) #Easy scale 0-32 @ 200mV w/ 1ohm resistor
                self.port.write(bytes(string, encoding='utf8'))
        temp_data = self.port.readlines()
        return temp_data
