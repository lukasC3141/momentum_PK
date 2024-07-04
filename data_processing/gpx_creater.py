path_ = "./output/new.gpx"
SRC = "./data/dispersed.txt"


with open(path_, "w") as ot_file:
    ot_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
    ot_file.write('<gpx version="1.1" creator="Momentum-Team">\n')
    ot_file.write('  <metadata>\n')
    ot_file.write('    <name>CanSat Tracker</name>\n')
    ot_file.write('    <desc>Path of Momentum CanSat during finale of CanSat competition</desc>\n')
    ot_file.write('    <author><name>Momentum-Team</name></author>\n')
    ot_file.write('  </metadata>\n')
    ot_file.write('\n')
    ot_file.write('  <trk>\n')
    ot_file.write(f'    <name>CanSat Path {0}</name>\n')
    ot_file.write('    <trkseg>\n')

    i = 0
    with open(SRC, "r") as src_file:
        while True:
            line = src_file.readline()
            if not line:
                break

            splitted = line.split(";")
            latitude, longitude, altitude = splitted[2], splitted[3], splitted[4]
            if float(latitude)*float(longitude)*float(altitude) == 0:
                i += 1
                continue

            ot_file.write(f'      <trkpt lat="{latitude}" lon="{longitude}">\n')
            ot_file.write(f'        <ele>{altitude}</ele>\n')
            ot_file.write(f'        <time>{i}</time>\n')
            ot_file.write(f'      </trkpt>\n')
            i += 1


    ot_file.write('    </trkseg>\n')
    ot_file.write('  </trk>\n')
    ot_file.write('</gpx>')