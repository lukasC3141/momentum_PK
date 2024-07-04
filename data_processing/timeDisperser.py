SRC = './data/clean.txt'
OUT = './data/dispersed.txt'

stack = []
stack_time = -1


def write_stack():
    with open(OUT, 'a') as ot_file:
        t = 0
        ln = len(stack)
        for row in stack:
            t += 1
            row[0] = str(round(float(row[0]) + t*1/ln, 2))
            ot_file.write(';'.join(row))


with open(OUT, 'w') as out_file:
    out_file.close()

with open(SRC, 'r') as src_file:
    while True:
        line = src_file.readline()
        if not line:
            write_stack()
            break

        time = line.split(';')[0]
        if time != stack_time:
            write_stack()
            stack = []
            stack_time = time
        stack.append(line.split(';'))
