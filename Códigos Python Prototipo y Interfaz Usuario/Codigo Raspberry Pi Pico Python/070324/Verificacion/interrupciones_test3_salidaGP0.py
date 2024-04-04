import machine
import utime

led_pin = machine.Pin(25, machine.Pin.OUT)
gp0_pin = machine.Pin(3, machine.Pin.OUT)  # Pin GP3

timer0 = machine.Timer()

def blink_led(timer):
    led_pin.toggle()
    gp0_pin.value(not gp0_pin.value())  # Invertir el estado de GP0

timer0.init(mode=machine.Timer.PERIODIC, period=10, callback=blink_led)

while True:
    utime.sleep(1)
