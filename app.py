from flask import Flask, jsonify, render_template, request
import threading
from plc_reader import plc_polling_thread
import json

app = Flask(__name__)

        
# Files Varaibles
file_path = "staionparam.json"
station_number = {"Active_Station_Number": 1}

# Dashboard rendering
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# Stations Selections
@app.route("/api/station", methods=["POST"])
def update_station():
    data = request.get_json()
    activestaion= str(data["station"])
    if activestaion == None:
        station_number['Active_Station_Number'] = 1
    else:
        station_number['Active_Station_Number'] = activestaion
    return render_template("dashboard.html")

# Updates Stations Data
@app.route("/api/stats")
def getstationupdate():
    temp_file = open(file_path, "r")
    latest_update = json.load(temp_file)
    temp_file.close()
    station_update = jsonify({
            "station": latest_update[f'Station {station_number['Active_Station_Number']}']['station Number'],
            "total_parts": latest_update[f'Station {station_number['Active_Station_Number']}']['total_parts'],
            "ok_parts": latest_update[f'Station {station_number['Active_Station_Number']}']['ok_parts'],
            "nok_parts": latest_update[f'Station {station_number['Active_Station_Number']}']['nok_parts'],
            "avg_cycle_time": latest_update[f'Station {station_number['Active_Station_Number']}']['avg_cycle_time'],
            "station_counts": [latest_update['Station 1']['total_parts'],
                                latest_update['Station 2']['total_parts'],
                                latest_update['Station 3']['total_parts'],
                                latest_update['Station 4']['total_parts'],
                                latest_update['Station 5']['total_parts']]
    })
    return station_update

if __name__ == "__main__":
    t = threading.Thread(target=plc_polling_thread, daemon=True)
    t.start()
    app.run(host="localhost", port=5100, debug=False)
    