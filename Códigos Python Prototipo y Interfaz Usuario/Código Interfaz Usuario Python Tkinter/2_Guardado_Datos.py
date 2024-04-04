# import serial

# serial_port = serial.Serial('COM5', baudrate=9600) 
# try:
#     while True:
#         data = serial_port.readline()
#         print(data.decode('utf-8'))  # Decode the data and print it as a string
# except KeyboardInterrupt:
#     serial_port.close()  # Close the serial port it is done
import os
import serial
import pandas as pd
import time
from datetime import datetime

# Define the serial port and baud rate
serial_port = 'COM5'  # Change this to the appropriate serial port on your system (e.g., 'COM5' for Windows)
baud_rate = 9600

# Create a serial connection
ser = serial.Serial(serial_port, baud_rate)

# Initialize an empty list to store data
data = []

# Record the start time
start_time = time.time()

while True:
    try:
        # Read data from the serial port
        data_from_serial = ser.readline().decode().strip()
        
        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create a dictionary for the current data
        data_dict = {'Timestamp': timestamp, 'Value': data_from_serial}
        
        # Append the data dictionary to the list
        data.append(data_dict)
        
        # Print the received data
        print(f"Timestamp: {timestamp}, Value: {data_from_serial}")

        # Check if an 10 seconds have passed
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:  # 10 seconds
            # Save the data to 'serial_data.csv'
            data_df = pd.DataFrame(data)
            if os.path.exists('serial_data.csv'):
                existing_data = pd.read_csv('serial_data.csv')
                data_df = pd.concat([existing_data, data_df], ignore_index=True)
            data_df.to_csv('serial_data.csv', index=False)
            
            # Reset the start time and clear the data list
            start_time = time.time()
            data = []

    except KeyboardInterrupt:
        # Close the serial connection when the user presses Ctrl+C
        ser.close()
        print("Serial connection closed.")
        break
