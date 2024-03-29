import time
import pycom
from pycoproc_1 import Pycoproc
import machine

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white

py = Pycoproc(Pycoproc.PYSENSE)

pybytes_enabled = False
if 'pybytes' in globals():
    if(pybytes.isconnected()):
        print('Pybytes is connected, sending signals to Pybytes')
        pybytes_enabled = True

mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
print("MPL3115A2 temperature: " + str(mp.temperature()))
print("Altitude: " + str(mp.altitude()) + "m")
mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
print("Pressure: " + str(mpp.pressure()))

si = SI7006A20(py)
print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")
print("Dew point: "+ str(si.dew_point()) + " deg C")
t_ambient = 24.4
print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(si.humid_ambient(t_ambient)) + "%RH")


lt = LTR329ALS01(py)
print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))

li = LIS2HH12(py)
print("Acceleration: " + str(li.acceleration()))
print("Roll: " + str(li.roll()))
print("Pitch: " + str(li.pitch()))

# set your battery voltage limits here
vmax = 4.2
vmin = 3.3
battery_voltage = py.read_battery_voltage()
battery_percentage = (battery_voltage - vmin / (vmax - vmin))*100
print("Battery voltage: " + str(py.read_battery_voltage()), " percentage: ", battery_percentage)
if(pybytes_enabled):
    pybytes.send_signal(1, mpp.pressure())
    pybytes.send_signal(2, si.temperature())
    pybytes.send_signal(3, lt.light())
    pybytes.send_signal(4, li.acceleration())
    pybytes.send_battery_level(int(battery_percentage))
    print("Sent data to pybytes")

time.sleep(1)
py.setup_sleep(2)
py.go_to_sleep()