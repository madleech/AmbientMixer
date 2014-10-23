#!/usr/bin/env python
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '../..'))
import ubus

if len(sys.argv) <= 2:
	sys.exit("Usage: {} <node> <event> - sends an ACOF event to the given node and event".format(sys.argv[0]))

# format packet
packet = ubus.format_packet(ubus.ACOF, [sys.argv[1], sys.argv[2]])

# and send it
ubus.send(packet)