from flask import Flask, jsonify, render_template_string
import threading

app = Flask(__name__)

# Global dictionary holding the flight controller status.
flight_status = {
    "motor_outputs": [0.0, 0.0, 0.0, 0.0],
    "accelerometer": {"ax": 0.0, "ay": 0.0, "az": 0.0},
    "gyroscope": {"gx": 0.0, "gy": 0.0, "gz": 0.0},
    "orientation": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
    "logs": []
}

# HTML for the webpage.
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Quadcopter Flight Controller Status</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; }
        h1 { text-align: center; color: #333; }
        .section { margin-bottom: 20px; }
        .section h2 { border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        .log { background: #eee; padding: 10px; height: 200px; overflow-y: scroll; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
<div class="container">
    <h1>Quadcopter Flight Controller Status</h1>
    <div class="section" id="sensor-data">
        <h2>Sensor Data</h2>
        <p><strong>Accelerometer:</strong> <span id="accel"></span></p>
        <p><strong>Gyroscope:</strong> <span id="gyro"></span></p>
        <p><strong>Orientation:</strong> <span id="orientation"></span></p>
    </div>
    <div class="section" id="motor-outputs">
        <h2>Motor Outputs</h2>
        <table>
            <thead>
                <tr>
                    <th>Motor 1</th>
                    <th>Motor 2</th>
                    <th>Motor 3</th>
                    <th>Motor 4</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td id="motor1"></td>
                    <td id="motor2"></td>
                    <td id="motor3"></td>
                    <td id="motor4"></td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="section" id="logs">
        <h2>Flight Controller Logs</h2>
        <div class="log" id="logArea"></div>
    </div>
</div>
<script>
function updateData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            document.getElementById("accel").innerText = 
                "ax: " + data.accelerometer.ax.toFixed(2) + ", ay: " + data.accelerometer.ay.toFixed(2) + ", az: " + data.accelerometer.az.toFixed(2);
            document.getElementById("gyro").innerText = 
                "gx: " + data.gyroscope.gx.toFixed(2) + ", gy: " + data.gyroscope.gy.toFixed(2) + ", gz: " + data.gyroscope.gz.toFixed(2);
            document.getElementById("orientation").innerText = 
                "roll: " + data.orientation.roll.toFixed(2) + ", pitch: " + data.orientation.pitch.toFixed(2) + ", yaw: " + data.orientation.yaw.toFixed(2);
            document.getElementById("motor1").innerText = data.motor_outputs[0].toFixed(2);
            document.getElementById("motor2").innerText = data.motor_outputs[1].toFixed(2);
            document.getElementById("motor3").innerText = data.motor_outputs[2].toFixed(2);
            document.getElementById("motor4").innerText = data.motor_outputs[3].toFixed(2);
            
            // Update logs area
            let logArea = document.getElementById("logArea");
            logArea.innerHTML = "";
            data.logs.forEach(function(log) {
                let p = document.createElement("p");
                p.innerText = log;
                logArea.appendChild(p);
            });
        })
        .catch(error => console.error("Error fetching data:", error));
}
setInterval(updateData, 500); // Update every 500 ms.
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/data')
def data():
    return jsonify(flight_status)

def run_server():
    # Run the Flask server on all network interfaces on port 5000.
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# Expose the flight_status dictionary for updating from other threads.
def get_status():
    return flight_status
