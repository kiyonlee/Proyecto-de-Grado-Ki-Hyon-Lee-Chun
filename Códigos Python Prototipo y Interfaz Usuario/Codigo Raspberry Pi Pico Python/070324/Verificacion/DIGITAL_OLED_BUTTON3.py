from machine import Pin, I2C, ADC
from utime import sleep_ms
from ssd1306 import SSD1306_I2C

LED_PINS = [Pin(pin_num, Pin.OUT) for pin_num in [3, 4, 5, 6]]


def plot_time(yp, t, x, y, var = [0,70], vpts=[25, 20, 36], hpts = [25, 55, 112]):
    """"
    
    plot_time(yp, t, x, y, var = [0,70], vpts=[25, 20, 36], hpts = [25, 55, 112]):

    yp: dependent variable
    t: time (used while the Cartesian plane is not complete)
    x: List of two positions of variable x, x[0] is the position in past x and x[1] position of current x.
    y: List of two posdditions of the variable y, y[0] is the position in y past and y[1] position of current x.
    var = [0.0,70]: Magnitude of the variable (default voltage)
    vpts = [25, 20, 36]: points on the vertical y axis.
    hpts = [25, 55, 112]: points on the vertical x axis.
    """
    # Define upper and lower bounds for plotting
    lower_bound = max(var[0], 0)
    upper_bound = min(var[1], 70)
    
    # Clamp the value of yp to the lower and upper bounds
    yp = max(lower_bound, min(yp, upper_bound))
    
    #Axis
    oled.vline(vpts[0], vpts[1], vpts[2], 1) #x, y, h
    oled.hline(hpts[0], hpts[1], hpts[2], 1) #x, y, w
    oled.text(str(round(var[0],1)), vpts[0]-25, hpts[1]-5)
    oled.text(str(round(var[1],1)), vpts[0]-25, vpts[1])
    #y - axis
    y[1] = int((yp-var[0])/(var[1]-var[0]) * (vpts[1]-hpts[1]) + hpts[1]) #Interpolation
    if t < hpts[2] - hpts[0]:
        x[1] = x[0]+1
    else:
        x[1] = hpts[2]
    
    #Plot the line
    oled.line(x[0],y[0],x[1],y[1],1)
    oled.show()
    
    #Update past values
    y[0] = y[1]
    x[0] = x[1]
    
    #If you have already reached the end of the graph then ...
    if t > hpts[2] - hpts[0]:
        #Erases the first few pixels of the graph and the y-axis.
        oled.fill_rect(vpts[0],vpts[1],2,vpts[2],0) 
        #Clears the entire y-axis scale
        oled.fill_rect(vpts[0]-25, vpts[1],vpts[0],vpts[2]+5,0)
        #shifts the graph one pixel to the left
        oled.scroll(-1,0)
        #Axis
        oled.vline(vpts[0], vpts[1], vpts[2], 1) #x, y, h
        oled.hline(hpts[0], hpts[1], hpts[2], 1) #x, y, w
        oled.text(str(round(var[0],1)), vpts[0]-25, hpts[1]-5)
        oled.text(str(round(var[1],1)), vpts[0]-25, vpts[1])
    else:
        t += 1

    
    return t,x,y


def iir_low_pass_filter1(input_value, prev_filtered_value):
    
    # Constants for the filter
    fs = 1000    # Sampling frequency in Hz
    fc = 10      # Cutoff frequency in Hz
    alpha = 2 * 3.141592653589793 * fc / fs
    
    output_value = alpha * input_value + (1 - alpha) * prev_filtered_value
    return output_value

def iir_low_pass_filter2(input_value, prev_filtered_value):
    
    # Constants for the filter
    fs = 1000    # Sampling frequency in Hz
    fc = 100      # Cutoff frequency in Hz
    alpha = 2 * 3.141592653589793 * fc / fs
    
    output_value = alpha * input_value + (1 - alpha) * prev_filtered_value
    return output_value


if __name__ == '__main__':
    
    WIDTH = 128
    HEIGHT = 64
    FACTOR = 3.3 / (65535)
    
    ADC_SENSOR = 26
    ADC_REF = 27
    
    PIN_SCL =17
    PIN_SDA = 16
    
    i2c = I2C(0, scl = Pin(PIN_SCL), sda = Pin(PIN_SDA), freq = 400000)
    sensor = ADC(ADC_SENSOR)
    ref = ADC(ADC_REF)
    
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    
    # Initialize previous filtered values for both channels
    prev_filtered_value_sensor = 0
    prev_filtered_value_ref = 0


    #Global Variables
    t = 0
    y = [55, 55]
    x = [25, 25]
    
    oled.fill(0)
    oled.text("PG - PUJ", 35, 5)
    oled.text("Ki Hyon Lee", 20, 20)
    oled.text("Sensor Temp", 25, 40)
    oled.show()
    sleep_ms(2000)
    oled.fill(0)
    
    button1 = Pin(0,Pin.IN)
    button2 = Pin(1,Pin.IN)
    button3 = Pin(2,Pin.IN)
    
#     button1 = Pin(0,Pin.IN,Pin.PULL_UP)
#     button2 = Pin(1,Pin.IN,Pin.PULL_UP)
#     button3 = Pin(2,Pin.IN,Pin.PULL_UP)    
    
    
    # Initialize LED states
    led_states = [0, 0, 0, 0]

    while True:
        
    # Handle button presses
        if not button1.value():
            led_states[0] = not led_states[0]  # Toggle LED on pin 3
        if not button2.value():
            led_states[1] = not led_states[1]  # Toggle LED on pin 4
        if not button3.value():
            led_states[2] = not led_states[2]  # Toggle LED on pin 5

        # Update LED states
        for i in range(4):
            LED_PINS[i].value(led_states[i])
        
        print(str("El button 1 esta: ")+str(button1.value()))
        print(str("El button 2 esta: ")+str(button2.value()))
        print(str("El button 3 esta: ")+str(button3.value()))
        
        volts1 = sensor.read_u16() * FACTOR
        volts2 = ref.read_u16() * FACTOR
        
        filtered_value_sensor = iir_low_pass_filter1(volts1, prev_filtered_value_sensor)
        prev_filtered_value_sensor = filtered_value_sensor
        
        RPT100=(filtered_value_sensor-0.0574)/0.0202
        TemperaturaPT100=(RPT100-100)/0.384
        
        t,x,y = plot_time(TemperaturaPT100,t,x,y)
        
        
        filtered_value_ref = iir_low_pass_filter2(volts2, prev_filtered_value_ref)
        prev_filtered_value_ref = filtered_value_ref
        
        TempRef = (70/3.3)*filtered_value_ref
        
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
        sleep_ms(100)