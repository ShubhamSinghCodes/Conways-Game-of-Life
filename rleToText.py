class RunLengthEncodedParser:
    def __init__(self, rle_string):
        self.rle_string = rle_string
        self.pattern_raw = ""
        # Fill in instance attributes by parsing the raw strings
        self.pattern_raw = "".join([line.strip(" \n\r\t") for line in self.rle_string.strip().splitlines() if not line.startswith("#")])





    def new_populate_pattern(self, pattern_raw, pads=0, padl=0, pade=0, padle=0):
        pattern = []
        pattern_rows = pattern_raw.rstrip("!").split("$")
        pattern_str = ".\n" * pads
        yield pattern_str
        for y in range(len(pattern_rows)):
            pattern.append([])
            tmp_num_str = ""
            rowstr = ""
            for c in pattern_rows[y]:
                if self.isdigit(c):
                    tmp_num_str += c
                else:
                    if tmp_num_str == "":
                        num_cells = 1
                    else:
                        num_cells = int(tmp_num_str)
                    rowstr += str("." if c == "b" else "O") * num_cells
                    # reset count until another number is encountered
                    tmp_num_str = ""
            print(len(pattern_rows) - y)
            yield ("." * padl) + rowstr + ("." * padle) + '\n'
            if tmp_num_str != "":
                print("splitting")
                yield (int(tmp_num_str)-1)*"\n"
        return ".\n" * pade

    def isdigit(self, c):
        """Returns True is the character is a digit"""
        return '0' <= c <= '9'


    def __str__(self):
        return self.rle_string

filepath = input("Enter filepath: ")
pads = int(input("Enter padding at start of pattern: "))
padl = int(input("Enter padding at start of each line: "))
pade = int(input("Enter padding at end of pattern: "))
padle = int(input("Enter padding at end of each line: "))
rlefilepath = "seeds/"+ filepath + ".txt"
filepath = "seeds/"+ filepath + ".rle"
with open(filepath, encoding='utf-8') as rlefile:
    writer = RunLengthEncodedParser(rlefile.read())
    with open(rlefilepath,'x') as savefile:
        for row in writer.new_populate_pattern(writer.pattern_raw,pads,padl,pade,padle):
            savefile.write(row)
            print(row)
        savefile.close()
