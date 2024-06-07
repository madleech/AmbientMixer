# coding=utf-8

import re
import socket

NONE = 0x00 # no result
ACON = 0x40	# accessory on
ACOF = 0x41	# accessory off
ASON = 0x98	# short accessory on
ASOF = 0x99	# short accessory off
DFON = 0x61 # dcc function on
DFOF = 0x62 # dcc function off

class ubus_listener:
	port = 5550
	sequencer = None
	mappings = []
	
	def __init__(self, sequencer):
		self.sequencer = sequencer
	
	# load in mappings
	def setup(self, mappings):
		self.mappings = mappings
	
	def get_config(self):
		return self.mappings
	
	# update a mapping
	def update_mapping(self, mapping):
		if mapping in self.mappings:
			idx = self.mappings.index(mapping)
			self.mappings[idx] = mapping
		else:
			self.mappings.append(mapping)
	
	def remove_mapping(self, mapping):
		if mapping in self.mappings:
			idx = self.mappings.index(mapping)
			del self.mappings[idx]
	
	def listen(self):
		# try on UDP
		try:
			self.listen_udp()
			self.listen_tcp()
		
		# otherwise try on TCP
		except Exception as e:
			print('Exception caught while running server: {}'.format(e))
	
	# listen for UBUS packets and dispatch to sequencer
	def listen_udp(self):
		print('➝ Starting UDP listener on port {}'.format(self.port))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			sock.bind(('', self.port))
			print('✓ UDP UBUS now listening on port {}'.format(self.port))
		except Exception as e:
			print('Exception caught while starting UDP listener: {}'.format(e))
			return False
		
		while True:
			# establish connection with client.
			packet, addr = sock.recvfrom(1024)
			
			# process packet
			self.process_packet(packet)
	
	# listen for UBUS packets and dispatch to sequencer
	def listen_tcp(self):
		print('➝ Connecting to TCP UBUS server on localhost:{}'.format(self.port))
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('localhost', self.port))
		print('✓ Connected to TCP UBUS server on port {}'.format(self.port))
		
		while True:
			# establish connection with client.
			packet, addr = sock.recvfrom(1024)
			
			# process packet
			self.process_packet(packet)
			
	
	def process_packet(self, packet):
		# decode packet
		data = self.decode(packet)
		if data:
			self.sequencer.dispatch(data)
	
	def decode(self, packet):
		opcode, data = self.decode_raw_packet(packet)
		if opcode:
			return parse_packet(opcode, data)
	
	# converts arbitrary data into meaningful data
	# e.g. U61000100 -> DFON, [loco:0001, function:01] (note +1 on function)
	# e.g. U410102 -> ACON [node:01, event: 02]
	def parse_packet(self, opcode, data):
		# U410102 -> ACON [node:01, event: 02]
		if opcode == ACON:
			return {"node":data[0], "event":data[1], "state":True}
		elif opcode == ACOF:
			return {"node":data[0], "event":data[1], "state":False}
		elif opcode == DFON:
			return {"loco":(data[0] << 8) + data[1], "function":data[2], "state":True}
		elif opcode == DFOF:
			return {"loco":(data[0] << 8) + data[1], "function":data[2], "state":False}
	
	# decode packets into event type, and event number
	# example packet: U410203
	# protocol details: http://wiki.rocrail.net/doku.php?id=cbus:protocol
	#  NONE = 0x00, // no result
	#  ACON = 0x90,	// accessory on
	#  ACOF = 0x91,	// accessory off
	#  ASON = 0x98,	// short accessory on
	#  ASOF = 0x99,	// short accessory off
	def decode_raw_packet(self, packet):
		# build regex and search for matching data
		match = re.match('U([A-F0-9]{2})(([A-F0-9]{2})*)', packet)
		if match:
			return (_split_into_chunks(match.group(1))[0], _split_into_chunks(match.group(2)))
		# no match
		else:
			return (None, None)


# convert "1234" to 0x4660
# convert "0x1234" to 0x1234
# convert 1234 to 0x4660
def a_to_double(anything):
	if isinstance(anything, int):
		return anything
	elif "0x" in anything and anything.index("0x") == 0:
		return int(anything, 16)
	else:
		return int(anything, 10)

def a_to_double_bytes(anything):
	anything = a_to_double(anything)
	return [anything >> 8, anything & 0xFF]

# 90, [0x0001, 0x0203] -> :SBFE0N9000010203;
def format_packet(opcode, data):
	packet = "U"
	packet += '%02x'%opcode
	packet += "".join('%02x'%a_to_double(byte) for byte in data)
	return packet.upper()

def send(data):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(data, ('255.255.255.255', 5550))
	sock.close()
	print(" -> {}".format(data))


# split a string into doubles
# ie "FFAA0011" => [0xFFAA, 0x0011]
def _split_into_chunks(line, n = 2):
	doubles = [line[i:i+n] for i in range(0, len(line), n)]
	return [int(double, 16) for double in doubles]

# split a string into nibbles
# ie "FFAA00" => ['FF', 'AA', '00']
def _split_into_nibbles(line):
	n = 2
	return [line[i:i+n] for i in range(0, len(line), n)]

# convert pairs of hex digits into a byte
# ie ["FF", "00"] => [0xFF, 0x00]
def _decode_2_hex_nibbles(nibbles):
	n = 2
	return [int(nibbles[i] + nibbles[i+1], 16) for i in range(0, len(nibbles), n)]

def _destring_opcode(opcodes):
	out = []
	for opcode in opcodes:
		if (opcode == "ACON"):
			out.append(ACON)
		elif (opcode == "ACOF"):
			out.append(ACOF)
		elif (opcode == "DFON"):
			out.append(DFON)
		elif (opcode == "DFOF"):
			out.append(DFOF)
	return out
