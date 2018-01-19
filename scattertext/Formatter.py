def large_int_format(x):
	num = round_downer(x)
	if 1000000000 <= num:
		return str(num // 1000000000) + 'b'
	elif 1000000 <= num < 1000000000:
		return str(num // 1000000) + 'mm'
	elif 1000 <= num < 1000000:
		return str(num // 1000) + 'k'
	else:
		return str(num)


def round_downer(x):
	power_of_ten = 10 ** (len(str(int(x))) - 1)
	num = power_of_ten * (x // power_of_ten)
	return num
