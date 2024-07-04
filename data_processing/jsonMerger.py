SRCSTART = './fragments/raw'
SRCEND = '.txt'

OUT = './data/raw.txt'


with open(OUT, 'w') as out_file:
    i = 0
    while True:
        try:
            with open(SRCSTART + str(i) + SRCEND, 'r') as src_file:
                while True: 
                    line = src_file.readline()
                    if not line:
                        break
                        
                    out_file.write(line)
            
            i += 1
        except FileNotFoundError:
            print(i)
            break
    