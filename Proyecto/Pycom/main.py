from network import WLAN
from sensors import Sensors
from pycoproc_1 import Pycoproc
from machine import Timer
from machine import RTC

import pycom
import machine

import urequests
import time
import ujson
from urequests import Response


SERVER_ADDRESS = "http://192.168.1.142" # LCD
# SERVER_ADDRESS = "http://192.168.0.13" # Casa
# SERVER_ADDRESS = "" # APP HEROKU
SERVER_PORT = "5000"

# Colors indicator led
RED = 0x7f0000
GREEN = 0x007f00
BLUE = 0x00007f
YELLOW = 0x7f7f00
WHITE = 0x7f7f7f
PINK = 0x7f007f
CIAN = 0x007f7f
ORANGE = 0xd35400
NO_COLOUR = 0x000000

pycom.heartbeat(False)

# WiFi connectation
wlan = WLAN(mode=WLAN.STA)
# wlan.connect('RAYA 2.4', auth=(WLAN.WPA2, 'Rayaplasencia1996'))
wlan.connect('LCD3', auth=(WLAN.WPA2, '1cdunc0rd0ba'))
print('Network found!')
while not wlan.isconnected():
    machine.idle()
print('WLAN connection succeeded!')
pycom.rgbled(YELLOW)
time.sleep(2)
pycom.rgbled(NO_COLOUR)

# Pysense object and sensors
py = Pycoproc(Pycoproc.PYSENSE)
pySensor = Sensors(py)

data_sensor = {
    'light' : pySensor.get_light(),
    'humidity' : pySensor.get_humidity(),
    'temperature' : pySensor.get_temperature(),
    'altitude' : pySensor.get_altitude()
}

rate = {
    'transmission_rate': 2,
    'light_rate': 1,
    'humidity_rate': 1,
    'temperature_rate': 1,
    'altitude_rate': 1
}

chrono = Timer.Chrono()

def transmission_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(transmission_handler, rate['transmission_rate'], periodic=True)

def light_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(light_handler, rate['light_rate'], periodic=True)
    data_sensor['light'] = pySensor.get_light()

def humidity_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(humidity_handler, rate['humidity_rate'], periodic=True)
    data_sensor['humidity'] = pySensor.get_humidity()

def temperature_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(temperature_handler, rate['temperature_rate'], periodic=True)
    data_sensor['temperature'] = pySensor.get_temperature()

def altitude_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(altitude_handler, rate['altitude_rate'], periodic=True)
    data_sensor['altitude'] = pySensor.get_altitude()

chrono.start()

transmission_alarm = Timer.Alarm(transmission_handler, rate['transmission_rate'], periodic=True)
light_rate = Timer.Alarm(light_handler, rate['light_rate'], periodic=True)
humidity_rate = Timer.Alarm(humidity_handler, rate['humidity_rate'], periodic=True)
temperature_rate = Timer.Alarm(temperature_handler, rate['temperature_rate'], periodic=True)
altitude_rate = Timer.Alarm(altitude_handler, rate['altitude_rate'], periodic=True)

alarm_sets = []

alarm_sets.append([transmission_alarm, transmission_handler, 'transmission_rate'])
alarm_sets.append([light_rate, light_handler, 'light_rate'])
alarm_sets.append([humidity_rate, humidity_handler, 'humidity_rate'])
alarm_sets.append([temperature_rate, temperature_handler, 'temperature_rate'])
alarm_sets.append([altitude_rate, altitude_handler, 'altitude_rate'])

def stored_data(samples, interval):
    store_data = {}
    time.sleep(interval)
    aux = dict()
    aux["ts"] = int(time.time())
    aux["values"] = data_sensor
    store_data = aux
    print(aux)
    print('\n------------------------------------------------------\n')
    print(store_data)
    print('\n------------------------------------------------------\n')
    json_store_data = ujson.dumps(store_data)
    return json_store_data

while True:
    stored_data(2,5)

# def post_method(address, raw_data):
#     response = urequests.post(address, data=raw_data)
#     return response


# count = 0

# while True:
#     # time.sleep(1)
#     try:
#         response = post_method(SERVER_ADDRESS + ":" + SERVER_PORT + "/tasks", stored_data())
#         # print(response.content)
#         # response.close()
#         pycom.rgbled(0x007f00)
#         count += 1
#         # time.sleep(2)
#         pycom.rgbled(0x7f007f)
#         # time.sleep(3)
#     except Exception as e:
#         print(e)
#         response = ''
#         print("POST attempet failed.")
#         pycom.rgbled(0x00007f)
#         time.sleep(2)
#     # time.sleep(1)
#     pycom.rgbled(0x4a007f)
#     print(count)