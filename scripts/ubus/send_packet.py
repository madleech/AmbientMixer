import sys
import ubus

if len(sys.argv) <= 1:
	sys.exit("Usage: {} <packet>".format(sys.argv[0]))

ubus.send(sys.argv[1])