SRC = './data/can.txt'
OUT = './data/numeric.txt'


with open(SRC, 'r') as src_file:
    with open(OUT, 'w') as out_file:
        i = 0
        while True:
            line = src_file.readline()
            if not line:
                break
        
            com_i = line.index("a")
            new = line[com_i:]
            n = new.replace("a;", "").replace("b;", "").replace(";e", "")
            
            out_file.write(f"{round(i)};{1.1};{n}")
            i += 0.5
            