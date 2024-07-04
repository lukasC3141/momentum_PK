SRC = './data/clean.txt'
OUT = './data/cut.txt'

LENGTH = 8
TOLERANCE = 8
PRE_POST = 20


start = -1
stop = -1
i = 0
stack = []


with open(SRC, 'r') as src_file:
    while True:
        line = src_file.readline()
        if not line:
            break

        tim, _, _, _, alt = line.split(';')[:5]
        tim, alt = int(tim), int(alt)
        stack.append((tim, alt))

        to_pop = 0
        for item in stack:
            if item[0] < tim - LENGTH:
                to_pop += 1
            else:
                break
        for p in range(to_pop):
            stack.pop(0)

        vals = [val for key, val in stack]
        if abs(min(vals) - max(vals)) > TOLERANCE:
            if start < 0:
                start = i
            stop = i
        i += 1

start -= PRE_POST
stop += PRE_POST

with open(SRC, 'r') as src_file:
    with open(OUT, 'w') as out_file:
        for i in range(stop + 1):
            line = src_file.readline()
            if not line:
                break
            if i < start:
                continue

            out_file.write(line)
