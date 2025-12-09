import serial
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS
import threading

SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
JSON_FILE = 'arduino_data.json'

app = Flask(__name__)
CORS(app)  # allow Next.js frontend

data_list = []


# ---- SERIAL READING THREAD ----
def read_serial():
    global data_list

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    print("Listening for Arduino data...")

    while True:
        try:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            # Parse JSON
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Append with timestamp
            entry = {
                "timestamp": time.time(),
                "data": parsed
            }

            data_list.append(entry)

            # Save entire list
            with open(JSON_FILE, "w") as f:
                json.dump(data_list, f, indent=2)

            print("Saved:", entry)

        except Exception as e:
            print("Serial Error:", e)
            break


# ---- API ROUTE ----
@app.get("/data")
def get_data():
    """Return full history to frontend."""
    return jsonify(data_list)


# ---- START THREAD + SERVER ----
if __name__ == "__main__":
    # Start the serial reading loop in background
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()

    # Start the API server
    app.run(host="0.0.0.0", port=5000)
