import re
import socket

class server:
	def listen(self, port, cb):
		sock = socket.socket()
		sock.bind(('', port))
		sock.listen(5)
		
		while True:
			# Establish connection with client.
			conn, addr = sock.accept()
			data = conn.recv(4096)
			
			# Close the connection with the client
			conn.close()
			
			# Run callback
			packet = self.parse(data)
			if packet and cb:
				command, id, val = packet
				cb(command, id, val)
	
	def parse(self, data):
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
