#!/usr/bin/python3
#
#

import sys

LIGHTSPEED = 299792
VFACT = 0.922


# usage
if len(sys.argv) < 2:
	print("")
	print(f"USAGE: {sys.argv[0]} FREQ RADIUS OFFSET")
	print("")
	print("    FREQ		Frequency in Mhz")
	print("    OFFSET   Mount-Offset in mm")
	print("    RADIUS   Wire-Radius in mm")
	print("")
	exit(1)

# args
freq = 868.0
if len(sys.argv) > 1:
	freq = float(sys.argv[1])

offset = 3
if len(sys.argv) > 2:
	offset = float(sys.argv[2])

wire = None
if len(sys.argv) > 3:
	wire = float(sys.argv[3])


class simpleDXF():

	xoff = 0.0
	yoff = 0.0
	data = ""

	def __init__(self):
		self.data = "0\nSECTION\n2\nENTITIES\n"

	def offset(self, x=0.0, y=0.0):
		self.xoff = x
		self.yoff = y

	def line(self, x1, y1, x2, y2, layer=0, color=65535):
		self.data += f"0\nLINE\n8\n{layer}\n62\n{color}\n10\n{x1 + self.xoff}\n20\n{y1 + self.yoff}\n11\n{x2 + self.xoff}\n21\n{y2 + self.yoff}\n"

	def arc(self, cx, cy, r, start, stop, layer=0, color=65535):
		self.data += f"0\nARC\n8\n{layer}\n62\n{color}\n10\n{cx + self.xoff}\n20\n{cy + self.yoff}\n40\n{r}\n50\n{start}\n51\n{stop}\n"

	def mtext(self, x, y, h, text, anchor=1, rotate=0, layer=0, color=65535):
		self.data += f"0\nMTEXT\n8\n{layer}\n62\n{color}\n10\n{x + self.xoff}\n20\n{y + self.yoff}\n40\n{h}\n1\n{text}\n71\n{anchor}\n50\n{rotate}\n"

	def print(self):
		self.data += "0\nENDSEC\n0\nEOF\n"
		print(self.data)


def calc(freq=2400.0, off=3.0, wr=None):
	Lambda = LIGHTSPEED / freq
	a = (Lambda * 0.19 * VFACT)
	b = (Lambda * 0.10 * VFACT)
	c = (Lambda * 0.40 * VFACT)
	d = (Lambda * 0.20 * VFACT)
	gap = (Lambda * 0.01 * VFACT)
	r = (Lambda * (0.10 / 3.141592653 ) * VFACT)
	rod = (Lambda / 300)
	total = (Lambda * VFACT)

	if not wr:
		wr = rod / 2

	dxf = simpleDXF()

	# display info
	info = {
		'Freq;Mhz': freq,
		'1/4lambda;mm': Lambda / 4,
		'Total;mm': total,
		'Rod;mm': rod,
	}
	y = r*2 + wr*4 + 18 + (len(info) * 5)
	dxf.mtext(0, y + 9, 5, "Folded-Dipole", anchor=1, layer="info", color=63)
	for key in info:
		name, unit = key.split(";")
		dxf.mtext(0, y, 3, f"{name}", anchor=1, layer="info", color=63)
		dxf.mtext(36, y, 3, f"{round(info[key], 2)}", anchor=3, layer="info", color=63)
		dxf.mtext(38, y, 3, f"{unit}", anchor=1, layer="info", color=63)
		y -= 5

	dxf.offset(d + r + wr*2, 15)

	# wire/rod
	dxf.line(gap, 0, gap + a, 0, layer="wire", color=100)
	dxf.arc(gap + a, r, r, -90, 90, layer="wire", color=100)
	dxf.line(gap + a, r*2, -d, r*2, layer="wire", color=100)
	dxf.arc(-d, r, r, 90, -90, layer="wire", color=100)
	dxf.line(-d, 0, 0, 0, layer="wire", color=100)

	# info2
	tsize = off / 3
	dxf.mtext(0, r * 2 + wr*2, tsize, f"C={round(c, 2)}mm", anchor=8, layer="info", color=63)
	dxf.mtext(d + r + wr*2, r, tsize, f"B={round(b, 2)}mm", anchor=4, layer="info", color=63)
	dxf.mtext(-d - r - wr*2, r, tsize, f"B={round(b, 2)}mm", anchor=6, layer="info", color=63)
	dxf.mtext(d + r/3*2, 0, tsize, f"R={round(r, 2)}mm", anchor=4, layer="info", color=63)
	dxf.mtext(-d - r/3*2, 0, tsize, f"R={round(r, 2)}mm", anchor=6, layer="info", color=63)
	dxf.mtext(d/2, -wr*2, tsize, f"A={round(a, 2)}mm", anchor=1, layer="info", color=63)
	dxf.mtext(-d/2, -wr*2, tsize, f"D={round(d, 2)}mm", anchor=3, layer="info", color=63)
	dxf.mtext(gap/2, -wr*2, tsize, f"Gap={round(gap, 2)}mm", anchor=2, layer="info", color=63)

	# inner
	dxf.line(gap, wr, gap + a, wr, layer="inner")
	dxf.arc(gap + a, r, r - wr, -90, 90, layer="inner")
	dxf.arc(-d, r, r - wr, 90, -90, layer="inner")
	dxf.line(-d, wr, 0, wr, layer="inner")
	dxf.line(gap + a, r*2 - wr, -d, r*2 - wr, layer="inner")
	dxf.line(0, wr, 0, -wr, layer="inner")
	dxf.line(gap, wr, gap, -wr, layer="inner")
	dxf.line(0, -wr, gap, -wr, layer="inner")

	# holes
	dxf.arc(-d, r, r - off, 90, -90, layer="inner")
	dxf.arc(-r, r, r - off, -90, 90, layer="inner")
	dxf.line(-d, r*2 - off, -r, r*2 - off, layer="inner")
	dxf.line(-d, off, -r, off, layer="inner")
	dxf.arc(d, r, r - off, -90, 90, layer="inner")
	dxf.arc(r, r, r - off, 90, -90, layer="inner")
	dxf.line(d, r*2 - off, r, r*2 - off, layer="inner")
	dxf.line(d, off, r, off, layer="inner")

	# outer
	dxf.arc(gap + a, r, r + wr, -90, 90, layer="outer")
	dxf.arc(-d, r, r + wr, 90, -90, layer="outer")
	dxf.line(d, r*2 + wr, -d, r*2 + wr, layer="outer")
	dxf.line(7, -wr, d, -wr, layer="outer")
	dxf.line(-d, -wr, -7, -wr, layer="outer")
	dxf.line(-7, -wr, -2, -15, layer="outer")
	dxf.line(7, -wr, 2, -15, layer="outer")
	dxf.line(-2, -15, 2, -15, layer="outer")

	# holes
	dxf.arc(-d, r, r - off, 90, -90, layer="outer")
	dxf.arc(-r, r, r - off, -90, 90, layer="outer")
	dxf.line(-d, r*2 - off, -r, r*2 - off, layer="outer")
	dxf.line(-d, off, -r, off, layer="outer")
	dxf.arc(d, r, r - off, -90, 90, layer="outer")
	dxf.arc(r, r, r - off, 90, -90, layer="outer")
	dxf.line(d, r*2 - off, r, r*2 - off, layer="outer")
	dxf.line(d, off, r, off, layer="outer")

	dxf.print()


calc(freq, offset, wire)




