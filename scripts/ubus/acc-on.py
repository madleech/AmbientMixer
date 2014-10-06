import os, sys
import ubus

if len(sys.argv) <= 2:
	sys.exit("Usage: {} <node> <event> - sends an ACON event to the given node and event".format(sys.argv[0]))

# format packet
packet = ubus.format_packet(ubus.ACON, [sys.argv[1], sys.argv[2]])

# and send it
ubus.send(packet)