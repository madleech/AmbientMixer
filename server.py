import re
import socket

class tcp_server:
	port = None
	callback = None
	
	def __init__(self, port, callback):
		self.port = port
		self.callback = callback
	
	def listen(self):
		sock = socket.socket()
		sock.bind(('', self.port))
		sock.listen(5)
		print 'TCP server now listening on port {}'.format(self.port)
		
		while True:
			# Establish connection with client.
			conn, addr = sock.accept()
			data = conn.recv(4096)
			
			# Close the connection with the client
			conn.close()
			
			# Run callback
			handle_packet(data, self.callback)


class udp_server:
	port = None
	callback = None
	
	def __init__(self, port, callback):
		self.port = port
		self.callback = callback
	
	def listen(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', self.port))
		print 'UDP server now listening on port {}'.format(self.port)
		
		while True:
			# Establish connection with client.
			data, addr = sock.recvfrom(1024)
			
			print 'UDP: {}'.format(data)
			
			# Run callback
			handle_packet(data, self.callback)
	
	
def handle_packet(data, callback):
	packet = decode_packet(data)
	if packet and callback:
		command, id, val = packet
		callback(command, id, val)

def decode_packet(data):
	match = re.match('(dump)', data)
	if match:
		command = match.group(1)
		return (command, None, None)
		
	match = re.match('(play|stop) ([0-9]+)', data)
	if match:
		command, id = match.groups()
		return (command, id, None)
	
	match = re.match('(loop) ([0-9]+) (on|off)', data)
	if match:
		command, id, val = match.groups()
		return (command, id, val == 'on')

	match = re.match('(freq|vol) ([0-9]+) ([0-9]+)', data)
	if match:
		command, id, val = match.groups()
		return (command, id, val)
