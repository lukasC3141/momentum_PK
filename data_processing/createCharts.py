import pandas
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from typing import Tuple, List


"""PURPLE = '#742FFF'
YELLOW = '#FAFF00'"""

BACKGROUND = '#000000'
ACTIVE = '#FFFFFF'

SRC = './data/autoDataframe.pkl'

TESTING = False

#plt.rcParams["font.family"] = "bahnschrift"


def load_dataframe():
    df = pandas.read_pickle(SRC)
    return df


def create_line_chart_3d(*args: Tuple[str, List, List, List, str, float, bool], x_label='', y_label='', z_label='',
                         background: str = BACKGROUND, active: str = ACTIVE, title: str = "",
                         transparent: bool = False, legend: bool = True,
                         save: bool = True, file: str = '', show: bool = TESTING, svg: bool = not TESTING,
                         grid: bool = True, planes: bool = True) -> None:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(background)
    ax.set_facecolor(background)
    ax.set_title(title)

    ax.xaxis.set_major_formatter(FormatStrFormatter('%.5f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.5f'))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_zlabel(z_label)
    ax.xaxis.label.set_color(active)
    ax.yaxis.label.set_color(active)
    ax.zaxis.label.set_color(active)
    ax.tick_params(color=active, labelcolor=active)
    for spine in ax.spines.values():
        spine.set_edgecolor(active)

    if not planes:
        ax.xaxis.pane.fill = planes
        ax.yaxis.pane.fill = planes
        ax.zaxis.pane.fill = planes

        ax.xaxis.pane.set_edgecolor('w')
        ax.yaxis.pane.set_edgecolor('w')
        ax.zaxis.pane.set_edgecolor('w')
    ax.grid(grid)

    lines = None
    for arg in args:
        line = ax.plot(arg[1], arg[2], arg[3], label=arg[0], c=arg[4], linewidth=arg[5])

        if lines is None:
            lines = line
        else:
            lines += line

    if legend:
        labs = [str(li.get_label()) for li in lines]
        ax.legend(lines, labs)

    fig.tight_layout()

    if save and file != '':
        if svg:
            plt.savefig(f'./output/{file}.svg', transparent=transparent, format='svg')
        else:
            plt.savefig(f'./output/{file}.png', transparent=transparent, format='png')
    if show:
        plt.show()


def create_line_chart(*args: Tuple[str, List, List, str, float, bool], x_label='', y_label='',
                      twin: bool = False, twin_label: str = '', transparent: bool = False, legend: bool = True,
                      background: str = BACKGROUND, active: str = ACTIVE, title: str = "",
                      save: str = True, file: str = '', show: str = TESTING, svg: bool = True) -> None:
    fig, ax = plt.subplots()
    fig.set_facecolor(background)
    ax.set_facecolor(background)
    ax.set_title(title, c=active)

    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.xaxis.label.set_color(active)
    ax.yaxis.label.set_color(active)
    ax.tick_params(color=active, labelcolor=active)
    for spine in ax.spines.values():
        spine.set_edgecolor(active)

    if twin:
        ax2 = ax.twinx()
        ax2.tick_params(color=active, labelcolor=active)
        ax2.set_ylabel(twin_label)
        ax2.yaxis.label.set_color(active)
        for spine in ax2.spines.values():
            spine.set_edgecolor(active)
    else:
        ax2 = None

    lines = None
    for arg in args:
        if arg[5] and twin:
            line = ax2.plot(arg[1], arg[2], label=arg[0], c=arg[3], linewidth=arg[4])
            ax2.tick_params(color=arg[3], labelcolor=arg[3])
            ax2.yaxis.label.set_color(arg[3])
        else:
            line = ax.plot(arg[1], arg[2], label=arg[0], c=arg[3], linewidth=arg[4])

        if '_avg' in arg[0]:
            pass
        elif lines is None:
            lines = line
        else:
            lines += line
    #plt.tick_params(axis='x', colors=YELLOW, direction='out', length=0, width=0)
    #plt.tick_params(axis='y', colors=YELLOW, direction='out', length=0, width=0)
    #plt.xlabel(x_label, fontweight='bold', color=ACTIVE, fontsize='17', horizontalalignment='center')
    #plt.ylabel(y_label, fontweight='bold', color=ACTIVE, fontsize='17', horizontalalignment='center')

    if legend:
        labs = [li.get_label() for li in lines]
        ax.legend(lines, labs)

    fig.tight_layout()

    if save and file != '':
        if svg:
            plt.savefig(f'./output/{file}.svg', bbox_inches='tight', transparent=transparent, format='svg')
        else:
            plt.savefig(f'./output/{file}.png', bbox_inches='tight', transparent=transparent, format='png')
    if show:
        plt.show()


dataf = load_dataframe()


"""create_line_chart(
                  ('Board', dataf['flight_time'].tolist(), dataf['board_temperature'].tolist(), '#00ff00', 1, False),
                  ('Atmospheric', dataf['flight_time'].tolist(), dataf['atm_temperature'].tolist(), '#ff0000', 1, True),
                  ('Battery', dataf['flight_time'].tolist(), dataf['battery_temperature'].tolist(), '#0000ff', 1, False),
                  twin=False, legend=True, file='Temperatures2', x_label='Time (s)', y_label=r'Temperature ($^\circ$C)',
                  twin_label=r'Temperature ($^\circ$C)', svg=True, title="Temperatures")"""
'''create_line_chart_3d(('Position', dataf['latitude'].tolist(), dataf["longitude"].tolist(),
                      dataf["altitude"].tolist(), '#ff0000', 1, False),
                     legend=False, file='Position', transparent=True, svg=True,
                     x_label=r'Latitude', y_label='Longitude', z_label='Altitude', planes=False, grid=False)'''
"""create_line_chart(('Charge', dataf["time"].tolist(), dataf['battery_charge'].tolist(), '#00ff00', 1, False),
                  ('Charge_avg', dataf["time"].tolist(), dataf['battery_charge_avg'].tolist(), '#00ff77', 2, False),
                  ('Voltage_avg', dataf["time"].tolist(), dataf['battery_voltage_avg'].tolist(), '#ff0077',  2, True),
                  ('Voltage', dataf["time"].tolist(), dataf['battery_voltage'].tolist(), '#ff0000',  1, True),
                  legend=True, file="Battery", title="Battery",
                  x_label=r'Time (s)', y_label="Charge", twin=True, twin_label="Voltage")

create_line_chart(
                  ('x', dataf['flight_time'].tolist(), dataf['g_force_x'].tolist(), '#00ff00', 1, False),
                  ('z', dataf['flight_time'].tolist(), dataf['g_force_y'].tolist(), '#ff0000', 1, False),
                  ('y', dataf['flight_time'].tolist(), dataf['g_force_z'].tolist(), '#0000ff', 1, False),
                  twin=False, legend=True, file='Gforces', x_label='Time (s)', y_label=r'Force (G)',
                  twin_label=r'Temperature ($^\circ$C)', svg=True, title="G force")
create_line_chart(
                  ('x', dataf['flight_time'].tolist(), dataf['acceleration_x'].tolist(), '#00ff00', 1, False),
                  ('z', dataf['flight_time'].tolist(), dataf['acceleration_y'].tolist(), '#ff0000', 1, False),
                  ('y', dataf['flight_time'].tolist(), dataf['acceleration_z'].tolist(), '#0000ff', 1, False),
                  twin=False, legend=True, file='Acceleration', x_label='Time (s)', y_label=r'Acceleration ($m*s^2$)',
                  twin_label=r'Temperature ($^\circ$C)', svg=True, title="Acceleration")
create_line_chart(
                  ('x', dataf['flight_time'].tolist(), dataf['gyroscope_x'].tolist(), '#00ff00', 1, False),
                  ('z', dataf['flight_time'].tolist(), dataf['gyroscope_y'].tolist(), '#ff0000', 1, False),
                  ('y', dataf['flight_time'].tolist(), dataf['gyroscope_z'].tolist(), '#0000ff', 1, False),
                  ('compass', dataf['flight_time'].tolist(), dataf['compass'].tolist(), '#ff00ff', 1, True),
                  twin=True, legend=True, file='Gyroscope', x_label='Time (s)', y_label=r'Rotation ($^\circ$/s)',
                  twin_label=r'', svg=True, title="Gyroscope")

create_line_chart(
                  ('uv', dataf['flight_time'].tolist(), dataf['uv'].tolist(), '#00ff00', 1, False),
                  ('light', dataf['flight_time'].tolist(), dataf['light'].tolist(), '#ff0000', 1, True),
                  ('rad_cmp', dataf['flight_time'].tolist(), dataf['rad_cmp'].tolist(), '#0000ff', 1, False),
                  twin=True, legend=True, file='Radiation', x_label='Time (s)', y_label=r'Light (LUX), Alpha + Beta (cmp)',
                  twin_label=r'', svg=True, title="Radiation")"""

create_line_chart(
                  ('uv', dataf['flight_time'].tolist(), dataf['sat_count'].tolist(), '#00ff00', 1, False),
                  twin=False, legend=False, file='GPS_comm', x_label='Time (s)', y_label=r'Satelites',
                  twin_label=r'', svg=True, title="GPS Connection")

"""create_line_chart(
                  ('humidity', dataf['flight_time'].tolist(), dataf['atm_humidity'].tolist(), '#00ff00', 1, True),
                  ('iaq', dataf['flight_time'].tolist(), dataf['atm_iaq'].tolist(), '#ff0000', 1, False),
                  ('co2 eq', dataf['flight_time'].tolist(), dataf['atm_co2_eq'].tolist(), '#0000ff', 1, False),
                  twin=True, legend=True, file='Air', x_label='Time (s)', y_label=r'CO2 (ppm), iaq',
                  twin_label=r'Humidity (%)', svg=True, title="Air")"""





# r"Radiation ($MJ\,m^{-2}\,d^{-1}$)"
