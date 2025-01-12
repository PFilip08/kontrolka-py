import utime
from machine import Pin
import urequests
import secrets
from boot import check_wifi_connection, ota_update
import _thread

api_url = secrets.api_url
api_ok = True
debounce_time = 200  # milliseconds
long_press_time = 2500  # milliseconds
last_button_press = {}
button_press_start = {}
stop_blinking = False

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


def button_callback(pin):
    button_name = [name for name, p in buttons.items() if p == pin][0]
    current_time = utime.ticks_ms()
    if pin.value() == 0:
        button_press_start[button_name] = current_time
    else:
        if button_name in button_press_start:
            press_duration = utime.ticks_diff(current_time, button_press_start[button_name])
            if press_duration > long_press_time:
                handle_long_press(button_name)
            else:
                handle_short_press(button_name)
            del button_press_start[button_name]

def handle_short_press(button_name):
    try:
        response = urequests.post(api_url + '/button', json={"button": button_name}, timeout=5)
        print(f"Wysłano żądanie do API z {button_name}: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Błąd przy wysyłaniu żądania dla {button_name}: {e}")

def handle_long_press(button_name):
    long_button_name = f"{button_name}_long"
    print(f"Trzymanie przycisku: {button_name}")
    try:
        response = urequests.post(api_url + '/button', json={"button": long_button_name}, timeout=5)
        print(f"Wysłano żądanie do API z {long_button_name}: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Błąd przy wysyłaniu żądania dla {long_button_name}: {e}")

def check_api_status():
    global api_ok, stop_blinking
    try:
        response = urequests.get(api_url + '/led', timeout=5)
        if response.status_code == 200:
            data = response.json()
            for led_name, led_pin in leds.items():
                if data.get(f"{led_name}"):
                    led_pin.on()
                else:
                    led_pin.off()
            api_ok = True
            stop_blinking = True
        else:
            raise Exception(f"Nieprawidłowy status odpowiedzi z API: {response.status_code}")
        response.close()
    except Exception as e:
        print("Błąd przy odczytywaniu statusu z API:", e)
        api_ok = False

def blink_led(led_pin):
    global stop_blinking
    while not api_ok and not stop_blinking:
        led_pin.on()
        utime.sleep(1)
        led_pin.off()
        utime.sleep(1)

def api_unreachable():
    global api_ok, stop_blinking
    stop_blinking = False
    for led_pin in leds.values():
        led_pin.off()
    led_pin = leds["led3"]
    _thread.start_new_thread(blink_led, (led_pin,))

    while not api_ok:
        print("API nieosiągalne, próba ponownego połączenia...")
        check_api_status()

    print("Połączenie z API przywrócone")

def periodic_ota_update():
    while True:
        print("Sprawdzanie aktualizacji OTA...")
        ota_update()
        utime.sleep(30)

for button_name, button_pin in buttons.items():
    button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_callback)

_thread.start_new_thread(periodic_ota_update, ())

while True:
    check_wifi_connection()

    if api_ok:
        check_api_status()
    else:
        api_unreachable()

    utime.sleep(10)
