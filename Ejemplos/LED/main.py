import time
import pycom

delay = 1

red = 0x7f0000
green = 0x007f00
blue = 0x00007f
yellow = 0x7f7f00
white = 0x7f7f7f
pink = 0x7f007f
cian = 0x007f7f
orange = 0xd35400
none= 0x000000

pycom.heartbeat(False)

for cycles in range(10):
    pycom.rgbled(red)
    time.sleep(delay)

    pycom.rgbled(green)
    time.sleep(delay)

    pycom.rgbled(blue)
    time.sleep(delay)

    pycom.rgbled(yellow)
    time.sleep(delay)

    pycom.rgbled(white)
    time.sleep(delay)

    pycom.rgbled(pink)
    time.sleep(delay)

    pycom.rgbled(cian)
    time.sleep(delay)

    pycom.rgbled(orange)
    time.sleep(delay)

    d = 16711935
    print(hex(d))
    pycom.rgbled(int(hex(d)))
    time.sleep(delay)
    pycom.rgbled(none)
    time.sleep(delay)