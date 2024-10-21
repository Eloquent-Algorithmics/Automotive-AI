import time
import threading
import re
from flask import Flask, render_template_string, jsonify
import obd
from src.config import SERIAL_PORT, BAUD_RATE

app = Flask(__name__)

# Initialize data structures
SENSOR_DATA = {}
timestamps = []
sensors_info = []
start_time = time.time()

# Establish OBD-II connection
connection = obd.OBD(portstr=SERIAL_PORT, baudrate=BAUD_RATE, fast=False)

# Lock for thread-safe operations
data_lock = threading.Lock()


def sanitize_sensor_desc(desc):
    """Sanitize sensor descriptions to create valid HTML IDs."""
    return re.sub(r"\W|^(?=\d)", "_", desc)


def check_and_add_sensor(sensor):
    """
    Checks if the given sensor exists in the database and adds it to the supported sensors list if it does.
    Returns:
        dict: sensor_info dict if successful, None otherwise.
    """
    response = connection.query(sensor)
    if response.is_null():
        return None
    sensor_desc = sensor.desc
    sensor_id = sanitize_sensor_desc(sensor_desc)
    SENSOR_DATA[sensor_id] = []
    sensor_info = {"sensor": sensor, "desc": sensor_desc, "id": sensor_id}
    return sensor_info


def start_datastream():
    global sensors_info
    sensor_list = [
        obd.commands["RPM"],
        obd.commands["MAF"],
        obd.commands["SHORT_FUEL_TRIM_1"],
        obd.commands["SHORT_FUEL_TRIM_2"],
        obd.commands["O2_B1S1"],
        obd.commands["O2_B2S1"],
        # Add other sensors as needed
    ]

    for sensor in sensor_list:
        sensor_info = check_and_add_sensor(sensor)
        if sensor_info:
            sensors_info.append(sensor_info)


def data_collector():
    """Background thread for collecting sensor data."""
    while True:
        with data_lock:
            for sensor_info in sensors_info:
                sensor = sensor_info["sensor"]
                sensor_id = sensor_info["id"]
                response = connection.query(sensor)
                sensor_data = None
                if not response.is_null():
                    value = response.value
                    if value is not None:
                        sensor_data = value.magnitude
                SENSOR_DATA[sensor_id].append(sensor_data)
                # Limit data length to last 500 points
                if len(SENSOR_DATA[sensor_id]) > 500:
                    SENSOR_DATA[sensor_id] = SENSOR_DATA[sensor_id][-500:]
            # Append the timestamp
            timestamps.append(time.time())
            if len(timestamps) > 500:
                timestamps[:] = timestamps[-500:]
        time.sleep(0.2)  # Adjust the sleep time as needed


@app.route("/")
def index():
    return render_template_string(
        """
        <html>
            <head>
                <title>OBD-II Live Data Stream</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: space-around;
                        height: 100vh;
                        margin: 23px;
                        padding: 0;
                    }
                    .graph-container {
                        box-sizing: border-box;
                        width: 50%;
                        padding: 10px;
                    }
                </style>
            </head>
            <body>
                {% for sensor in sensors_info %}
                <div class="graph-container" id="{{ sensor.id }}"></div>
                {% endfor %}
                <script>
                    var graphs = {};
                    {% for sensor in sensors_info %}
                    var trace = {
                        x: [],
                        y: [],
                        mode: 'lines',
                        name: '{{ sensor.desc }}'
                    };
                    var layout = {
                        title: '{{ sensor.desc }}',
                        xaxis: {
                            title: 'Elapsed Time (s)'
                        },
                        yaxis: {
                            title: 'Value'
                        },
                        height: '50%',
                        margin: {
                            t: 50,
                            l: 50,
                            r: 50,
                            b: 50
                        },
                        annotations: [{
                            xref: 'paper',
                            yref: 'y',
                            x: 1,
                            xanchor: 'right',
                            y: 0,
                            yanchor: 'bottom',
                            text: '',
                            showarrow: false,
                            font: {
                                size: 16
                            }
                        }]
                    };
                    var config = {responsive: true};
                    Plotly.newPlot('{{ sensor.id }}', [trace], layout, config);
                    graphs['{{ sensor.id }}'] = {
                        trace: trace,
                        layout: layout
                    };
                    {% endfor %}
                    function updateData() {
                        fetch('/data')
                            .then(response => response.json())
                            .then(data => {
                                var timestamps = data.timestamps.map(ts => ts - data.start_time);
                                for (var sensor_id in data.sensor_data) {
                                    if (graphs.hasOwnProperty(sensor_id)) {
                                        var graph = graphs[sensor_id];
                                        graph.trace.x = timestamps;
                                        graph.trace.y = data.sensor_data[sensor_id];
                                        var xAxisRange = [
                                            timestamps[timestamps.length -1] - 10,
                                            timestamps[timestamps.length -1]
                                        ];
                                        var updateRange = {'xaxis.range': xAxisRange};
                                        Plotly.relayout(sensor_id, updateRange);
                                        Plotly.update(sensor_id, {x: [graph.trace.x], y: [graph.trace.y]});
                                        var currentValue = data.sensor_data[sensor_id][data.sensor_data[sensor_id].length -1];
                                        var labelText = 'Current value: ' + currentValue;
                                        // Custom annotations based on sensor IDs
                                        if (sensor_id === 'Engine_RPM') {
                                            labelText = 'Current RPM: ' + currentValue;
                                        } else if (sensor_id === 'Mass_Air_Flow') {
                                            labelText = 'Current gm/s: ' + currentValue;
                                        }
                                        var update = {annotations: [{text: labelText}]};
                                        Plotly.relayout(sensor_id, update);
                                    }
                                }
                            })
                            .catch(error => console.error(error));
                        setTimeout(updateData, 200);
                    }
                    updateData();
                </script>
            </body>
        </html>
        """,
        sensors_info=sensors_info,
        start_time=start_time,
    )


@app.route("/data")
def data():
    with data_lock:
        # Prepare sensor data for JSON
        sensor_data_json = {
            sensor_info["id"]: SENSOR_DATA[sensor_info["id"]]
            for sensor_info in sensors_info
        }
        return jsonify(
            {
                "timestamps": [t - start_time for t in timestamps],
                "sensor_data": sensor_data_json,
                "start_time": 0,  # Timestamps are already adjusted
            }
        )


if __name__ == "__main__":
    start_datastream()
    # Start the data collection thread
    data_thread = threading.Thread(target=data_collector, daemon=True)
    data_thread.start()
    app.run(debug=False)
