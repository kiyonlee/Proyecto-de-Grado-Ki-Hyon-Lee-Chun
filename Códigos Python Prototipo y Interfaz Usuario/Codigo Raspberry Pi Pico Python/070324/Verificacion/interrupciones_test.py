import machine
import utime

led_pin = machine.Pin(25, machine.Pin.OUT)
timer0 = machine.Timer()

def blink_led(timer):
    led_pin.toggle()

timer0.init(mode=machine.Timer.PERIODIC, period=1000, callback=blink_led)

while True:
    utime.sleep(1)
