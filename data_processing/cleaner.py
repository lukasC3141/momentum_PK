import re


SRC = './data/numeric.txt'
OUT = './data/clean.txt'
REST_OUT = "./data/cleaner_trash.txt"

F = '(-)?[0-9]+(\\.[0-9]+)?'
INT = '(-)?[0-9]+'

DATA = f'^{INT};{F};{F};{F};{INT};{INT};{F};{F};{F};{F};{F};{INT};' \
       f'{F};{F};{INT};{INT};{F};{INT};{F};{F};{F};{F};{F};{F};{F};{F};{F};{F};{F};{F};{F};{F};{F}$'
PATTERN = re.compile(DATA)


with open(SRC, 'r') as src_file:
    with open(OUT, 'w') as out_file:
        with open(REST_OUT, "w") as trash_file:
            while True:
                line = src_file.readline()
                if not line:
                    break

                line = line.replace('\n', '')
                if PATTERN.match(line):
                    out_file.write(line + '\n')
                else:
                    trash_file.write(line + '\n')
