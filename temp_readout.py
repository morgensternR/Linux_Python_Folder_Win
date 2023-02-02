

import serial
import time
from datetime import datetime 
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.interpolate import interp1d
import zmq
import ujson
import heater_class as h
import diode_class as d
import lockin_class as l

heater_port = serial.Serial('/dev/heaters', timeout = 1 )
diode_port = serial.Serial('/dev/ttyACM0', timeout = 1 )
lockin_port =serial.Serial('/dev/lockins', timeout = 1 )

dt670 = np.loadtxt('DT670.csv', delimiter =',', dtype=float)
DC2018 = np.loadtxt('DC2018.csv', delimiter =',', dtype=float)
ROX6951 = np.loadtxt('ROX6951.csv', delimiter =',', dtype=float)

dt670_func = interp1d(dt670[:,1], dt670[:,0])
dc2018_func = interp1d(DC2018[:,1], DC2018[:,0])
rox6951_func = interp1d(ROX6951[:,1], ROX6951[:,0])

daq = zmq.Context()
daq_socket = daq.socket(zmq.REP)
daq_socket.bind("tcp://*:5555")



lockin_object = l.lockin(lockin_port)
diode_object = d.diode(diode_port)
heater_object = h.heater(heater_port)

#%%
while True:

    message = daq_socket.recv()
    check = False
    if message == b'read all':
        check = True
        diode_data = diode_object.read()
        heater_data = heater_object.read()
        lockin_data = lockin_object.read_all()
        daq_socket.send_json(ujson.dumps( diode_data + heater_data + lockin_data ))
    message = message.split()
    print(message)
    if (message[0].lower() == b'read' and len(message[1]) > 3):
        check = True
        if message[1].lower() == b'diode':
            
            daq_socket.send_json(ujson.dumps( diode_object.read() ))
            
        elif message[1].lower() == b'heater':
            
            daq_socket.send_json(ujson.dumps( heater_object.read() ))
            
        elif message[1].lower() == b'lockin':
            if len(message) > 2:
            
                daq_socket.send_json(ujson.dumps( lockin_object.read(message[2].decode(), message[3].decode() ) ))
            else:
                daq_socket.send_json(ujson.dumps( lockin_object.read_all() ))
        else:
            daq_socket.send_json(b'bad command') 
      
    #Heater Write      
    if message[0].lower() == b'lph':
        check = True
        heater_object.write(int(message[1]), int(message[2]), True)
        daq_socket.send_json(bytes('Setting LPH {0} {1}\r\n'.format(message[1], message[2]), encoding = 'utf-8'))
    if message[0].lower() == b'reset':
        check = True
        if type(message[1]) == int:
            heater_object.write(int(message[1]),'r' ,False)
            daq_socket.send_json(bytes('resetting HP {0}\r\n'.format(message[1]), encoding = 'utf-8'))
        elif message[1].lower() == b'all':
            heater_object.write('r', None, False)
            daq_socket.send_json(bytes('resetting All Hps', encoding = 'utf-8'))
    if message[0].lower() == b'i':
        check = True
        heater_object.write(int(message[1]), int(message[2]), False)
        daq_socket.send_json(bytes('Setting I {0} {1}\r\n'.format(message[1], message[2]), encoding = 'utf-8'))

    
    #Lockin Write
    if message[0].lower() == b'bias':
        check = True
        bias_state = lockin_object.write(int(message[1]))
        print(bytes('Bias {0} {1}\r\n'.format(message[1], bias_state), encoding = 'utf-8'))
        daq_socket.send_json(bytes('Bias {0} {1}\r\n'.format(message[1], bias_state), encoding = 'utf-8'))
    #if check == False:
        #daq_socket.send_json(b'bad command') 
        #these arn't in elif statments so this would run at the very end and attempt sending 
        #information when there was anever a request.....but if there's an error in the command sent, 
        #the server will break bc overall nothing is sent back when requested
            

#%%
#Test PRogram to write into file
import zmq
import numpy as np 
import ujson
from datetime import datetime, date
import time

Logger = zmq.Context()

#  Socket to talk to server
logging_socket = Logger.socket(zmq.REQ)
logging_socket.connect("tcp://localhost:5555")        
def send_n(message):    
    logging_socket.send(bytes(message))
    return logging_socket.recv_json()

#Start new file when logger is started
header = f'{"Time"},{"4 Pump A"},{"3 Pump A"},{"4 Switch A"},{"3 Switch A"},{"4 Pump B"},{"3 Pump B"},{"4 Switch B"},{"3 Switch B"},{"40K Diode"},{"4K Diode"} \n'

'''
file = open("thermometry_log_{0}.csv".format(date.today(), encoding = 'utf-8'), "r")
#Need a check to see if the file exists... Waht if I start the logging server twice in 1 day... 
if file.readline() != header:
    print("no header ")
    file = open("thermometry_log_{0}.csv".format(date.today(), encoding = 'utf-8'), "w")
    file.write(header)
    file.flush()

file = open("thermometry_log_{0}.csv".format(date.today(), encoding = 'utf-8'), "a")
'''

file = open("thermometry_log_{0}.csv".format(date.today(), encoding = 'utf-8'), "w")
file.write(header)
file.flush()
file = open("thermometry_log_{0}.csv".format(date.today(), encoding = 'utf-8'), "a")


while True:

    data = ujson.loads(send_n(b'read diode'))
    header = f'{time.time()},{data[0]},{data[1]},{data[2]},{data[3]},{data[4]},{data[5]},{data[6]},{data[7]},{data[8]},{data[9]} \n'

        
    #print(header)
    file.write(header)
    file.flush()
    time.sleep(10)

#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from scipy.interpolate import interp1d
#import pandas as pd
#df = pd.read_csv("thermometry_log_2023-01-24.csv")
file = np.loadtxt("thermometry_log_2023-01-26.csv", delimiter=",", dtype = float, skiprows = 1)
dt670 = np.loadtxt('DT670.csv', delimiter =',', dtype=float)
DC2018 = np.loadtxt('DC2018.csv', delimiter =',', dtype=float)
ROX6951 = np.loadtxt('ROX6951.csv', delimiter =',', dtype=float)

dt670_func = interp1d(dt670[:,1], dt670[:,0])
dc2018_func = interp1d(DC2018[:,1], DC2018[:,0])
rox6951_func = interp1d(ROX6951[:,1], ROX6951[:,0])
#data_list = np.array([dt670_func(i) for i in file])
#%%
header = ["4 Pump A","3 Pump A","4 Switch A","3 Switch A","4 Pump B","3 Pump B","4 Switch B","3 Switch B","40K Diode","4K Diode"]

time_list = []
secs = mdate.epoch2num(file[:,0])
fig, ax = plt.subplots()

# Plot the date using plot_date rather than plot
for i in range(1,file.shape[1]):
    if i == 9 or i == 10:
        ax.plot_date(secs, dt670_func(file[:,i]), label = header[i-1])
    else:
        ax.plot_date(secs, dc2018_func(file[:,i]), label = header[i-1])
plt.legend()

# Choose your xtick format string
date_fmt = '%d-%m-%y %H:%M:%S'

# Use a DateFormatter to set the data to the correct format.
date_formatter = mdate.DateFormatter(date_fmt)
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

plt.show()
   #%% 
for i in range(1,file.shape[1]):
    plt.plot(time_list, file[:,i], label = header[i-1])
plt.legend()
plt.show()

#%%v
import numpy

def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype = str(A.dtype),
        shape = A.shape,
    )
    socket.send_json(md, flags|zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)

def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = buffer(msg)
    A = numpy.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])

#%%

import sys
import glob
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):'
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    print(serial_ports())

#%%
    
#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")
#%%
#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")


socket.send(b"Hello000")

