from machine import Pin, I2C, ADC
from utime import sleep_ms
from ssd1306 import SSD1306_I2C
# 
# def inicializacion():
    
global FACTOR
FACTOR = 3.3 / (65535)

global ADC_SENSOR
global ADC_REF
ADC_SENSOR = 26
ADC_REF = 27

global PIN_SCL
global PIN_SDA
PIN_SCL =17
PIN_SDA = 16


global PENDIENTE
global CORTE_Y
PENDIENTE = 0.0202
CORTE_Y = 0.0574

#     En la documentación se menciona que puede haber un offset de 0.03V = 30mV
global CONSTANT_PICO
CONSTANT_PICO = -0.03

i2c = I2C(0, scl = Pin(PIN_SCL), sda = Pin(PIN_SDA), freq = 400000)
sensor = ADC(ADC_SENSOR)
ref = ADC(ADC_REF)

# Tiene un WIDTH = 128 y un HEIGHT = 64 que es el tamaño de la pantalla en pixeles
oled = SSD1306_I2C(128, 64, i2c)

# Initialize previous filtered values for both channels
prev_filtered_value_sensor = 0
prev_filtered_value_ref = 0


#Global Variables
t = 0
y = [55, 55]
x = [25, 25]



LED_PINS = [Pin(pin_num, Pin.OUT) for pin_num in [3, 4, 5, 6]]

button1 = Pin(0,Pin.IN,Pin.PULL_UP)
button2 = Pin(1,Pin.IN,Pin.PULL_UP)
button3 = Pin(2,Pin.IN,Pin.PULL_UP)    


# Initialize LED states
led_states = [0, 0, 0, 0]

t0= t
x0= x
y0= y

var = [0,70]
vpts=[25, 20, 36]
hpts = [25, 55, 112]

i2c = I2C(0, scl = Pin(PIN_SCL), sda = Pin(PIN_SDA), freq = 400000)
