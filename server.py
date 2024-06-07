import re
import sys
import json
import socket

class tcp_server:
	port = None
	sequencer = None
	
	def __init__(self, port, sequencer, ubus_server):
		self.port = port
		self.sequencer = sequencer
		self.ubus_server = ubus_server
	
	# listen for TCP messages and dispatch to sequencer/ubus_server
	def listen(self):
		sock = socket.socket()
		sock.bind(('', self.port))
		sock.listen(5)
		print('TCP management server now listening on port {}'.format(self.port))
		
		while True:
			# establish connection with client.
			conn, addr = sock.accept()
			data = self.recv(conn)
			
			# decode packet
			method, target, name, args = self.decode(data)
			
			# dispatch to appropriate handler
			result = self.dispatch(method, target, name, args)
			
			# return response, close connection with client
			conn.send(json.dumps(result))
			conn.close()
	
	# work out where to send a packet, send it there, and return result/error
	def dispatch(self, method, target, name, args):
		try:
			# ensure valid
			if not method:
				return {"error":"Missing method"}
			if not target:
				return {"error":"Target method"}
			if not args:
				return {"error":"Missing args"}
			
			# dispatch to ubus_server
			if target == 'ubus':
				if method == 'update_mapping':
					return self.ubus_server.update_mapping(*args)
			
			# dispatch to sequencer
			elif target == 'sequencer':
				if hasattr(self.sequencer, method):
					return getattr(self.sequencer, method)(*args)
			
			# dispatch to sound
			elif target == 'sound' or target == 'background_sound':
				if target == 'sound':
					sound = self.sequencer.get_sound(name)
				else:
					sound = self.sequencer.get_background_sound(name)
				
				if hasattr(sound, method):
					return getattr(sound, method)(*args)
		
		# catch any kind of dispatch error
		except:
			e = sys.exc_info()[0]
			print(e)
			return {"error", e[1]}
	
	# get data from socket, return as single big string
	def recv(self, conn):
		data = ""
		while True:
			bits = conn.recv(4096);
			data += bits
			if not bits: break
		return data
	
	# packet format: {method:<method>, target:<ubus, sequencer, sound, background_sound>, [name:sound name], args:[args]}
	def decode(self, packet):
		try:
			data   = json.loads(packet)
			method = data[method]
			target = data[target]
			name   = data[name] if 'name' in data else None
			args   = data[args]
		except:
			method = target = name = args = None
		
		return (method, target, name, args)
