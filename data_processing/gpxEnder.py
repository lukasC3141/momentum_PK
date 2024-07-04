SRC = './data/track.gpx'


with open(SRC, 'a') as file:
    file.write('    </trkseg>\n')
    file.write('  </trk>\n')
    file.write('</gpx>')
