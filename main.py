import time
import utime
from machine import Pin
import urequests
import secrets
from boot import check_wifi_connection

api_url = secrets.api_url
api_ok = True

leds = {
    "led1": Pin(1, Pin.OUT),
    "led2": Pin(2, Pin.OUT),
    "led3": Pin(4, Pin.OUT),
    "led_s1": Pin(6, Pin.OUT),
    "led_s2": Pin(8, Pin.OUT),
    "led_s3": Pin(10, Pin.OUT)
}

buttons = {
    "button1": Pin(7, Pin.IN, Pin.PULL_UP),
    "button2": Pin(5, Pin.IN, Pin.PULL_UP),
    "button3": Pin(3, Pin.IN, Pin.PULL_UP),
    "sw1": Pin(12, Pin.IN, Pin.PULL_UP),
    "sw1b": Pin(13, Pin.IN, Pin.PULL_UP),
    "sw2": Pin(11, Pin.IN, Pin.PULL_UP),
    "sw2b": Pin(14, Pin.IN, Pin.PULL_UP),
    "sw3": Pin(9, Pin.IN, Pin.PULL_UP),
    "sw3b": Pin(15, Pin.IN, Pin.PULL_UP)
}


def button_callback(pin, button_name):
    if pin.value() == 0:
        try:
            response = urequests.post(api_url + '/button', json={"button": button_name})
            print(f"Wysłano żądanie do API z {button_name}: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"Błąd przy wysyłaniu żądania dla {button_name}: {e}")


def check_api_status():
    global api_ok
    try:
        response = urequests.get(api_url + '/led')
        if response.status_code == 200:
            data = response.json()
            for led_name, led_pin in leds.items():
                if data.get(f"{led_name}"):
                    led_pin.on()
                else:
                    led_pin.off()
            api_ok = True
        response.close()
    except Exception as e:
        print("Błąd przy odczytywaniu statusu z API:", e)
        api_ok = False


def api_unreachable():
    global api_ok
    l3 = leds["led3"]

    while not api_ok:
        print("API nieosiągalne, próba ponownego połączenia...")
        l3.on()
        time.sleep(1)
        l3.off()
        time.sleep(1)
        check_api_status()  # Ciągle sprawdzaj, czy API wróciło

    print("Połączenie z API przywrócone")


for button_name, button_pin in buttons.items():
    button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin, name=button_name: button_callback(pin, name))

while True:
    check_wifi_connection()

    if api_ok:
        check_api_status()
    else:
        api_unreachable()

    utime.sleep(2)
