# boot.py - - runs on boot-up
import uota
import machine
import secrets

ssid = secrets.ssid
passwd = secrets.passwd

def do_connect():
    import network
    network.country("PL")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    # wlan.config(txpower=5)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, passwd)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

do_connect()

if do_ota_update and uota.check_for_updates():
      uota.install_new_firmware()
      machine.reset()