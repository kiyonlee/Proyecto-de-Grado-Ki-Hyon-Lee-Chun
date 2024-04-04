from machine import Pin, Timer, ADC
from utime import sleep_ms
from ssd1306 import SSD1306_I2C
import base as bs
# import presentacion
# import random
# import etapa1


# Constants
TEMP_REF_INCREMENT = 0.01  # Increment value for the temperature reference
COUNT_SPEED = 100  # Increase for slower counting
DEBOUNCE_TIME_MS = 10
TEMP_SENSOR_SCALE = 127.8255586
TEMP_SENSOR_OFFSET = -274.75
REF_SCALE = (70 / 3.3)

# Pin configuration
GP0_PIN = Pin(13, Pin.OUT)

# Variables
temp_ref = 25.1
count_counter = 0
state = 0
average_sensor = 0
average_ref = 0

# Timer initialization
timer0 = Timer()

def timer_10ms_callback(timer):
    global state
    # Toggle state between 0 and 1 every 1 second (100 * 10ms)
    state = 1 - state

def update_temp_ref(button1_pressed, button2_pressed):
    global temp_ref, count_counter
    # Adjust the temp_ref based on button presses
    if button1_pressed or button2_pressed:
        if count_counter >= COUNT_SPEED:
            temp_ref += TEMP_REF_INCREMENT if button1_pressed else -TEMP_REF_INCREMENT
            count_counter = 0
        else:
            count_counter += 1

def main():
    # Setup and initialization code here...
    # presentacion.presentation(i2c)
    timer0.init(mode=Timer.PERIODIC, period=DEBOUNCE_TIME_MS, callback=timer_10ms_callback)
    
    while True:
        # Button and LED handling code here...
        # read_sensor and display_logic can be functions defined to handle
        # sensor reading and display logic respectively.
        
        # Example functions that need to be implemented
        read_sensor()
        display_logic()

        # Sleeping to prevent tight loop from consuming resources
        sleep_ms(10)

def read_sensor():
    global average_sensor, average_ref, state
    # Sensor reading and filtering logic...
    # Assumes the existence of an iir_low_pass_filter function and ADC reading functions
    if state == 0:
        # Direct sensor reading
    elif state == 1:
        # Filtered sensor reading

def display_logic():
    global average_sensor, temp_ref
    # Display handling logic...
    # Assumes the existence of a display object like an OLED to show data

if __name__ == '__main__':
    main()
