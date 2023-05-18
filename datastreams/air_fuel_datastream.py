"""
tkinter OBD simple GUI application.
"""
import time
from tkinter import Tk, TOP, BOTH
import obd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Create a tkinter window
root = Tk()
root.title("OBD-II Live Data Stream")

# Create a matplotlib figure and add it to the tkinter window
fig = plt.figure(figsize=(10, 15))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

# Initialize lists for storing data
timestamps = []
SENSOR_DATA = {}
SENSOR_AXES = {}

# List of supported sensors
supported_sensors = []


def check_and_add_sensor(sensor):
    """
    Check if a sensor is supported and add it to the list.

    Args:
        sensor (obd.commands): The OBD-II sensor command to check for support.

    Returns:
        bool: True if the sensor is supported and added to the list.
    """
    if connection.query(sensor).is_null():
        return False
    supported_sensors.append(sensor)
    SENSOR_DATA[sensor] = []
    return True


# Check for supported sensors
check_and_add_sensor(obd.commands.RPM)
check_and_add_sensor(obd.commands.MAF)
check_and_add_sensor(obd.commands.SHORT_FUEL_TRIM_1)
check_and_add_sensor(obd.commands.LONG_FUEL_TRIM_1)
check_and_add_sensor(obd.commands.SHORT_FUEL_TRIM_2)
check_and_add_sensor(obd.commands.LONG_FUEL_TRIM_2)
check_and_add_sensor(obd.commands.O2_B1S1)
check_and_add_sensor(obd.commands.O2_B2S1)
check_and_add_sensor(obd.commands.INTAKE_PRESSURE)
check_and_add_sensor(obd.commands.THROTTLE_POS)
check_and_add_sensor(obd.commands.O2_S1_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S2_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S2_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S3_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S3_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S4_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S4_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S5_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S5_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S6_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S6_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S7_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S7_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S7_WR_CURRENT)
check_and_add_sensor(obd.commands.O2_S8_WR_VOLTAGE)
check_and_add_sensor(obd.commands.O2_S8_WR_CURRENT)

# Create subplots only for supported sensors
axs = []
for idx, sensor in enumerate(supported_sensors):
    ax = fig.add_subplot(len(supported_sensors), 1, idx + 1)
    axs.append(ax)


def update_graph(i):
    """
    Update the graph with new sensor data.

    Args:
        i (int): The index of the current data point.

    Globals:
        timestamps: List of timestamp values.
        SENSOR_DATA: List of sensor data values.
        SENSOR_AXES: List of sensor axes values.
    """
    global TIMESTAMPS, SENSOR_DATA, SENSOR_AXES

    # Read the required OBD-II parameters
    for sensor in supported_sensors:
        SENSOR_DATA[sensor].append(
            connection.query(sensor).value.magnitude)

    # Append the timestamp
    timestamps.append(time.time())

    # Update the graphs
    for axis in axs:
        axis.clear()

    for idx, sensor in enumerate(supported_sensors):
        SENSOR_AXES[sensor] = axs[idx]
        SENSOR_AXES[sensor].plot(timestamps, SENSOR_DATA[sensor])
        SENSOR_AXES[sensor].set_title(sensor.desc)

    for axis in axs:
        axis.set(xlabel="Time", ylabel="Value")

    fig.tight_layout()


# Create an animation to update the graph
ani = animation.FuncAnimation(
    fig, update_graph, interval=1, cache_frame_data=False, blit=False
)

# Start the tkinter main loop
root.mainloop()
