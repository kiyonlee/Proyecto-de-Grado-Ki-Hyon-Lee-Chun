from machine import Pin, I2C, ADC
from utime import sleep_ms
from ssd1306 import SSD1306_I2C

LED_PINS = [Pin(pin_num, Pin.OUT) for pin_num in [3, 4, 5, 6]]

def plot_time(yp, t, x, y, var, vpts, hpts, salida_oled):
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
    salida_oled.vline(vpts[0], vpts[1], vpts[2], 1) #x, y, h
    salida_oled.hline(hpts[0], hpts[1], hpts[2], 1) #x, y, w
    salida_oled.text(str(round(var[0],1)), vpts[0]-25, hpts[1]-5)
    salida_oled.text(str(round(var[1],1)), vpts[0]-25, vpts[1])
    #y - axis
    y[1] = int((yp-var[0])/(var[1]-var[0]) * (vpts[1]-hpts[1]) + hpts[1]) #Interpolation
    if t < hpts[2] - hpts[0]:
        x[1] = x[0]+1
    else:
        x[1] = hpts[2]
    
    #Plot the line
    salida_oled.line(x[0],y[0],x[1],y[1],1)
    salida_oled.show()
    
    #Update past values
    y[0] = y[1]
    x[0] = x[1]
    
    #If you have already reached the end of the graph then ...
    if t > hpts[2] - hpts[0]:
        #Erases the first few pixels of the graph and the y-axis.
        salida_oled.fill_rect(vpts[0],vpts[1],2,vpts[2],0) 
        #Clears the entire y-axis scale
        salida_oled.fill_rect(vpts[0]-25, vpts[1],vpts[0],vpts[2]+5,0)
        #shifts the graph one pixel to the left
        salida_oled.scroll(-1,0)
        #Axis
        salida_oled.vline(vpts[0], vpts[1], vpts[2], 1) #x, y, h
        salida_oled.hline(hpts[0], hpts[1], hpts[2], 1) #x, y, w
        salida_oled.text(str(round(var[0],1)), vpts[0]-25, hpts[1]-5)
        salida_oled.text(str(round(var[1],1)), vpts[0]-25, vpts[1])
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


    