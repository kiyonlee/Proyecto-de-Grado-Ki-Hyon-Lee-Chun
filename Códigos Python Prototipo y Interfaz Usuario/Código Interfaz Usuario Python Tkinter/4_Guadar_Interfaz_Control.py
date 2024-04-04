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

# Definir el puerto serie y la tasa de baudios
serial_port = 'COM3'  # Actualizar esto a su puerto serie
baud_rate = 115200

# Crear una conexión serie
ser = serial.Serial(serial_port, baud_rate)

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
led_canvas.create_text(30, 50, text="Controlado")
led_canvas.create_text(100, 50, text="ON")
led_canvas.create_text(140, 50, text="OFF")

def update_leds(temp_pt100, temp_ref):
    led_canvas.itemconfig(led_yellow1, fill="grey")
    led_canvas.itemconfig(led_yellow2, fill="grey")
    led_canvas.itemconfig(led_blue, fill="grey")
    led_canvas.itemconfig(led_red, fill="grey")

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

# Función para iniciar la lectura de datos
def iniciar_lectura():
    global serial_port, baud_rate, ser
    serial_port = entrada_puerto_serie.get()
    baud_rate = int(entrada_baudios.get())
    ser = serial.Serial(serial_port, baud_rate)
    update_gui()

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
def update_gui():
    global start_time, minute_values_pt100, minute_values_ref, last_minute  # Declarar variable global
    try:
        # Leer datos del puerto serie
        data_from_serial = ser.readline().decode().strip()
        temp_pt100, temp_ref = map(float, data_from_serial.split(','))

        # Obtener la marca de tiempo actual sin milisegundos
        timestamp = datetime.now().replace(microsecond=0)

        # Actualizar las listas de datos para el gráfico en vivo
        timestamps.append(timestamp)
        temp_pt100_values.append(temp_pt100)
        temp_ref_values.append(temp_ref)

        # Actualizar indicadores LED
        update_leds(temp_pt100, temp_ref)

        # Mostrar los datos recibidos en la interfaz tkinter
        etiqueta_valor.config(text=f"Marca de Tiempo: {timestamp}, Temp PT100: {temp_pt100}, Temp Ref: {temp_ref}")

        # Actualizar el gráfico en vivo
        ax.clear()
        ax.plot(timestamps, temp_pt100_values, label='Temp PT100')
        ax.plot(timestamps, temp_ref_values, label='Temp Ref', linestyle='--')
        ax.legend()
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Temperatura")

        # Personalizar las etiquetas del eje x usando DateFormatter
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

        canvas.draw()

        # Agregar valores a la lista para el promedio por minuto
        current_minute = timestamp.minute
        if last_minute is None or last_minute != current_minute:
            if minute_values_pt100 and minute_values_ref:
                # Calcular el promedio del minuto anterior
                avg_pt100 = sum(minute_values_pt100) / len(minute_values_pt100)
                avg_ref = sum(minute_values_ref) / len(minute_values_ref)

                # Guardar el promedio en un archivo CSV
                minute_avg_data = {'Timestamp': timestamp, 'Average_PT100': avg_pt100, 'Average_Ref': avg_ref}
                minute_avg_df = pd.DataFrame([minute_avg_data])
                minute_avg_df.to_csv('minute_average_data.csv', mode='a', header=not os.path.exists('minute_average_data.csv'), index=False, date_format='%Y-%m-%d %H:%M:%S')

            # Reiniciar las listas para el próximo minuto
            minute_values_pt100 = []
            minute_values_ref = []
            last_minute = current_minute

        minute_values_pt100.append(temp_pt100)
        minute_values_ref.append(temp_ref)

        # Verificar si han pasado 10 segundos para el registro de datos
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:
            # Guardar los datos en un archivo CSV
            data_to_save = {'Timestamp': timestamp, 'Temp_PT100': temp_pt100, 'Temp_Ref': temp_ref}
            df_to_save = pd.DataFrame([data_to_save])
            file_exists = os.path.exists('serial_data.csv')
            df_to_save.to_csv('serial_data.csv', mode='a', header=not file_exists, index=False)

            # Restablecer el tiempo de inicio
            start_time = time.time()

        # Programar la función para ejecutarse nuevamente después de 1000 milisegundos (1 segundo)
        root.after(1000, update_gui)
    except KeyboardInterrupt:

        # Cerrar la conexión serie cuando el usuario presiona Ctrl+C
        ser.close()
        print("Conexión serie cerrada.")
        root.destroy()

# Ejecutar el bucle principal tkinter
root.mainloop()
