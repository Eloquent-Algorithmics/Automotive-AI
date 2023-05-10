"""
tkinter OBD simple GUI application.
"""
import time
from tkinter import Tk, TOP, BOTH
import obd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import SERIAL_PORT, BAUD_RATE

# Connect to the ELM327 device
connection = obd.OBD(portstr=SERIAL_PORT, baudrate=BAUD_RATE)

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
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_1)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_2)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_3)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_4)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_5)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_6)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_7)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_8)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_9)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_10)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_11)
check_and_add_sensor(obd.commands.MONITOR_MISFIRE_CYLINDER_12)

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
        response = connection.query(sensor)

        # Get the MonitorTest object for MISFIRE_COUNT
        misfire_count_test = response.value.MISFIRE_COUNT

        # Ensure the test is not null before appending its value
        if not misfire_count_test.is_null():
            SENSOR_DATA[sensor].append(misfire_count_test.value.magnitude)

    # Append the timestamp
    timestamps.append(time.time())

    # Update the graphs
    for axis in axs:
        axis.clear()

    for idx, sensor in enumerate(supported_sensors):
        SENSOR_AXES[sensor] = axs[idx]
        # Check if there is data for this sensor
        if len(SENSOR_DATA[sensor]) == len(timestamps):
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
