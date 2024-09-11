# boot.py - - runs on boot-up
import time
import uota
import machine
import secrets
import network

ssid = secrets.ssid
passwd = secrets.passwd
do_ota_update = secrets.do_ota_update

wlan = network.WLAN(network.STA_IF)

def do_connect():
    network.country("PL")
    wlan.active(False)
    wlan.active(True)
    # wlan.config(txpower=5)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, passwd)
        while not wlan.isconnected():
            l1 = machine.Pin(1, machine.Pin.OUT)
            l2 = machine.Pin(2, machine.Pin.OUT)
            l3 = machine.Pin(4, machine.Pin.OUT)
            l1.off()
            l2.off()
            l3.off()
            l1.on()
            time.sleep(1)
            l2.on()
            time.sleep(1)
            l3.on()
            time.sleep(1)
            l1.off()
            l2.off()
            l3.off()
            time.sleep(1)
            pass
    print('network config:', wlan.ifconfig())

def check_wifi_connection():
    if not wlan.isconnected():
        print('Wi-Fi disconnected, trying to reconnect...')
        do_connect()

do_connect()

try:
    if do_ota_update and uota.check_for_updates():
        led = machine.Pin(1, machine.Pin.OUT)
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
        led.on()
        time.sleep(0.5)
        led.off()
        print('Updating uota...')
        uota.install_new_firmware()
        machine.reset()
    else: print('no update');
except Exception as e:
        print("Błąd przy łączeniu z serwerem OTA:", e)


import webrepl
webrepl.start()