# boot.py - - runs on boot-up
import network

ssid = ''
passwd = ''

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, passwd)

while station.isconnected() == False:
    pass

print('Polaczono')
print(station.ifconfig())