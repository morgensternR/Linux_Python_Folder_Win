import mcp3421 as mcp
import tca9548a as mux
from machine import I2C, Pin, SoftI2C
import time as time
import json
#import supervisor

def build_sensors():
    sensor_list = ['4 Pump A','3 Pump A','4 Switch A','3 Switch A','4 Pump B','3 Pump B','4 Switch B','3 Switch B','40K', '4K']
    mux_port_address = [0,1,2,3,4,5,6,7]
    slope_correction_16bit = [15971, 15987, 15971, 15975, 15979,15973,15973,15989, 15986, 15981]
    offset_correction = diode_offset = [10, 1, 8, 0, -9,-13,-4,3, 10, 6]
    sensors = {}
    for i in range(8):
        sensors[sensor_list[i]] = {'mux port': mux_port_address[i], 'slope': slope_correction_16bit[i], 'offset': offset_correction[i]}

    print(sensors)
    if 'i2c' not in locals():
        i2c = None

    

    return sensors

def getT(sensors):
    results = {}
    for key in sensors:
        results[key] = sensors[key]['adc'].singleT()
    return results

def getBoardT(sensors):
    results = {}
    for key in sensors:
        results[key] = sensors[key]['adc'].readBoardTemp()
    return results

sensors = build_sensors()
def g():
    print('got g')

commands = {
    'getT?'.upper(): getT,
    'getBoardT?'.upper(): getBoardT,
    }


