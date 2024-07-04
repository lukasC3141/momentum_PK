from typing import Tuple, Union, List, Dict
from flask import Flask, render_template
from serial import Serial
from datetime import datetime
from os import getcwd, mkdir
from json import dump, dumps, load
from math import log, atan2, pi
from time import sleep


# this is not used, left it here just in case
TEST_MODE: bool = False
REPLAY: bool = False
REPLAY_TIME = 0
REPLAY_CONNECTION = None
REPLAY_SRC = './rep.txt'
REPLAY_FREQUENCY = 2
REPLAY_START = 54_165
REPLAY_TIME_PLUS = 0

PORT: str = 'COM6'
BAUD_RATE: int = 115200
FREQUENCY: int = 2

M: float = 1000
m: float = 0.32
T: float = 273.15
R: float = 8.31432
g: float = 9.81

MAP_CORNERS: Tuple[Tuple[float, float], Tuple[float, float]] = ((49.2465356, 16.5284819), (49.2284906, 16.5833922))
MAP_SIZE: Tuple[float, float] = (
    MAP_CORNERS[1][0] - MAP_CORNERS[0][0],
    MAP_CORNERS[1][1] - MAP_CORNERS[0][1]
)
BATTERY_MILESTONES: Tuple = (2.5, 3.51, 3.6, 3.63, 3.65, 3.7, 3.74, 3.8, 3.87, 3.96)
GPS_LIMITS = ((48.5519972, 51.0556997), (12.0906633, 18.8591456))


atmospheric_pressure_reference: float = 1000
last_pressure: float = -1
last_data: dict = {}
distributed_data: dict = {"latitude": 0, "longitude": 0, "altitude": 0, "sat_count": 0, "battery_charge": 1,
                          "battery_voltage": 3.81, "battery_temperature": 24.33, "board_temperature": 37.07,
                          "atm_pressure": 1021.82, "atm_temperature": 22.77, "atm_humidity": 29, "atm_co2_eq": 500, "atm_co2_voc": 0.49, "atm_iaq": 25, 
                          "g_force": (0.07, 0.52, 0.86), "gyroscope": (0.00, 0.00, 0.00), "acceleration": (0.03,0.04,0.01), "magnetometer": (-321.00, -497.00, -557.00), "orientation": (-0.55, 0.07, 3.65), "force":(0.00, 0.00, 0.00)}

rad_clicks: List[int] = []
rad_times: List[int] = []


def load_pressure() -> None:
    try:
        with open(f"reference.json", "r") as file:
            pressure = float(load(file))

            global atmospheric_pressure_reference, last_pressure
            atmospheric_pressure_reference = pressure
            last_pressure = pressure
    except FileNotFoundError as err:
        archive_error(repr(err), path)


def process_data(data_str: str, errors: List[str]) -> dict:
    processed: dict = {'errors': errors}

    if len(data_str) == 0:
        return processed

    sliced: list = data_str.strip().split(';')
    try:
        a_index: int = sliced.index('a')

        latitude: str = sliced[a_index + 1]
        longitude: str = sliced[a_index + 2]
        altitude: str = sliced[a_index + 3]
        sat_count: str = sliced[a_index + 4]
        battery_voltage: str = sliced[a_index + 5]
        battery_temperature: str = sliced[a_index + 6]
        board_temperature: str = sliced[a_index + 7]
    except (ValueError, IndexError) as err:
        archive_error(repr(err), path)
        processed['errors'].append(repr(err))
        return processed

    try:
        if GPS_LIMITS[0][0] < float(latitude) < GPS_LIMITS[0][1]:
            processed['latitude'] = round(float(latitude), 6)
        if GPS_LIMITS[1][0] < float(longitude) < GPS_LIMITS[1][1]:
            processed['longitude'] = round(float(longitude), 6)

        if altitude != 0:
            processed['altitude'] = int(altitude)
        processed['sat_count'] = int(sat_count)
        processed['battery_voltage'] = round(float(battery_voltage), 2)
        processed['battery_temperature'] = \
            round(float(battery_temperature), 2)
        processed['board_temperature'] = \
            round(float(board_temperature), 2)
    except ValueError as err:
        archive_error(repr(err), path)
        processed['errors'].append(repr(err))

    try:
        b_index: int = sliced.index('b')
        atm_pressure: str = sliced[b_index + 1]
        atm_temperature: str = sliced[b_index + 2]
        atm_humidity: str = sliced[b_index + 3]
        atm_co2_eq: str = sliced[b_index + 4]
        atm_co2_voc: str = sliced[b_index + 5]
        atm_iaq: str = sliced[b_index + 6]

        g_force_x: str = sliced[b_index + 7]
        g_force_y: str = sliced[b_index + 8]
        g_force_z: str = sliced[b_index + 9]
        gyroscope_x: str = sliced[b_index + 10]
        gyroscope_y: str = sliced[b_index + 11]
        gyroscope_z: str = sliced[b_index + 12]
        acceleration_x: str = sliced[b_index + 13]
        acceleration_y: str = sliced[b_index + 14]
        acceleration_z: str = sliced[b_index + 15]
        magnetometer_x: str = sliced[b_index + 16]
        magnetometer_y: str = sliced[b_index + 17]
        magnetometer_z: str = sliced[b_index + 18]
        orientation_x: str = sliced[b_index + 19]
        orientation_y: str = sliced[b_index + 20]
        orientation_z: str = sliced[b_index + 21]
    except (ValueError, IndexError) as err:
        archive_error(repr(err), path)
        processed['errors'].insert(0, 'Secondary Arduino not responding')
        return processed

    try:
        processed['atm_pressure'] = round(float(atm_pressure), 2)
        processed['atm_temperature'] = round(float(atm_temperature), 2)
        processed['atm_humidity'] = int(atm_humidity)
        processed['atm_co2_eq'] = int(atm_co2_eq)
        processed['atm_co2_voc'] = round(float(atm_co2_voc), 2)
        processed['atm_iaq'] = int(atm_iaq)

        processed['g_force'] = (
            round(float(g_force_x), 2),
            round(float(g_force_y), 2),
            round(float(g_force_z), 2),
        )
        processed['gyroscope'] = (
            round(float(gyroscope_x), 2),
            round(float(gyroscope_y), 2),
            round(float(gyroscope_z), 2),
        )
        processed['acceleration'] = (
            round(float(acceleration_x), 2),
            round(float(acceleration_y), 2),
            round(float(acceleration_z), 2),
        )
        processed['magnetometer'] = (
            round(float(magnetometer_x), 2),
            round(float(magnetometer_y), 2),
            round(float(magnetometer_z), 2),
        )
        processed['orientation'] = (
            round(float(orientation_x), 2),
            round(float(orientation_y), 2),
            round(float(orientation_z), 2),
        )
    except ValueError as err:
        archive_error(repr(err), path)
        processed['errors'].insert(0, 'Secondary Arduino not responding')

    

    return processed


def get_time(organize: bool = False, textify: bool = False, date: bool = False) -> \
        Union[int, str, Tuple[int, int, int]]:
    now = datetime.now()
    if organize:
        if textify:
            if date:
                return f'{now.strftime("%Y")}-{now.strftime("%m")}-{now.strftime("%d")}T{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")}Z'
            else:
                return f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")}'
        else:
            return int(now.strftime("%H")), int(now.strftime("%M")), \
                int(now.strftime("%S"))
    else:
        return (int(now.strftime("%S")) + int(now.strftime("%M"))*60 +
                int(now.strftime("%H"))*60*60)


def archive_gpx(latitude: float, longitude: float, altitude: float, path_: str) -> None:
    if GPS_LIMITS[0][0] < latitude < GPS_LIMITS[0][1] or GPS_LIMITS[1][0] < longitude < GPS_LIMITS[1][1]:
        return
    
    try:
        with open(path_ + '\\track.gpx', 'a') as outfile:
            outfile.write(f'      <trkpt lat="{latitude}" lon="{longitude}">\n')
            outfile.write(f'        <ele>{altitude}</ele>\n')
            outfile.write(f'        <time>{get_time(organize=True, textify=True, date=True)}</time>\n')
            outfile.write(f'      </trkpt>\n')
    except FileNotFoundError:
        pass


def calculate_from_data(new: dict, last_data_: dict, init_time_: int,
                        atmospheric_pressure_reference_: float, path_: str) \
        -> Tuple[dict, dict, float]:
    if REPLAY:
        global REPLAY_TIME_PLUS
        print(REPLAY_TIME_PLUS)
        time = get_time()
        new['time'] = time - init_time_ + 49
        new['real_time'] = format_seconds(round(REPLAY_START + REPLAY_TIME_PLUS, 0), textify=True)[:-3]
        REPLAY_TIME_PLUS += 0.5
    else:
        time = get_time()
        new['time'] = time - init_time_
        new['real_time'] = get_time(True, True)[:-3]
    new['reference_pressure'] = round(atmospheric_pressure_reference_, 2)

    try:
        new['map'] = (
            (new['latitude'] - MAP_CORNERS[0][0]) / MAP_SIZE[0],
            (new['longitude'] - MAP_CORNERS[0][1]) / MAP_SIZE[1]
        )
        archive_gpx(new['latitude'], new['longitude'], new['altitude'], path_)
    except KeyError as err:
        archive_error(repr(err), path)
        new['errors'].append(repr(err))
    except Exception as err:
        archive_error(repr(err), path)
        new['errors'].append(repr(err))

    try:
        current_voltage = new['battery_voltage']
        charge_i = 0
        for milestone in BATTERY_MILESTONES:
            if milestone < current_voltage:
                charge_i += 1
            else:
                break
        if charge_i+1 >= len(BATTERY_MILESTONES):
            new['battery_charge'] = 1
        else:
            lin = BATTERY_MILESTONES[charge_i+1] - BATTERY_MILESTONES[charge_i]
            lin_ = (current_voltage - BATTERY_MILESTONES[charge_i])/lin
            new['battery_charge'] = round((charge_i + lin_)/10, 2)

        try:
            new['battery_charge'] = round(new['battery_charge'], 2)
            pa = new['atm_pressure'] * 100
            po = atmospheric_pressure_reference_ * 100
            t_ = new['atm_temperature']

            new['relative_altitude'] = \
                -(log(pa / po) * pa) / (((pa * M) / (R * (T + t_))) * g)
        except Exception:
            pass

        try:
            new['force'] = [
                round(new['acceleration'][0] * m, 4),
                round(new['acceleration'][1] * m, 4),
                round(new['acceleration'][2] * m, 4)
            ]

            new['compass'] = atan2(new['magnetometer'][0], new['magnetometer'][1])
            while True:
                if new['compass'] < 0:
                    new['compass'] += 2 * pi
                elif new['compass'] >= 2 * pi:
                    new['compass'] -= 2 * pi
                else:
                    break
            new['compass'] = round(new['compass'], 6)
        except Exception:
            pass

        to_pop = 0
        for item in rad_times:
            if item + 60 < new['time']:
                to_pop += 1
        for i in range(to_pop):
            rad_clicks.pop(0)
            rad_times.pop(0)
        try:
            rad_clicks.append(new['rad_click'])
            rad_times.append(new['time'])
        except Exception:
            pass
        if len(rad_clicks) == 0: 
            new["rad_cmp"] = 0
        else:
            new['rad_cmp'] = sum(rad_clicks)

        if 'time' not in last_data_.keys():
            last_data_ = new.copy()

        if last_data_['time'] < new['time']:
            new['fall_speed'] = round((last_data_['relative_altitude'] -
                                      new['relative_altitude']) /
                                      (new['time'] - last_data_['time']), 2)
            if new['fall_speed'] == 0:
                new['time_to_land'] = 0
            elif new['fall_speed'] < 0:
                new['time_to_land'] = False
            else:
                new['time_to_land'] = round(new['relative_altitude'] /
                                            new['fall_speed'], 2)
            new['momentum'] = round(new['fall_speed'] * m, 2)
            last_data_ = new.copy()

        new['relative_altitude'] = round(new['relative_altitude'], 2)
    except NameError as err:
        archive_error(repr(err), path)
        new['errors'].append(repr(err))
    except KeyError as err:
        archive_error(repr(err), path)
        new['errors'].append(repr(err))
    except ZeroDivisionError as err:
        archive_error(repr(err), path)
        new['errors'].append(repr(err))

    try:
        return new, last_data_, new['atm_pressure']
    except KeyError:
        new["errors"].append("Invalid data")
        return new, last_data, 0


def receive_data() -> str:
    try:
        ser = Serial(PORT, BAUD_RATE)
        try:
            new = ser.readline()
            return str(new)
        except Exception as err:
            print(err)
            return ''
        finally:
            ser.close()
    except Exception as err:
        archive_error(repr(err), path)
        return ''


def format_seconds(time: int, textify: bool = False) -> \
        Union[str, Tuple[int, int, int]]:
    hour = int(time//(60*60))
    minute = int((time-hour*60*60)//60)
    second = int(time-hour*60*60-minute*60)
    if textify:
        return f'{hour}:{0 if minute < 10 else ""}{minute}:' \
               f'{0 if second < 10 else ""}{second}'
    else:
        return hour, minute, second


def init() -> Tuple[str, int]:
    if REPLAY:
        global REPLAY_CONNECTION
        REPLAY_CONNECTION = open(REPLAY_SRC, 'r')
        for _ in range(REPLAY_TIME):
            line = REPLAY_CONNECTION.readline()
            if not line:
                break


    path_: str = getcwd()
    init_now: datetime = datetime.now()
    init_date: Dict[str, Union[str, int]] = {
        'day': init_now.strftime("%d"),
        'month': init_now.strftime("%m"),
        'year': init_now.strftime("%Y"),
        'hour': init_now.strftime("%H"),
        'minute': init_now.strftime("%M"),
        'second': init_now.strftime("%S")
    }
    init_t: int = int(init_date["second"]) + int(
        init_date["minute"]) * 60 + int(init_date["hour"]) * 60 * 60
    load_pressure()

    try:
        mkdir(path_ + '\\storage')
    except FileExistsError:
        pass
    path_ += f'\\storage\\{init_date["day"]}_{init_date["month"]}_'\
             f'{init_date["year"]}_{init_date["hour"]}_{init_date["minute"]}_'\
             f'{init_date["second"]}'
    try:
        mkdir(path_)
    except FileExistsError:
        pass

    base_info = {
        'port': PORT,
        'baud_rate': BAUD_RATE,
        'date': init_date,
        'init_time': init_t}
    with open(path_ + "\\header.json", "w") as ot_file:
        dump(base_info, ot_file)

    with open(path_ + "\\track.gpx", "w") as ot_file:
        ot_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
        ot_file.write('<gpx version="1.1" creator="Momentum-Team">\n')
        ot_file.write('  <metadata>\n')
        ot_file.write('    <name>CanSat Tracker</name>\n')
        ot_file.write('    <desc>Path of Momentum CanSat during finale of CanSat competition</desc>\n')
        ot_file.write('    <author><name>Momentum-Team</name></author>\n')
        ot_file.write('  </metadata>\n')
        ot_file.write('\n')
        ot_file.write('  <trk>\n')
        ot_file.write(f'    <name>CanSat Path {get_time(organize=True, textify=True, date=True)}</name>\n')
        ot_file.write('    <trkseg>\n')

    return path_, init_t


def archive_error(err: str, path_: str) -> None:
    with open(path_ + '\\errors.txt', 'a') as outfile:
        outfile.write(f'{get_time(organize=True, textify=True)}: {err}\n')


def archive_data(new: str, path_: str) -> None:
    new: str = f'{get_time()};{atmospheric_pressure_reference};{new}\n'
    with open(path_ + '\\raw.txt', 'a') as outfile:
        outfile.write(new)
    with open(path_ + '\\backup_raw.txt', 'a') as outfile:
        outfile.write(new)


server = Flask(__name__)
#scheduler = APScheduler()


def refresh():
    if REPLAY:
        org = REPLAY_CONNECTION.readline()
        if not org:
            sleep(60)

        col_i = org.index(';')
        org = org[col_i+1:]
        print(org)
    elif TEST_MODE:
        org = 'a;49.239185;16.554634;430;1;4.01;26.11;25.05;122;b;982.1;27.1;8;155;0.02;12;1.2;0.2;1.2;0;0.2;0.05;12;5;1;11;8;12.2;3.14;6.28;0;e'
    else:
        org = receive_data()
        org = org[2:-1]
    archive_data(org, path)
    dat = process_data(org, [])
    if len(dat['errors']) == 0:
        global last_data, last_pressure
        dat, last_data, last_pressure = \
            calculate_from_data(dat, last_data, init_time,
                                atmospheric_pressure_reference, path)

    global distributed_data
    keys_to_copy = [
        'latitude', 'longitude', 'altitude', 'sat_count', 'battery_voltage', 
        'battery_temperature', 'board_temperature',
        'atm_pressure', 'atm_temperature', 'atm_humidity', 'atm_co2_eq',
        'atm_co2_voc', 'atm_iaq', 'g_force', 'gyroscope', 'acceleration',
        'magnetometer', 'orientation', 'force', 'time', 'real_time',
        'reference_pressure', 'compass', 'relative_altitude', 'map',
        'fall_speed', 'time_to_land', 'momentum', 'battery_charge'
    ]

    distributed_data['errors'] = dat['errors']
    for key in keys_to_copy:
        if key in dat.keys():
            if dat[key] is not None:
                distributed_data[key] = dat[key]


@server.route('/data')
def data():
    refresh()
    return dumps(distributed_data)


@server.route('/set_pressure')
def set_pressure():
    global atmospheric_pressure_reference
    atmospheric_pressure_reference = distributed_data["atm_pressure"]

    with open(f"reference.json", "w") as file:
        dump(last_pressure, file)
    return dumps({"error": False})


@server.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    path, init_time = init()

    if TEST_MODE:
        server.run(debug=True, use_reloader=False)
    else:
        server.run()
