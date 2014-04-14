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
				command, id = packet
				cb(command, id)
	
	def parse(self, data):
		match = re.match('(play|stop) ([0-9]+)', data)
		if match:
			command, id = match.groups()
			return (command, int(id))
