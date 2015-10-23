import sys, os

def countchars(directory):
	n = 0
	p = "for test"
	for name in os.listdir(directory):
		fp = open(name)
		for line in fp:
			n  += line
		fp.fclose()
	return n

countchars(sys.argv[1])
