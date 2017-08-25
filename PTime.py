import re

def getTime(s):
	t = re.findall(r', (\S*) (\S*) [0-9]+ (.{2}).(.{2})[^\+-]*([\+-])([0-9]{2})(.*)', str(s))[0]
	d = int(t[0])
	mstr = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	m = mstr[t[1]]
	h = int(t[2])
	mm = int(t[3])
	f = t[4]
	t5 = int(t[5]) if f == '+' else -int(t[5])
	t6 = int(t[6]) if f == '+' else -int(t[6])
	return getTime_(d, m, h, mm, f, t5, t6)

def genUnix(s):
	import datetime
	t = re.findall(r'([^-]*)-([^-]*)-([^-]*) ([^:]*):([^:]*):([^:]*)', str(datetime.datetime.fromtimestamp(float(s))))[0]
	d = int(t[2])
	m = int(t[1])
	h = int(t[3])
	mm = int(t[4])
	f = '+'
	t5 = 9
	t6 = 0
	return getTime_(d, m, h, mm, f, t5, t6)

def getTime_(d, m, h, mm, f, t5, t6):
	import win32timezone
	import re
	dt = re.findall(r'-([0-9]+)-([0-9]+)[^\+-]*([\+-])([0-9]+):([0-9]+)', str(win32timezone.now()))[0]
	ym = int(dt[0])
	yd = int(dt[1])
	g = dt[2]
	r5 = int(dt[3]) if g == '+' else -int(dt[3])
	r6 = int(dt[4]) if g == '+' else -int(dt[4])
	h -= t5 - r5
	mm -= t6 - r6
	if mm < 0:
		h -= 1
		mm += 60
	elif mm >= 60:
		h += 1
		mm -= 60
	if h > 23:
		d += 1
		h -= 24
	elif h < 0:
		d -= 1
		h += 24
	if m == ym and d == yd:
		return str(h).zfill(2) + ':' + str(mm).zfill(2)
	else:
		return str(m) + '/' + str(d)