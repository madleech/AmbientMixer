import os, sys
import ubus

if len(sys.argv) <= 3:
	sys.exit("Usage: {} <opcode> <node> <event> - sends an ACON event to the given node and event".format(sys.argv[0]))

# convert data
if sys.argv[1] == 'ACON' or sys.argv[1] == 'ON':
	opcode = ubus.ACON
	data = [sys.argv[2], sys.argv[3]]
elif sys.argv[1] == 'ACOF' or sys.argv[1] == 'OF':
	opcode = ubus.ACOF
	data = [sys.argv[2], sys.argv[3]]

elif sys.argv[1] == 'DFON':
	opcode = ubus.DFON
	data = ubus.a_to_double_bytes(sys.argv[2]) + [sys.argv[3]]
elif sys.argv[1] == 'DFOF':
	opcode = ubus.DFOF
	data = ubus.a_to_double_bytes(sys.argv[2]) + [sys.argv[3]]

else:
	sys.exit("Unknown opcode: {}".format(sys.argv[1]))

# format packet
packet = ubus.format_packet(opcode, data)

# and send it
ubus.send(packet)