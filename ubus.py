import re
import socket

class ubus_listener:
	port = 5550
	callback = None
	address = 0
	
	def __init__(self, address, callback):
		self.callback = callback
		self.address = address
	
	def listen(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', self.port))
		print 'UDP server now listening on port {}'.format(self.port)
		
		while True:
			# Establish connection with client.
			data, addr = sock.recvfrom(1024)
			
			print 'UDP: {}'.format(data)
			
			# Run callback
			self.handle_packet(data)
	
	def handle_packet(self, data):
		packet = self.decode_packet(data)
		if packet and self.callback:
			command, id, val = packet
			self.callback(command, id, val)
	
	# example packet: :SBFE0N9000010203;
	# protocol details: http://wiki.rocrail.net/doku.php?id=cbus:protocol
	#  NONE = 0x00, // no result
	#  ACON = 0x90,	// accessory on
	#  ACOF = 0x91,	// accessory off
	#  ASON = 0x98,	// short accessory on
	#  ASOF = 0x99,	// short accessory off
	
	def decode_packet(self, data):
		# ACON - <90><node byte 1><node 2><event number 1><event number 2>
		# decode as PLAY <event number = channel>
		match = self.match(data, 0x90, [self.address])
		if match:
			return ("play", match[0], None)

		# ACOF - <91><node byte 1><node 2><event number 1><event number 2>
		# decode as STOP <event number = channel>
		match = self.match(data, 0x91, [self.address])
		if match:
			return ("stop", match[0], None)
		
		# ASON - <98><node byte 1><node 2><device number 1><device number 2>
		# decode as PLAY <device number = channel>
		match = self.match(data, 0x98, [self.address])
		if match:
			return ("play", match[0], None)
		
		# ASOF - <99><node byte 1><node 2><device number 1><device number 2>
		# decode as STOP <device number = channel>
		match = self.match(data, 0x99, [self.address])
		if match:
			return ("stop", match[0], None)
	
	def match(self, data, opcode, prefixes):
		# calculate hex prefix to look for
		opcode = '%02x'%opcode
		prefix = ''.join('%04x'%i for i in prefixes)
		# build regex and search for matching data
		match = re.match(':S[A-F0-9]{4}N'+opcode+prefix+'(([A-F0-9]{2})*);', data)
		if match:
			nibbles = _split_into_nibbles(match.group(1))
			data = _decode_2_hex_nibbles(nibbles)
			return data
		# no match
		else:
			return False


def _split_into_nibbles(line):
	n = 2
	return [line[i:i+n] for i in range(0, len(line), n)]

def _decode_2_hex_nibbles(nibbles):
	n = 2
	return [int(nibbles[i] + nibbles[i+1], 16) for i in range(0, len(nibbles), n)]
