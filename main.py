# main.py
import utime
from machine import Pin
import urequests
import secrets

api_url = secrets.api_url

leds = {
    # duże, do funkcji
    "led1": Pin(1, Pin.OUT), # GPIO 4
    "led2": Pin(2, Pin.OUT), # GPIO 2
    "led3": Pin(4, Pin.OUT), # GPIO 1

    # małe, do statusu pc
    "led_s1": Pin(6, Pin.OUT), # GPIO 6
    "led_s2": Pin(8, Pin.OUT), # GPIO 8
    "led_s3": Pin(10, Pin.OUT) # GPIO 10
}

buttons = {
    # duże, do funkcji
    "button1": Pin(7, Pin.IN, Pin.PULL_UP), # GPIO 7
    "button2": Pin(5, Pin.IN, Pin.PULL_UP), # GPIO 5
    "button3": Pin(3, Pin.IN, Pin.PULL_UP), # GPIO 3

    # małe, do pc
    "sw1": Pin(12, Pin.IN, Pin.PULL_UP), # GPIO 12
    "sw2": Pin(11, Pin.IN, Pin.PULL_UP), # GPIO 11
    "sw3": Pin(9, Pin.IN, Pin.PULL_UP) # GPIO 9
}

def button_callback(pin, button_name):
    if pin.value() == 0:
        try:
            response = urequests.post(api_url+'/button', json={"button": button_name})
            print(f"Wysłano żądanie do API z {button_name}: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"Błąd przy wysyłaniu żądania dla {button_name}: {e}")

def check_api_status():
    try:
        response = urequests.get(api_url+'/led')
        if response.status_code == 200:
            data = response.json()
            for led_name, led_pin in leds.items():
                if data.get(f"{led_name}"):
                    led_pin.on()
                else:
                    led_pin.off()
        response.close()
    except Exception as e:
        print("Błąd przy odczytywaniu statusu z API:", e)


for button_name, button_pin in buttons.items():
    button_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin, name=button_name: button_callback(pin, name))


while True:
    check_api_status()
    utime.sleep(5)