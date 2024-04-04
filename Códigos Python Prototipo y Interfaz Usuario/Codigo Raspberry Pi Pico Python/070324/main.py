from machine import Pin, I2C, ADC, Timer
from utime import sleep_ms
from ssd1306 import SSD1306_I2C
import base as bs
import presentacion
import random
import sys
import uselect
import time
import select
# import etapa1


# Create an instance of a polling object 
poll_obj = select.poll()
# Register sys.stdin (standard input) for monitoring read events with priority 1
poll_obj.register(sys.stdin,1)

timer0 = Timer()

CONTADOR=0
CONTADOR2=0
STATE=0

TemperaturaPT100=0

TempRef = 25.1


count_speed = 100  # Increase this value for slower counting
count_counter = 0

LED_Estado=""

gp0_pin = machine.Pin(13, machine.Pin.OUT)  # Pin GP13

def contador_10ms(timer):
    
    global CONTADOR, STATE, CONTADOR2

    if CONTADOR == 100:
        STATE=1
        CONTADOR=0
    else:
        STATE=2
        

    CONTADOR += 1
#     CONTADOR2 +=1
    

if __name__ == '__main__':
    

    
    # Importar las variables necesarias
    from inicializacion import PIN_SCL, PIN_SDA, LED_PINS,  button1,button2,button3, led_states, sensor, ref, FACTOR, CONSTANT_PICO, prev_filtered_value_sensor,prev_filtered_value_ref, t, x, y, t0, x0, y0,var, vpts,hpts,oled,i2c

    presentacion.presentation(i2c)
    
    timer0.init(mode=machine.Timer.PERIODIC, period=10, callback=contador_10ms)

    while True:
        
        if TemperaturaPT100 > (TempRef*1.02):
            LED_Estado="PRENDIDO"
        elif TemperaturaPT100 < (TempRef*0.98):
            LED_Estado="APAGADO"
        else:
            LED_Estado="CONTROLADO"
        
        if poll_obj.poll(0):
            
            # Lee 4 caracteres de la UART
            try:
                input_data = sys.stdin.read(4)
                input_data = float(input_data)
                
                if input_data==9997:
                    LED_Estado="CONTROLADO"

                elif input_data==9998:
                    LED_Estado="APAGADO"

                elif input_data==9999:
                    LED_Estado="PRENDIDO"

                else :
                    TempRef = input_data
            except ValueError:
                pass

            
        if button3.value():
#             print(str("El button de ARRIBA esta presionado: ")+str(button3.value()))
            led_states[0] = 1  # Toggle LED on pin 3
            led_states[1] = 1  # Toggle LED on pin 6
            
            if button1.value() and button3.value():
                # Button 1 and Button 3 are pressed, count upwards (slower)
                led_states[2] = 1  # Toggle LED on pin 5

                if count_counter >= count_speed:
                    TempRef += 0.01
                    count_counter = 0
                else:
                    count_counter += 1

            elif button2.value() and button3.value():
                # Button 2 and Button 3 are pressed, count downwards (slower)
                led_states[3] = 1  # Toggle LED on pin 4

                if count_counter >= count_speed:
                    TempRef -= 0.01
                    count_counter = 0
                else:
                    count_counter += 1
            else:
                led_states[2] = 0
                led_states[3] = 0
        else:
            if LED_Estado=="CONTROLADO":                
                led_states[0] = 1  # Encender LED amarillo en pin asociado
                led_states[1] = 1  # Encender otro LED amarillo en pin asociado
                led_states[2] = 0
                led_states[3] = 0
            elif LED_Estado=="APAGADO":
                led_states[0] = 0  # Encender LED amarillo en pin asociado
                led_states[1] = 0  # Encender otro LED amarillo en pin asociado
                led_states[2] = 1
                led_states[3] = 0
            elif LED_Estado=="PRENDIDO":
                led_states[0] = 0  # Encender LED amarillo en pin asociado
                led_states[1] = 0  # Encender otro LED amarillo en pin asociado
                led_states[2] = 0
                led_states[3] = 1
            else:
                led_states[0] = 0  # Encender LED amarillo en pin asociado
                led_states[1] = 0  # Encender otro LED amarillo en pin asociado
                led_states[2] = 0
                led_states[3] = 0             
        # Update LED states
        for i in range(4):
            LED_PINS[i].value(led_states[i])
        
        if STATE == 0:
            
#             gp0_pin.value(not gp0_pin.value())  # Invertir el estado de GP0
            
            volts1 = (sensor.read_u16() * FACTOR)+CONSTANT_PICO
            volts2 = (ref.read_u16() * FACTOR)+CONSTANT_PICO
            
            prev_filtered_value_sensor = volts1
            prev_filtered_value_ref = volts2
            
            promedio1=prev_filtered_value_sensor
            promedio2=prev_filtered_value_ref
            
        
        if STATE == 1:
            
            
            TemperaturaPT100=promedio1/100
            promedio1=0
            
#             TempRef=promedio2/100          
#             promedio2=0

#             print(str(round(volts1,2))+","+str(round(TemperaturaPT100,2)))
            print(str(TemperaturaPT100)+","+str(TempRef))
#             print(str(TemperaturaPT100))

            
            t,x,y = bs.plot_time(TemperaturaPT100,t0,x0,y0,var, vpts, hpts, oled)

            t0= t
            x0= x
            y0= y
            
            oled.fill_rect(0,0,120,20,0)
            
            oled.text("Temp Act: ", 0, 0)
            
            if TemperaturaPT100 > 70:
                oled.text(str("Err"), 80, 0)
            else:
                if TemperaturaPT100 < 0:
                    oled.text(str("Err"), 80, 0)
                else:
                    oled.text(str(round(TemperaturaPT100,2)), 80, 0)
            
            oled.text("Temp Ref: ", 0, 9)
            oled.text(str(round(TempRef,2)), 80, 9)
            
            oled.show()
            
            STATE=3
            
        if STATE == 2:
            
            gp0_pin.value(not gp0_pin.value())  # Invertir el estado de GP0
            
            volts1 = (sensor.read_u16() * FACTOR)+CONSTANT_PICO
            volts2 = (ref.read_u16() * FACTOR)+CONSTANT_PICO
            
            filtered_value_sensor = bs.iir_low_pass_filter1(volts1, prev_filtered_value_sensor)
            prev_filtered_value_sensor = filtered_value_sensor
            
            filtered_value_ref = bs.iir_low_pass_filter2(volts2, prev_filtered_value_ref)
            prev_filtered_value_ref = filtered_value_ref
            
            
            promedio1=promedio1+(filtered_value_sensor*126.38)-273.83
            promedio2=promedio2+((70/3.3)*filtered_value_ref)
            
            STATE=3
            


