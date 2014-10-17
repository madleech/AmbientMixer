import os, sys
import ubus

if len(sys.argv) <= 3:
	sys.exit("Usage: {} <opcode> <node> <event> - sends an ACON event to the given node and event".format(sys.argv[0]))

# convert data
if sys.argv[1] == 'ACON' or sys.argv[1] == 'ON':
	opcode = ubus.ACON
elif sys.argv[1] == 'ACOF' or sys.argv[1] == 'OF':
	opcode = ubus.ACOF
else:
	sys.exit("Unknown opcode: {}".format(sys.argv[1]))

# format packet
packet = ubus.format_packet(opcode, [sys.argv[2]] + ubus.a_to_double_bytes(sys.argv[3]))

# and send it
ubus.send(packet)