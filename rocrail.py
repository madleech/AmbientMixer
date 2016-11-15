# coding=utf-8

import re
import socket
import xml.etree.ElementTree as ET

class client:
	port = 8051
	host = 'localhost'
	sequencer = None
	mappings = []
	
	def __init__(self, sequencer, host = 'localhost'):
		self.sequencer = sequencer
		self.host = host
	
	def listen(self):
		self.listen_tcp()
	
	# listen for rocrail packets and dispatch to sequencer
	def listen_tcp(self):
		print 'Connecting to RocRail server at {}:{}'.format(self.host, self.port)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.host, self.port))
		print u'✓ Connected to RocRail server at {}:{}'.format(self.host, self.port).encode('utf-8')
		
		while True:
			# establish connection with client.
			packet = sock.recv(4096)
			
			# process packet
			self.process_packet(packet)
	
	def process_packet(self, packet):
		# decode packet
		data = self.decode(packet)
		if not data:
			return
		else:
			self.sequencer.dispatch(data)
	
	# decode packets into loco id, function, state
	def decode(self, packet):
		packet = strip_xml(packet)
		if not packet or len(packet) < 10:
			return
		parser = ET.XMLParser(encoding="utf-8")
		data = ET.fromstring(packet, parser=parser)
		# <fn id="NS1113" fnchanged="1" group="1" f1="false" server="infwB6700B7C" dir="false" addr="1113" secaddr="0" V="0" placing="true" blockenterside="false" blockenterid="" mode="idle" modereason="" resumeauto="false" manual="false" destblockid="" fn="false" runtime="2458" mtime="0" mint="0" throttleid="" active="true" waittime="0" scidx="-1" scheduleid="" tourid="" train="" trainlen="0" trainweight="0" V_realkmh="0" fifotop="false" image="" imagenr="0"/>
		if data.tag == 'fn':
			fn = int(data.attrib['fnchanged'])
			return {
				'loco': data.attrib['id'],
				'function': fn,
				'state': data.attrib['f{}'.format(fn)] == "true",
			}
		# <co id="block-power-upper-rear" state="on" value="1" iid=""/>
		if data.tag == 'co':
			return {
				'id': data.attrib['id'],
				'state': data.attrib['state'] == "on",
			}

def strip_xml(packet):
	# remove <?xml version="1.0" encoding="UTF-8"?>
	match = re.search('^<\?xml[^>]+\?>(.*)$', packet, re.DOTALL)
	if match:
		packet = match.group(1)
	
	# remove <xmlh>...</xmlh>
	match = re.search('<xmlh>.+</xmlh>(.*)$', packet, re.DOTALL)
	if match:
		packet = match.group(1)
	
	if len(packet) > 10:
		return '<?xml version="1.0" encoding="UTF-8"?>{}'.format(packet).strip().rstrip(' \t\r\n\0')
	
