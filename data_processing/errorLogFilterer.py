import re


SRC = "./data/errors.txt"
OUT = "./output/filteredErrors.txt"
REST_OUT = "./data/error_trash.txt"

FILTER = (
    (".*SerialException.*COM6.*", 2),
)
PATTERNS = ((re.compile(pat[0]), pat[1]) for pat in FILTER)
STRINGS = (("COM6", 2), ("SerialException", 2))


with open(SRC, "r") as src_file:
    with open(OUT, "w") as out_file:
        with open(REST_OUT, "w") as trash_file:
            while True:
                line = src_file.readline()
                print(line)
                if not line:
                    break

                valid = True
                skip = 0
                """for pattern in PATTERNS:
                    print(pattern[0].match(line))
                    if pattern[0].match(line):
                        valid = False
                        skip = pattern[1]
                        break"""
                for st in STRINGS:
                    if st[0] in line:
                        valid = False
                        skip = st[1]
                        
                if valid:
                    out_file.write(line)
                else:
                    trash_file.write(line)
                    ext = False
                    for _ in range(skip):
                        line = src_file.readline()
                        if not line:
                            ext = True
                            break
                        trash_file.write(line)
                    
                    if ext: 
                        break

