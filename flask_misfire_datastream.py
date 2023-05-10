import time
from flask import Flask, render_template_string, jsonify
import obd
from config import SERIAL_PORT, BAUD_RATE

# Connect to the ELM327 device
connection = obd.OBD(portstr=SERIAL_PORT, baudrate=BAUD_RATE)

app = Flask(__name__)

# Initialize lists for storing data
timestamps = []
SENSOR_DATA = {}
supported_sensors = []


def check_and_add_sensor(sensor):
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


@app.route("/")
def index():
    return render_template_string(
        """
        <html>
            <head>
                <title>OBD-II Live Data Stream</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div id="plot"></div>
                <script>
                    var traces = [];
                    var layout = {
                        title: 'OBD-II Live Data Stream',
                        xaxis: {
                            title: 'Time'
                        },
                        yaxis: {
                            title: 'Value'
                        }
                    };
                    var config = {responsive: true};

                    for (var i = 0; i < {{ num_sensors }}; i++) {
                        traces.push({
                            x: [],
                            y: [],
                            mode: 'lines',
                            name: 'Sensor ' + (i + 1)
                        });
                    }

                    Plotly.newPlot('plot', traces, layout, config);

                    function updateData() {
                        fetch('/data')
                            .then(response => response.json())
                            .then(data => {
                                for (var i = 0; i < {{ num_sensors }}; i++) {
                                    traces[i].x = data.timestamps;
                                    traces[i].y = data.sensor_data[i];
                                    Plotly.update('plot', {x: [traces[i].x], y: [traces[i].y]}, {}, [i]);
                                }
                            })
                            .catch(error => console.error(error));

                        setTimeout(updateData, 1000);
                    }

                    updateData();
                </script>
            </body>
        </html>
    """,
        num_sensors=len(supported_sensors),
    )


@app.route("/data")
def data():
    global timestamps, SENSOR_DATA

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

    sensor_data_list = [SENSOR_DATA[sensor] for sensor in supported_sensors]

    return jsonify({"timestamps": timestamps, "sensor_data": sensor_data_list})


if __name__ == "__main__":
    app.run(debug=False)
