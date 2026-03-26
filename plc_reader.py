import snap7
import snap7.util
import time,json
import threading

PLC_ip = "192.168.0.183"
DB_NUMBER = 1
DB_SIZE = 12
file_path = "staionparam.json"

def makeconnection():
    client = snap7.client.Client()
    try:
        client.connect(PLC_ip, 0, 1)
        if client:
            print("Connected ")
    except Exception as e:
        print("Error Occured Connecting to PLC: ", e)


shared_data = {
    "station": 1,
    "total_parts": 0,
    "ok_parts": 0,
    "nok_parts": 0,
    "avg_cycle_time": 0.0,
    "station_counts": [0,0,0,0,0],
    "connected": False
}

lock = threading.Lock()
staionpoffset=1

def offsetCalculation(stationNumber):
    stationoffset = 12*stationNumber
    totalparts = 2 + stationoffset
    averagecycletime = 4 + stationoffset
    okparts =8+ stationoffset
    nokpart =10+ stationoffset
    # print("Off sets: ",stationNumber, stationoffset, totalparts, okparts,nokpart, averagecycletime)
    return stationoffset, totalparts, okparts,nokpart, averagecycletime

def read_int_FromPLC(plc, db_number, byteindex, size):
    Data1 = plc.db_read(db_number, byteindex, size)
    binary_str = ''.join(f'{byte:08b}' for byte in Data1)
    result = int(binary_str, 2)
    # print("Integer value: ", result)
    return result

def read_float_FromPLC(plc, db_number, byteindex, size):
    Data1 = plc.db_read(db_number, byteindex, 4)
    result = snap7.util.get_real(Data1, 0)
    # print("Real value: ", result)
    return result


with open(file_path, "r") as file:
    stations = json.load(file)

def readallatonce(client):
    for i in range(1,6):
        stationoffset, totalparts, okparts,nokpart, averagecycletime = offsetCalculation(i)
        stationcount = read_int_FromPLC(client, 1, stationoffset, 2)
        total_parts = read_int_FromPLC(client, 1, totalparts, 2)
        ok_parts = read_int_FromPLC(client, 1, okparts,2)
        nok_parts = read_int_FromPLC(client, 1, nokpart,2)
        avg_cycle = read_float_FromPLC(client, 1, averagecycletime, 2)
        stations[f'Station {i}']['station Number'] = stationcount
        stations[f'Station {i}']['total_parts'] = total_parts
        stations[f'Station {i}']['ok_parts'] = ok_parts
        stations[f'Station {i}']['nok_parts'] = nok_parts
        stations[f'Station {i}']['avg_cycle_time'] = avg_cycle
        # print(stations[f'Station {i}'])
    with open(file_path, "w") as file:
        json.dump(stations, file, indent=4)
    file.close()

def plc_polling_thread():
    client = snap7.client.Client()
    try:
        client.connect(PLC_ip, 0, 1)
        if client:
            print("Connected ")
    except Exception as e:
        makeconnection()
        print("Error Occured Connecting to PLC: ", e)
    while True:
            try:
                # data = client.db_read(DB_NUMBER, 0, DB_SIZE)
                # station = snap7.util.get_int(data, 0)
                staionpoffset=1
                if staionpoffset==0:
                    staionpoffset=1
                readallatonce(client)

                time.sleep(1)
            except Exception as e:
                makeconnection()
                print("Made new connections...", e)
                time.sleep(1)
