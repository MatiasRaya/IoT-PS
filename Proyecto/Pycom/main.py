import pycom
import machine
import urequests
import time
import ujson

from network import WLAN
from sensors import Sensors
from pycoproc_1 import Pycoproc
from machine import Timer, RTC
from urequests import Response

# Global variable
iteration = 0
verification = 1
year = 0
month = 0
day = 0

# Colors indicator led
RED = 0x7f0000
GREEN = 0x007f00
BLUE = 0x00007f
YELLOW = 0x7f7f00
WHITE = 0x7f7f7f
PINK = 0x7f007f
CIAN = 0x007f7f
NO_COLOUR = 0x000000

pycom.heartbeat(False)

pycom.rgbled(GREEN)
time.sleep(5)
pycom.rgbled(NO_COLOUR)

# WiFi connectation
SERVER_ADDRESS = "http://192.168.1.142" # LCD
# SERVER_ADDRESS = "" # APP HEROKU
SERVER_PORT = "5000"

wlan = WLAN(mode=WLAN.STA)
wlan.connect('LCD', auth=(WLAN.WPA2, '1cdunc0rd0ba'))
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
    'nodo' : 1,
    'iteration' : iteration,
    'year' : year,
    'month' : month,
    'day' : day,
    'lightB' : pySensor.get_light()[0],
    'lightR' : pySensor.get_light()[1],
    'humidity' : pySensor.get_humidity(),
    'temperature' : pySensor.get_temperature(),
    'pressure' :pySensor.get_pressure()
}

rate = {
    'transmission_rate': 5,
    'light_rate': 1,
    'humidity_rate': 1,
    'temperature_rate': 1,
    'pressure_rate': 1
}

# Chrono definition and inicialization
chrono = Timer.Chrono()

def transmission_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(transmission_handler, rate['transmission_rate'], periodic=True)
    send_recive()

def light_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(light_handler, rate['light_rate'], periodic=True)
    light = pySensor.get_light()
    data_sensor['lightB'] = light[0]
    data_sensor['lightR'] = light[1]

def humidity_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(humidity_handler, rate['humidity_rate'], periodic=True)
    data_sensor['humidity'] = pySensor.get_humidity()

def temperature_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(temperature_handler, rate['temperature_rate'], periodic=True)
    data_sensor['temperature'] = pySensor.get_temperature()

def pressure_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(pressure_handler, rate['pressure_rate'], periodic=True)
    data_sensor['pressure'] = pySensor.get_pressure()

chrono.start()

transmission_alarm = Timer.Alarm(transmission_handler, rate['transmission_rate'], periodic=True)
light_rate = Timer.Alarm(light_handler, rate['light_rate'], periodic=True)
humidity_rate = Timer.Alarm(humidity_handler, rate['humidity_rate'], periodic=True)
temperature_rate = Timer.Alarm(temperature_handler, rate['temperature_rate'], periodic=True)
pressure_rate = Timer.Alarm(pressure_handler, rate['pressure_rate'], periodic=True)

alarm_sets = []

alarm_sets.append([transmission_alarm, transmission_handler, 'transmission_rate'])
alarm_sets.append([light_rate, light_handler, 'light_rate'])
alarm_sets.append([humidity_rate, humidity_handler, 'humidity_rate'])
alarm_sets.append([temperature_rate, temperature_handler, 'temperature_rate'])
alarm_sets.append([pressure_rate, pressure_handler, 'pressure_rate'])

def stored_data():
    store_data = {}
    data_sensor['iteration'] = iteration
    data_sensor['year'] = year
    data_sensor['month'] = month
    data_sensor['day'] = day
    store_data = data_sensor
    json_store_data = ujson.dumps(store_data)
    return json_store_data

def post_data(address, raw_data):
    response = urequests.post(address, data=raw_data)
    return response

def get_iteration(address):
    global iteration
    response = urequests.get(address)
    aux = response.json()
    if iteration <= aux['iteration']:
        iteration = aux['iteration'] + 1
    return response

def get_time(address):
    global year, month, day
    response = urequests.get(address)
    aux = response.json()
    year = aux['year']
    month = aux['month']
    day = aux['day']
    return response

def get_rate(address):
    response = urequests.get(address)
    aux = response.json()
    rate['transmission_rate'] = aux['transmition']
    rate['humidity_rate'] = aux['sensor']
    rate['light_rate'] = aux['sensor']
    rate['pressure_rate'] = aux['sensor']
    rate['temperature_rate'] = aux['sensor']

def send_recive():
    global verification, iteration
    if verification == 1:
        try:
            response = get_iteration(SERVER_ADDRESS + ":" + SERVER_PORT + "/iteration/" + str(data_sensor['nodo']))
        except Exception as e:
            print(e)
            pycom.rgbled(BLUE)
            time.sleep(1)
            pycom.rgbled(NO_COLOUR)
        verification = verification - 1

    try:
        response = get_rate(SERVER_ADDRESS + ":" + SERVER_PORT + "/actualization/" + str(data_sensor['nodo']))
    except Exception as e:
        print(e)
        pycom.rgbled(CIAN)
        time.sleep(1)
        pycom.rgbled(NO_COLOUR)

    try:
        response = get_time(SERVER_ADDRESS + ":" + SERVER_PORT + "/time")
    except Exception as e:
        print(e)
        pycom.rgbled(PINK)
        time.sleep(1)
        pycom.rgbled(NO_COLOUR)

    try:
        response = post_data(SERVER_ADDRESS + ":" + SERVER_PORT + "/data", stored_data())
        iteration += 1
    except Exception as e:
        print(e)
        print("POST attempet failed.")
        pycom.rgbled(RED)
        time.sleep(1)
        pycom.rgbled(NO_COLOUR)