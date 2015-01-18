#!/usr/bin/env python
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '../..'))
import ubus

if len(sys.argv) <= 2:
	sys.exit("Usage: {} <loco addr> <function> - simulates a DFOF event".format(sys.argv[0]))

# format packet
packet = ubus.format_packet(ubus.DFOF, [0, sys.argv[1], sys.argv[2]])

# and send it
ubus.send(packet)