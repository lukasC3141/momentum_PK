from flask import Flask, render_template
from json import dumps, dump, load
import serial
from datetime import datetime
import os
import math

#setting path to folders with forntend
templates_directory = os.path.abspath('./react-app/build') 
static_directory = os.path.abspath('./react-app/build/static')





# variables
atmospheric_pressure_reference: list = [1000, 1000, 1000]
last_pressure: list = []
T: float = 273.15
R: float = 8.31432
M: float = 0.02896
g: float = 9.81
m: dict = {
    0: 0.32
}

port = 'COM5'
baud_rate: int = 115200
size_of_arch_files: int = 30
test_mode: bool = True

# initianilizing time, date and path settings

path: str = os.getcwd()
n_file: int = 0
init_now = datetime.now()
init_date: dict = {
    'day': init_now.strftime("%d"),
    'month': init_now.strftime("%m"),
    'year': init_now.strftime("%Y"),
    'hour': init_now.strftime("%H"),
    'minute': init_now.strftime("%M"),
    'second': init_now.strftime("%S")
}
init_time: int = int(init_date["second"]) + int(init_date["minute"])*60 + \
                 int(init_date["hour"])*60*60
last_time: int = init_time
last_data: dict = {}
path += f'/storage/{init_date["day"]}_{init_date["month"]}_' \
        f'{init_date["year"]}_{init_date["hour"]}_{init_date["minute"]}_{init_date["second"]}'

# make directories in storage dir

try:
    os.mkdir(path)
    os.mkdir(path+'/archives')
    os.mkdir(path+'/archives_backup')
    os.mkdir(path+'/workplace')
    path = path

    with open(f"{path}/workplace/main_arch.json", "w") as ot_file:
        dump([], ot_file)
    with open(f"{path}/workplace/backup_arch.json", "w") as ot_file:
        dump([], ot_file)

    base_info = {
        'port': port,
        'baud_rate': baud_rate,
        'date': init_date,
        'init_time': init_time}

    with open(path + "/header.json", "w") as ot_file:
        dump(base_info, ot_file)
except FileExistsError as er:
    print(er)
except Exception as er:
    print(er)
    exit()

del init_now
del init_date

# get time and set processed data

def get_time() -> int:
    now = datetime.now()
    return (int(now.strftime("%S")) + int(now.strftime("%M"))*60 +
            int(now.strftime("%H"))*60*60)


def process_data(dat: str) -> dict:
    processed: dict = {
        0: {"error": False}
    }

    try:
        sliced: list = dat.split(';')
    except ValueError as err:
        print(err)
        processed[0]['error']: bool = True
        return processed

    # processing data from rocket

    try:
        p_index: int = sliced.index('-')
        temperature: str = sliced[p_index + 1]
        pressure: str = sliced[p_index + 2]
        reference_height: str = sliced[p_index + 3]
        voltage: str = sliced[p_index + 4]

        processed[0]['temperature']: float = float(temperature)
        processed[0]['pressure']: float = float(pressure)
        processed[0]['reference_height']: float = float(reference_height)
        processed[0]['voltage']: float = float(voltage)

        if not sliced[p_index + 5][0] == 'e':
            processed[0]['error']: bool = True
    except ValueError as err:
        processed[0]['error']: bool = True
        print(err)

    processed[0]['time']: int = get_time()

    return processed

# function for recieving data

def receive_data() -> dict:
    try:
        ser = serial.Serial(port, baud_rate)
        new = ser.readline()
        proc = process_data(str(new))
        ser.close()
        return proc
    except Exception as err:
        print(err)
        return {
            0: {"error": True},
            1: {"error": True},
            2: {"error": True},
        }


def get_hour_from_time(time: int) -> str:
    hour = time//(60*60)
    minute = (time-hour*60*60)//60
    second = time-hour*60*60-minute*60
    return f'{hour}:{minute}:{second}'

# calculate and refresh data

def calculate_and_refresh_data(new: dict) -> dict:
    global last_data, last_pressure, atmospheric_pressure_reference
    time = get_time()
    new[0]['time'] = time - init_time
    last_pressure = [
        -1
    ]
    new[0]['pressure_reference'] = atmospheric_pressure_reference[0]

    try:
        last_pressure[0] = new[0]['pressure']
        if last_data[0]['time'] == new[0]['time'] - 1:
            new[0]['speed_of_fall'] = abs(last_data[0]['reference_height'] - new[0]['reference_height'])
            new[0]['momentum'] = new[0]['speed_of_fall'] * m[0]
        else:
            new[0]['speed_of_fall'] = last_data[0]['speed_of_fall']
            new[0]['momentum'] = last_data[0]['momentum']
    except KeyError as err:
        print(err)

    last_data = new
    archive_data(new)

    return new

# archives data to workplace and main arch

def archive_data(new: dict):
    lis: list
    try:
        with open(path + "/workplace/main_arch.json", "r") as outfile:
            lis = load(outfile)
    except Exception as err:
        print(err)
        try:
            with open(path + "/workplace/backup_arch.json", "r") as \
                    outfile:
                lis = load(outfile)
        except Exception as err:
            print(err)
            lis = []
    lis.append(new)

    # archive of small parts or get lis in json main_arch

    if len(lis) >= size_of_arch_files:
        global n_file
        with open(path + "/workplace/main_arch.json", "w") as outfile:
            dump([], outfile)
        with open(path + "/workplace/backup_arch.json", "w") as outfile:
            dump([], outfile)

        with open(path + f"/archives/{n_file}.json", "w") as outfile:
            dump(lis, outfile)
        with open(path + f"/archives_backup/{n_file}.json", "w") as outfile:
            dump(lis, outfile)

        n_file += 1
    else:
        with open(path + "/workplace/main_arch.json", "w") as outfile:
            dump(lis, outfile)
        with open(path + "/workplace/backup_arch.json", "w") as outfile:
            dump(lis, outfile)


server = Flask(__name__,
    template_folder=templates_directory,
    static_folder=static_directory)


@server.route('/set_pressure')
def set_pressure():
    global atmospheric_pressure_reference

    atmospheric_pressure_reference = [None, None, None]
    try:
        atmospheric_pressure_reference[0] = last_pressure[0]
    except Exception as err:
        print(err)
        print("critical error measuring pressure \n pressure not recorded")
        return dumps({"error": True})

    with open(f"reference.json", "w") as file:
        dump(last_pressure, file)

    return dumps({"error": False})


@server.route('/load_pressure')
def load_pressure():
    global last_pressure
    try:
        with open(f"reference.json", "r") as file:
            pressure = list(load(file))

            global atmospheric_pressure_reference
            atmospheric_pressure_reference = pressure
            last_pressure = pressure
    except FileNotFoundError as err:
        print(err)
        with open(f"reference.json", "w") as file:
            dump(last_pressure, file)

    return dumps({"error": False})


@server.route('/data')
def data():
    if test_mode:
        new = process_data('-;27.76;1082.63;2.67;4.01;e')
        dat = calculate_and_refresh_data(new)
    else:
        new = receive_data()
        dat = calculate_and_refresh_data(new)
    return dumps(dat)


@server.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    server.run(debug=True)
