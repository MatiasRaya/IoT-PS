import pycom
import urequests
import time
import ujson
import connections

from sensors import Sensors
from pycoproc_1 import Pycoproc
from machine import Timer

# Global variable
iteration = 0
verification = 1

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
SERVER_ADDRESS = "http://192.168.1.153:5000" # LCD
# SERVER_ADDRESS = "https://matiasraya.pythonanywhere.com" # APP PYTHONANYWHERE

connections.wifi_connection()
# connections.lte_connection()
pycom.rgbled(YELLOW)
time.sleep(2)
pycom.rgbled(NO_COLOUR)

# Pytrack object and sensors
py = Pycoproc(Pycoproc.PYTRACK)
pySensor = Sensors(py)

data_sensor = {
    'nodo' : 1,
    'iteration' : iteration,
    'posLat' : pySensor.get_position().coordinates()[0],
    'posLon' : pySensor.get_position().coordinates()[1]
}

rate = {
    'transmission_rate' : 5,
    'sensor' : 1
}

# Chrono definition and inicialization
chrono = Timer.Chrono()

def transmission_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(transmission_handler, rate['transmission_rate'], periodic=True)
    send_recive()

def sensor_handler(alarm):
    alarm.cancel()
    alarm = Timer.Alarm(sensor_handler, rate['sensor'], periodic=True)
    position = pySensor.get_position().coordinates()
    data_sensor['posLat'] = position[0]
    data_sensor['posLon'] = position[1]
    data_sensor['iteration'] = iteration

chrono.start()

transmission_alarm = Timer.Alarm(transmission_handler, rate['transmission_rate'], periodic=True)
sensor_rate = Timer.Alarm(sensor_handler, rate['sensor'], periodic=True)

alarm_sets = []

alarm_sets.append([transmission_alarm, transmission_handler, 'transmission_rate'])
alarm_sets.append([sensor_rate, sensor_handler, 'sensor'])

def stored_data():
    store_data = {}
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

def get_rate(address):
    response = urequests.get(address)
    aux = response.json()
    rate['transmission_rate'] = aux['transmition']
    rate['sensor'] = aux['sensor']

def send_recive():
    global verification, iteration
    if verification == 1:
        try:
            response = get_iteration(SERVER_ADDRESS + "/iteration/" + str(data_sensor['nodo']))
        except Exception as e:
            print(e)
            print("ITERATION attempet failed.")
            pycom.rgbled(BLUE)
            time.sleep(1)
            pycom.rgbled(NO_COLOUR)
        verification = verification - 1


    try:
        response = get_rate(SERVER_ADDRESS + "/actualization/" + str(data_sensor['nodo']))
    except Exception as e:
        print(e)
        print("ACTUALIZATION attempet failed.")
        pycom.rgbled(CIAN)
        time.sleep(1)
        pycom.rgbled(NO_COLOUR)

    try:
        if data_sensor['posLat'] is not None:
            response = post_data(SERVER_ADDRESS + "/data", stored_data())
            iteration += 1
            print("Enviado")
    except Exception as e:
        print(e)
        print("POST attempet failed.")
        pycom.rgbled(RED)
        time.sleep(1)
        pycom.rgbled(NO_COLOUR)