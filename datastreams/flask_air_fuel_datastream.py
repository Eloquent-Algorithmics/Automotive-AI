import time
from flask import Flask, render_template_string, jsonify
import obd
from config import SERIAL_PORT, BAUD_RATE


app = Flask(__name__)

# Initialize lists for storing data
timestamps = []
SENSOR_DATA = {}
supported_sensors = []
start_time = time.time()


def check_and_add_sensor(sensor):
    if connection.query(sensor).is_null():
        return False
    supported_sensors.append(sensor)
    SENSOR_DATA[sensor] = []
    return True


@app.route("/")
def index():
    supported_sensors_desc = [sensor.desc for sensor in supported_sensors]
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
                {% for sensor_desc in supported_sensors %}
                <div class="graph-container" id="{{ sensor_desc }}"></div>
                {% endfor %}
                <script>
                    var graphs = {};

                    {% for sensor_desc in supported_sensors %}
                    var trace = {
                        x: [],
                        y: [],
                        mode: 'lines',
                        name: '{{ sensor_desc }}'
                    };

                    var layout = {
                        title: '{{ sensor_desc }}',
                        xaxis: {
                            title: 'Elapsed Time (s)'
                        },
                        yaxis: {
                            title: 'Value'
                        },
                        height: (100 / {{ num_sensors }}) + '%',
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

                    Plotly.newPlot('{{ sensor_desc }}', [trace], layout, config);
                    graphs['{{ sensor_desc }}'] = trace;
                    {% endfor %}

                    function updateData() {
                        fetch('/data')
                            .then(response => response.json())
                            .then(data => {
                                {% for sensor_desc in supported_sensors %}
                                var sensor_desc = '{{ sensor_desc }}';
                                var i = {{ loop.index0 }};
                                graphs[sensor_desc].x = data.timestamps.map(ts => (ts - data.start_time));
                                graphs[sensor_desc].y = data.sensor_data[i];
                                var xAxisRange = [
                                    graphs[sensor_desc].x[graphs[sensor_desc].x.length - 1] - 10,
                                    graphs[sensor_desc].x[graphs[sensor_desc].x.length - 1]
                                ];
                                var updateRange = {'xaxis.range': xAxisRange};
                                Plotly.relayout('{{ sensor_desc }}', updateRange);
                                Plotly.update('{{ sensor_desc }}', {x: [graphs[sensor_desc].x], y: [graphs[sensor_desc].y]});
                                var currentValue = data.sensor_data[i][data.sensor_data[i].length - 1];
                                var labelText = 'Current value: ' + currentValue;
                                if (sensor_desc === 'Engine RPM') {
                                    labelText = 'Current RPM: ' + currentValue;
                                } else if (sensor_desc === 'Mass Air Flow') {
                                    labelText = 'Current gm/s: ' + currentValue;
                                }
                                var update = {annotations: [{text: labelText}]};
                                Plotly.relayout('{{ sensor_desc }}', update);
                                {% endfor %}
                            })
                            .catch(error => console.error(error));

                        setTimeout(updateData, 200);
                    }

                    updateData();
                </script>
            </body>
        </html>
    """,
        num_sensors=len(supported_sensors),
        supported_sensors=supported_sensors_desc,
    )


@app.route("/data")
def data():
    global timestamps, SENSOR_DATA

    # Read the required OBD-II parameters
    for sensor in supported_sensors:
        response = connection.query(sensor)
        SENSOR_DATA[sensor].append(response.value.magnitude)

    # Append the timestamp
    timestamps.append(time.time())

    sensor_data_list = [SENSOR_DATA[sensor] for sensor in supported_sensors]

    return jsonify(
        {
            "timestamps": timestamps,
            "sensor_data": sensor_data_list,
            "start_time": start_time,
        }
    )


def start_datastream():
    connection = obd.OBD(portstr=SERIAL_PORT, baudrate=BAUD_RATE, fast=False)

    # Move the sensor checking logic inside this function
    supported_sensors = []
    SENSOR_DATA = {}
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

    if __name__ == "__main__":
        app.run(debug=False)