import serial

# Replace 'COMx' with the name of your serial port (e.g., '/dev/ttyUSB0' on Linux)
serial_port = serial.Serial('COM5', baudrate=9600)  # You may need to set the baud rate according to your device's settings

try:
    while True:
        data = serial_port.readline()
        print(data.decode('utf-8'))  # Decode the data and print it as a string
except KeyboardInterrupt:
    serial_port.close()  # Close the serial port when you're done

