import re
import socket

NONE = 0x00 # no result
ACON = 0x90	# accessory on
ACOF = 0x91	# accessory off
ASON = 0x98	# short accessory on
ASOF = 0x99	# short accessory off

class ubus_listener:
	port = 5550
	sequencer = None
	mappings = {}
	
	def __init__(self, sequencer):
		self.sequencer = sequencer
	
	# load in mappings
	def setup(self, mappings):
		for mapping in mappings:
			self.update_mapping(mapping)
	
	def get_config(self):
		return self.mappings.values()
	
	# update a mapping
	def update_mapping(self, mapping):
		key = self._mapping_key_name(mapping["node"], mapping["event"])
		self.mappings[key] = mapping
		#print "Added mapping: {} -> {}".format(key, sound)
	
	def remove_mapping(self, mapping):
		key = self._mapping_key_name(mapping["node"], mapping["event"])
		if self.mappings.has_key(key):
			del self.mappings[key]
	
	def _mapping_key_name(self, node, event):
		return '%04x'%node + ':' + '%04x'%event
	
	def sound_name_for_event(self, node, event):
		key = self._mapping_key_name(node, event)
		if self.mappings.has_key(key):
			return self.mappings[key]["sound"]
	
	# listen for UBUS packets and dispatch to sequencer
	def listen_udp(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', self.port))
		print 'UDP UBUS listening on port {}'.format(self.port)
		
		while True:
			# establish connection with client.
			packet, addr = sock.recvfrom(1024)
			
			# decode packet
			action, node, event = self.decode(packet)
			
			# dispatch to sequencer
			if action:
				self.dispatch(action, node, event)
	
	# listen for UBUS packets and dispatch to sequencer
	def listen_tcp(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('localhost', self.port))
		print 'TCP UBUS connected to localhost on port {}'.format(self.port)
		
		while True:
			# establish connection with client.
			packet, addr = sock.recvfrom(1024)
			
			# decode packet
			action, node, event = self.decode(packet)
			
			# dispatch to sequencer
			if action:
				self.dispatch(action, node, event)
	
	# send an event to the sequencer
	def dispatch(self, action, node, event):
		sound_name = self.sound_name_for_event(node, event)
		if not sound_name:
			print "No mapping for node {}, event {}".format(node, event)
			return
		
		sound = self.sequencer.get_sound(sound_name)
		if not sound:
			print "No sound in sequencer named {} for node {}, event {}".format(sound_name, node, event)
			return
		
		if action == "play":
			print "Playing {}".format(sound_name)
			sound.play()
		elif action == "stop":
			print "Stopping {}".format(sound_name)
			sound.stop();
		else:
			print "Unknown action: {}".format(action)
			return
	
	# decode packets into event type, and event number
	# example packet: :SBFE0N9000010203;
	# protocol details: http://wiki.rocrail.net/doku.php?id=cbus:protocol
	#  NONE = 0x00, // no result
	#  ACON = 0x90,	// accessory on
	#  ACOF = 0x91,	// accessory off
	#  ASON = 0x98,	// short accessory on
	#  ASOF = 0x99,	// short accessory off
	def decode(self, packet):
		# ACON - <90><node byte 1><node 2><event number 1><event number 2>
		# decode as PLAY <event number = channel>
		match = self.match(packet, 0x90)
		if match:
			return ("play", match[0], match[1])
		
		# ACOF - <91><node byte 1><node 2><event number 1><event number 2>
		# decode as STOP <event number = channel>
		match = self.match(packet, 0x91)
		if match:
			return ("stop", match[0], match[1])
		
		# ASON - <98><node byte 1><node 2><device number 1><device number 2>
		# decode as PLAY <device number = channel>
		match = self.match(packet, 0x98)
		if match:
			return ("play", match[0], match[1])
		
		# ASOF - <99><node byte 1><node 2><device number 1><device number 2>
		# decode as STOP <device number = channel>
		match = self.match(packet, 0x99)
		if match:
			return ("stop", match[0], match[1])
		
		# default
		return (None, None, None)
	
	# check if a packet matches the UBUS format
	def match(self, data, opcode, prefixes=[]):
		# calculate hex prefix to look for
		opcode = '%02x'%opcode
		prefix = ''.join('%04x'%i for i in prefixes)
		# build regex and search for matching data
		match = re.match(':S[A-F0-9]{4}N'+opcode+prefix+'(([A-F0-9]{2})*);', data)
		if match:
			return _split_into_doubles(match.group(1))
		# no match
		else:
			return None


# convert "1234" to 0x4660
# convert "0x1234" to 0x1234
# convert 1234 to 0x4660
def a_to_double(anything):
	if isinstance(anything, int):
		return anything
	else:
		return int(anything, 16)

# 90, [0x0001, 0x0203] -> :SBFE0N9000010203;
def format_packet(opcode, data):
	packet = ":SBFE0N"
	packet += '%02x'%opcode
	packet += "".join('%04x'%a_to_double(double) for double in data)
	packet += ";"
	return packet

def send(data):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(data, ('255.255.255.255', 5550))
	sock.close()
	print " -> {}".format(data)


# split a string into doubles
# ie "FFAA0011" => [0xFFAA, 0x0011]
def _split_into_doubles(line):
	n = 4
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
