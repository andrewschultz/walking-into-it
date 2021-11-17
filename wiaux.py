#
# wiaux.py
# walking into it auxiliary file
#

import re

square = [ '?', ' ', 'X', 'O' ]

def is_board_line(my_string):
    return re.search("^[OX\| ]{5,}$", my_string)

def rot13_string_convert(my_string):
    footer_chunk = "-+-+- "
    mss = my_string.rstrip()
    out_string = ''
    if is_board_line(my_string):
        paren_val = 0
        while len(mss) >= 7:
            paren_val <<= 6
            paren_val += square.index(mss[1]) + square.index(mss[1]) << 2 + square.index(mss[1]) << 4
            mss = mss[7:]
        out_string = "{{}}".format(paren_val)
        if '\n' in my_string:
            out_string += "\n"
        return out_string
    if mss.startswith("{") and mss.endswith("}"):
        this_idx = int(mss[1:-1])
        add_footer = (this_idx > 0)
        this_idx = abs(this_idx)
        footer_length = 0
        while this_idx > 0:
            footer_length += 1
            next_fragment = "{}|{}|{} ".format(square[this_idx & 3], square[(this_idx >> 2) & 3], square[(this_idx >> 4) & 3])
            this_idx >>= 6
            out_string += next_fragment
        out_string = out_string.rstrip()
        if add_footer:
            out_string += ("\n" + (footer_chunk * footer_length).rstrip())
        if '\n' in my_string:
            out_string += "\n"
        return out_string
    try:
        return my_string.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))
    except:
        import string
        rot13 = string.maketrans("ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz", 
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
        return string.translate(my_string, rot13)

# testing
#print(rot13_string_convert("{55}"))
#print(rot13_string_convert("{21}"))
#print(rot13_string_convert("{-39}"))
print(rot13_string_convert("Testing"))
print(rot13_string_convert("This is a test."))

def rot13_file_convert(file_name):
    out_file = rot13_string_convert(file_name)
    fout = open(out_file, "w")
    with open(file_name) as file:
        for (line_count, line) in enumerate (file, 1):
            if look_ahead:
                if line.startswith("-+"):
                    reserve_write = reserve_write[0] + '-' + reserve_write[1:]
                    fout.write(reserve_write)
                    continue
                else:
                    fout.write(reserve_write)
            if is_board_line(line):
                look_ahead = True
                reserve_write = rot13_string_convert(line)
                continue
            fout.write(rot13_string_convert(line))
    fout.close()
