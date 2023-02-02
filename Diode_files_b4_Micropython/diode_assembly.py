import mcp3421 as mcp
import tca9548a as mux
from machine import I2C, Pin, SoftI2C
import time as time

i2c = I2C(1, scl=Pin(23), sda=Pin(22))
i2c_40k = SoftI2C(scl = Pin(28), sda = Pin(29))
i2c_4k = SoftI2C(scl = Pin(20), sda = Pin(5))
diode_slope = [15971, 15987, 15971, 15975, 15979,15973,15973,15989, 15986, 15981]
diode_offset = [10, 1, 8, 0, -9,-13,-4,3, 10, 6]
diode_list = [0,0,0,0,0,0,0,0, 0, 0]

i2c_mux = mux.TCA9548A(i2c)
#[ina333_1, ina333_2, ina333_, 3, ina333_4, ina826_1, ina826_2, ina826_3, ina826_4, ina333_5, ina826_5]

for i in range(8):
    i2c_mux.write_reg(i)
    diode_list[i] = mcp.MCP3421(i2c, slope = diode_slope[i], offset = diode_offset[i], sampling = 2)
    diode_list[i].set_config()

#IN333 board 5
diode_list[8] = mcp.MCP3421(i2c_40k, slope = diode_slope[8], offset = diode_offset[8])
#INA826 Board 5
diode_list[9] = mcp.MCP3421(i2c_4k, slope = diode_slope[9], offset = diode_offset[9])
def read(i):
    i2c_mux.write_reg(i)
    return(diode_list[i].read_adc_v())

while True:
    print(read(0), read(1), read(2), read(3), read(4), read(5), read(6), read(7), diode_list[8].read_adc_v(), diode_list[9].read_adc_v())
    #time.sleep(0.1)