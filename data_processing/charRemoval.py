SRC = './data/comm.txt'
OUT = './data/numeric.txt'


REPLACE = [("b'a;", ''), ('a;', ''), (';b', ''), (';e\\r\\n', ''), ("'", ''), (";e", ''), ('b', '')]


with open(SRC, 'r') as src_file:
    with open(OUT, 'w') as out_file:
        while True:
            line = src_file.readline()
            if not line:
                break

            for old, new in REPLACE:
                line = line.replace(old, new)

            out_file.write(line)

print('chars')
