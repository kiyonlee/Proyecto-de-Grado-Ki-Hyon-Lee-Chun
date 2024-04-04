import os
import tkinter as tk
from tkinter import Entry, Button, Label
import pandas as pd
import serial
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from collections import deque

# Create a tkinter window
root = tk.Tk()
root.title("Serial Port Data Logger with Live Graph")

# Define the serial port and baud rate
serial_port = 'COM3'  # Change this to the appropriate serial port on your system
baud_rate = 115200

# Create a serial connection
ser = serial.Serial(serial_port, baud_rate)

# Initialize an empty list to store data
data = []

# Initialize deque objects to store data with a fixed length for live graph
max_data_points = 100  # Increase this to 100 or the desired number of data points on the graph
timestamps = deque(maxlen=max_data_points)
values = deque(maxlen=max_data_points)

# Initialize the start time
start_time = time.time()

# Initialize minute-averaging variables
minute_values = []

# Function to update the GUI with received data
def update_gui():
    global data, start_time, minute_values  # Declare global variables
    try:
        # Read data from the serial port
        data_from_serial = ser.readline().decode().strip()

        # Get the current timestamp without milliseconds
        timestamp = datetime.now().replace(microsecond=0)

        # Create a dictionary for the current data
        data_dict = {'Timestamp': timestamp, 'Value': data_from_serial}

        # Append the data dictionary to the list
        data.append(data_dict)

        # Update the data lists for live graph
        timestamps.append(timestamp)
        values.append(float(data_from_serial))

        # Compute and save the average value at the beginning of each minute
        current_minute = timestamp.second
        minute_values.append(float(data_from_serial))
        if current_minute == 0 and len(minute_values) > 0:
            # Compute the average value for the minute
            minute_average = sum(minute_values) / len(minute_values)

            # Save the minute average to a CSV file
            minute_data = {'Timestamp': timestamp, 'AverageValue': minute_average}
            minute_df = pd.DataFrame([minute_data])
            minute_df.to_csv('minute_average_data.csv', mode='a', header=not os.path.exists('minute_average_data.csv'), index=False, date_format='%Y-%m-%d %H:%M:%S')

            # Clear the minute-averaging list
            minute_values = []

        # Display the received data in the tkinter interface
        value_label.config(text=f"Timestamp: {timestamp}, Value: {data_from_serial}")

        # Update the live graph
        ax.clear()
        ax.plot(timestamps, values)
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")

        # Customize the x-axis labels using DateFormatter
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

        canvas.draw()

        # Check if 10 seconds have passed for data logging
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:  # 10 seconds
            # Save the data to 'serial_data.csv' with timestamp resolution in seconds
            data_df = pd.DataFrame(data)
            if os.path.exists('serial_data.csv'):
                existing_data = pd.read_csv('serial_data.csv')
                data_df = pd.concat([existing_data, data_df], ignore_index=True)
            data_df.to_csv('serial_data.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')

            # Reset the start time and clear the data list
            start_time = time.time()
            data = []

        # Schedule the function to run again after 1000 milliseconds (1 second)
        root.after(1000, update_gui)
    except KeyboardInterrupt:
        # Close the serial connection when the user presses Ctrl+C
        ser.close()
        print("Serial connection closed.")
        root.destroy()

# Serial Port Entry
serial_label = Label(root, text="Serial Port:")
serial_label.pack()
serial_entry = Entry(root)
serial_entry.insert(0, serial_port)
serial_entry.pack()

# Start Button
start_button = Button(root, text="Start Reading", command=update_gui)
start_button.pack()

# Label to display the last received value
value_label = Label(root, text="Waiting for data...")
value_label.pack()

# Create a figure for the live graph
fig, ax = plt.subplots()
ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Run the tkinter main loop
root.mainloop()
