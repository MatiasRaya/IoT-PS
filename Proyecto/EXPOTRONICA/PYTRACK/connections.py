import machine
import time

from network import WLAN, LTE, Bluetooth

def wifi_connection():
    wlan = WLAN(mode=WLAN.STA)
    wlan.antenna(WLAN.EXT_ANT)
    nets = wlan.scan()
    for net in nets:
        if net.ssid == "LCD":
            print('Network found!')
            break
    wlan.connect('LCD', auth=(WLAN.WPA2, '1cdunc0rd0ba'))
    while not wlan.isconnected():
        machine.idle()
    print('WLAN connection succeeded!')

def lte_connection():
    lte = LTE()
    # lte.attach(band=28, apn="datos.personal.com")
    lte.attach(band=28, apn="igprs.claro.com.ar")
    while not lte.isattached():
        time.sleep(0.25)
    lte.connect()
    while not lte.isconnected():
        time.sleep(0.25)
    print('LTE connection succeeded!')

def bluetooth_connection():
    bt = Bluetooth()
    bt.init(antenna=bt.EXT_ANT)
    bt.start_scan(-1)
    aux=bt.get_adv()
    return aux