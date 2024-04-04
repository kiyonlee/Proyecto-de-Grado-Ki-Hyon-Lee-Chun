import os
import tkinter as tk
from tkinter import Entry, Button, Label, Canvas
import pandas as pd
import serial
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from collections import deque
import threading
import queue


# Crear ventana tkinter
root = tk.Tk()
root.title("Registrador de Datos de Puerto Serie con Gráfico en Tiempo Real e Indicadores LED")

# Configurar el diseño de la ventana usando grid
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=1)

# Definir el puerto serie y la tasa de baudios iniciales
serial_port = 'COM3'  # Actualizar esto a su puerto serie
baud_rate = 115200

# Inicializar objetos deque para el gráfico en vivo
max_data_points = 100
timestamps = deque(maxlen=max_data_points)
temp_pt100_values = deque(maxlen=max_data_points)
temp_ref_values = deque(maxlen=max_data_points)

# Inicializar el tiempo de inicio y variables para el promedio por minuto
start_time = time.time()
minute_values_pt100 = []
minute_values_ref = []
last_minute = None

# Configuración del lienzo LED
led_canvas = Canvas(root, width=200, height=100)
led_canvas.grid(row=0, column=0, columnspan=2)

# Dibujar marcadores LED
led_yellow1 = led_canvas.create_oval(10, 10, 30, 30, fill="grey")
led_yellow2 = led_canvas.create_oval(50, 10, 70, 30, fill="grey")
led_blue = led_canvas.create_oval(90, 10, 110, 30, fill="grey")
led_red = led_canvas.create_oval(130, 10, 150, 30, fill="grey")

# Títulos LED
led_canvas.create_text(40, 50, text="Controlado")
led_canvas.create_text(100, 50, text="ON")
led_canvas.create_text(140, 50, text="OFF")


def update_leds(temp_pt100, temp_ref):
    # Ensure this function is called on the main thread
    if root is None or not isinstance(temp_pt100, (int, float)) or not isinstance(temp_ref, (int, float)):
        return

    # Reset LEDs to grey
    led_canvas.itemconfig(led_yellow1, fill="grey")
    led_canvas.itemconfig(led_yellow2, fill="grey")
    led_canvas.itemconfig(led_blue, fill="grey")
    led_canvas.itemconfig(led_red, fill="grey")

    # Update LEDs based on temperature comparison
    if temp_pt100 > temp_ref * 1.02:
        led_canvas.itemconfig(led_red, fill="red")
    elif temp_pt100 < temp_ref * 0.98:
        led_canvas.itemconfig(led_blue, fill="blue")
    else:
        led_canvas.itemconfig(led_yellow1, fill="yellow")
        led_canvas.itemconfig(led_yellow2, fill="yellow")

# Crear una figura para el gráfico en vivo
fig, ax = plt.subplots()
ax.set_xlabel("Tiempo")
ax.set_ylabel("Temperatura")
ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, columnspan=2)

# Etiqueta para mostrar el último valor recibido
etiqueta_valor = Label(root, text="Esperando datos...")
etiqueta_valor.grid(row=2, column=0, columnspan=2)

# Entrada del puerto serie
etiqueta_puerto_serie = Label(root, text="Puerto Serie:")
etiqueta_puerto_serie.grid(row=3, column=0, sticky=tk.E)
entrada_puerto_serie = Entry(root)
entrada_puerto_serie.insert(0, serial_port)
entrada_puerto_serie.grid(row=3, column=1, sticky=tk.W)

# Entrada de la tasa de baudios
etiqueta_baudios = Label(root, text="Tasa de Baudios:")
etiqueta_baudios.grid(row=4, column=0, sticky=tk.E)
entrada_baudios = Entry(root)
entrada_baudios.insert(0, str(baud_rate))
entrada_baudios.grid(row=4, column=1, sticky=tk.W)

# Crear una cola para comunicarse entre el hilo de lectura del puerto serie y la GUI
data_queue = queue.Queue()

# Función para leer del puerto serie en un hilo separado
def read_from_port(q):
    while True:
        try:
            if ser is not None and ser.isOpen():
                line = ser.readline().decode().strip()
                if line:
                    q.put(line)
        except serial.SerialException:
            break

# Función para iniciar la lectura de datos
def iniciar_lectura():
    global serial_port, baud_rate, ser, serial_thread
    serial_port = entrada_puerto_serie.get()
    baud_rate = int(entrada_baudios.get())
    ser = serial.Serial(serial_port, baud_rate, timeout=0)

    # Iniciar el hilo de lectura del puerto serie
    serial_thread = threading.Thread(target=read_from_port, args=(data_queue,))
    serial_thread.daemon = True
    serial_thread.start()

# Botón de inicio
boton_inicio = Button(root, text="Iniciar Lectura", command=iniciar_lectura)
boton_inicio.grid(row=5, column=0, columnspan=2)

# Función para limpiar el gráfico
def limpiar_grafico():
    global timestamps, temp_pt100_values, temp_ref_values
    timestamps.clear()
    temp_pt100_values.clear()
    temp_ref_values.clear()
    ax.clear()
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Temperatura")
    canvas.draw()

# Botón de limpieza
boton_limpiar = Button(root, text="Limpiar Gráfico", command=limpiar_grafico)
boton_limpiar.grid(row=6, column=0, columnspan=2)

# Función para actualizar la GUI con los datos recibidos
# Función para actualizar la GUI con los datos recibidos
def update_gui():
    global start_time, minute_values_pt100, minute_values_ref, last_minute
    try:
        while not data_queue.empty():
            data_from_serial = data_queue.get_nowait()
            temp_pt100, temp_ref = map(float, data_from_serial.split(','))

            timestamp = datetime.now().replace(microsecond=0)

            timestamps.append(timestamp)
            temp_pt100_values.append(temp_pt100)
            temp_ref_values.append(temp_ref)

            # Update the LEDs with the current temperature values
            update_leds(temp_pt100, temp_ref)

            etiqueta_valor.config(text=f"Marca de Tiempo: {timestamp}, Temp PT100: {temp_pt100}, Temp Ref: {temp_ref}")

            ax.clear()
            ax.plot(timestamps, temp_pt100_values, label='Temp PT100')
            ax.plot(timestamps, temp_ref_values, label='Temp Ref', linestyle='--')
            ax.legend()
            ax.set_xlabel("Tiempo")
            ax.set_ylabel("Temperatura")
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            canvas.draw()

            current_minute = timestamp.minute
            if last_minute is None or last_minute != current_minute:
                if minute_values_pt100 and minute_values_ref:
                    avg_pt100 = sum(minute_values_pt100) / len(minute_values_pt100)
                    avg_ref = sum(minute_values_ref) / len(minute_values_ref)

                    minute_avg_data = {'Timestamp': timestamp, 'Average_PT100': avg_pt100, 'Average_Ref': avg_ref}
                    minute_avg_df = pd.DataFrame([minute_avg_data])
                    minute_avg_df.to_csv('minute_average_data.csv', mode='a', header=not os.path.exists('minute_average_data.csv'), index=False, date_format='%Y-%m-%d %H:%M:%S')

                minute_values_pt100 = []
                minute_values_ref = []
                last_minute = current_minute

            minute_values_pt100.append(temp_pt100)
            minute_values_ref.append(temp_ref)

            elapsed_time = time.time() - start_time
            if elapsed_time >= 10:
                data_to_save = {'Timestamp': timestamp, 'Temp_PT100': temp_pt100, 'Temp_Ref': temp_ref}
                df_to_save = pd.DataFrame([data_to_save])
                file_exists = os.path.exists('serial_data.csv')
                df_to_save.to_csv('serial_data.csv', mode='a', header=not file_exists, index=False)

                start_time = time.time()

    except KeyboardInterrupt:
        ser.close()
        print("Conexión serie cerrada.")
        root.destroy()

    root.after(100, update_gui)


# Schedule the first call to update_gui
root.after(100, update_gui)

# Ejecutar el bucle principal tkinter
root.mainloop()
