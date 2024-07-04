import pandas
from math import atan2, pi, log
from typing import Tuple, Union, List, Dict


M: float = 1000
m: float = 0.32
T: float = 273.15
R: float = 8.31432
g: float = 9.81
BATTERY_MILESTONES: Tuple = (2.5, 3.51, 3.6, 3.63, 3.65, 3.7, 3.74, 3.8, 3.87, 3.96)

COLUMNS = ['time', 'reference_pressure', 'latitude', 'longitude', 'altitude', 'sat_count', 'battery_voltage', 'uv',
           'light', 'battery_temperature', 'board_temperature', 'rad_clicks',
           'atm_pressure', 'atm_temperature', 'atm_humidity', 'atm_co2_eq', 'atm_co2_voc', 'atm_iaq',
           'g_force_x', 'g_force_y', 'g_force_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z',
           'acceleration_x', 'acceleration_y', 'acceleration_z', 'magnetometer_x', 'magnetometer_y', 'magnetometer_z',
           'orientation_x', 'orientation_y', 'orientation_z']
AVG_KEYS = ['latitude', 'longitude', 'altitude', 'sat_count', 'battery_voltage', 'uv',
           'light', 'battery_temperature', 'board_temperature', 'rad_clicks',
           'atm_pressure', 'atm_temperature', 'atm_humidity', 'atm_co2_eq', 'atm_co2_voc', 'atm_iaq',
           'g_force_x', 'g_force_y', 'g_force_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z',
           'acceleration_x', 'acceleration_y', 'acceleration_z', 'magnetometer_x', 'magnetometer_y', 'magnetometer_z',
           'orientation_x', 'orientation_y', 'orientation_z', 
           
           "force_x", "force_y", "force_z", "compass", "battery_charge", "relative_altitude", "fall_speed", "momentum"]

SRC = './data/dispersed.txt'
OUT = './data/autoDataframe.pkl'


def save_dataframe(df) -> None:
    df.to_pickle(OUT)


def ground_compass(x: float) -> float:
    while True:
        if x < 0:
            x += 2 * pi
        elif x >= 2 * pi:
            x -= 2 * pi
        else:
            return x


def get_battery_charge(x: float) -> float:
    charge_i = 0
    for milestone in BATTERY_MILESTONES:
        if milestone < x:
            charge_i += 1
        else:
            break

    if charge_i+1 >= len(BATTERY_MILESTONES):
        return 1
    else:
        lin = BATTERY_MILESTONES[charge_i+1] - BATTERY_MILESTONES[charge_i]
        lin_ = (x - BATTERY_MILESTONES[charge_i])/lin
        return round((charge_i + lin_)/10, 2)


def remove_noise(x: str) -> str:
    x = x.replace('\\r\\n', '')
    return x


def get_relative_altitude(po: float, pa: float, t: float) -> float:
    #pa = float(atmo_pressure * 100)
    #po = float(reference_pressure * 100)
    #t = float(atmo_temperature)

    return -(log(pa*100 / po*100) * pa*100) / (((pa*100 * M) / (R * (T + t))) * g)


dataf = pandas.read_csv(SRC, sep=';', names=COLUMNS)
min_time = dataf['time'].min()
dataf['flight_time'] = dataf['time'] - min_time

dataf['force_x'] = dataf['acceleration_x'] * m
dataf['force_y'] = dataf['acceleration_y'] * m
dataf['force_z'] = dataf['acceleration_z'] * m

dataf['compass'] = dataf.apply(lambda x: atan2(x.magnetometer_x, x.magnetometer_y), axis=1)
dataf['compass'] = dataf['compass'].apply(ground_compass)
dataf['battery_charge'] = dataf['battery_voltage'].apply(get_battery_charge)
dataf['relative_altitude'] = dataf.apply(
    lambda x: get_relative_altitude(x.reference_pressure, x.atm_pressure, x.atm_temperature), axis=1)

dataf.loc[dataf['altitude'] == 0, 'altitude'] = dataf['relative_altitude']

dataf['delta_time'] = dataf['time'].diff(1).fillna(0)
dataf['delta_altitude'] = dataf['altitude'].diff(-1).fillna(0)
dataf['fall_speed'] = dataf['delta_altitude'].divide(dataf['delta_time'])
dataf['time_to_land'] = dataf['altitude'].divide(dataf['fall_speed'])
dataf['momentum'] = dataf['fall_speed'] * m


for avg_key in AVG_KEYS:
    dataf[avg_key + "_avg"] = (dataf[avg_key] + 
                               dataf[avg_key].add(dataf[avg_key].shift(1)).add(dataf[avg_key].shift(-1)) +
                               dataf[avg_key].add(dataf[avg_key].shift(1)).add(dataf[avg_key].shift(-1))
                               .add(dataf[avg_key].shift(2)).add(dataf[avg_key].shift(-2))
                               ) / 9
    

dataf["rad_cmp"] = dataf["rad_clicks"].tail(120).sum()


print(dataf)
save_dataframe(dataf)
