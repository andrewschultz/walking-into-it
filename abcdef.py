import re

begin_string = 'abc'
end_string = 'def'

def case_keep_replace(my_string, begin_string = 'abc', end_string = 'def'):
	offsets = [m.start() for m in re.finditer(begin_string, my_string, re.IGNORECASE)]
	for x in offsets:
		temp_string = ''
		for y in range(0, len(begin_string)):
			if my_string[x+y].islower():
				temp_string += end_string[y]
			else:
				temp_string += end_string[y].upper()
		my_string = my_string[:x] + temp_string + my_string[x + len(temp_string):]
	return my_string

def cap_preserving_replace(my_string, from_substring, to_substring):
    temp = my_string.replace(from_substring.lower(), to_substring.lower())
    temp = temp.replace(from_substring.upper(), to_substring.upper())
    temp = temp.replace(from_substring.title(), to_substring.title())
    return temp

process_string = "All 8: abc, abC, aBc, aBC, Abc, AbC, ABc, ABC."

print("BEFORE:", process_string)
print(" AFTER:", case_keep_replace(process_string))
print("INCAPS:", cap_preserving_replace(process_string, 'abc', 'def'))
