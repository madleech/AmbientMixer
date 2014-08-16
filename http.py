import sys
import json
import logging
import BaseHTTPServer


# decode HTTP posts
class PostHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_POST(self):
		# get posted data
		content_len = int(self.headers.getheader('content-length', 0))
		data = self.rfile.read(content_len)
		
		# begin response
		self.send_response(200)
		self.end_headers()
		
		print data
		
		# decode packet
		target, method, name, args = self.server.decode(data)
		
		# dispatch to appropriate handler
		result = self.server.dispatch(target, method, name, args)
		
		# return response, close connection with client
		self.wfile.write(json.dumps(result))
	
	def log_message(self, format, *args):
		return


class http_server:
	port = None
	sequencer = None
	ubus_server = None
	
	def __init__(self, port, sequencer, ubus_server):
		self.port = port
		self.sequencer = sequencer
		self.ubus_server = ubus_server
	
	def listen(self):
		server = BaseHTTPServer.HTTPServer(('localhost', self.port), PostHandler)
		# set up callbacks for processing from handler
		server.sequencer = self.sequencer
		server.decode = self.decode
		server.dispatch = self.dispatch
		# start server
		print 'HTTP server listening on port {}'.format(self.port)
		server.serve_forever()
	
	# packet format: {method:<method>, target:<ubus, sequencer, sound, background_sound>, [name:sound name], args:[args]}
	def decode(self, packet):
		#try:
		data   = json.loads(packet)
		target = data['target']
		method = data['method']
		name   = data['name'] if data.has_key('name') else None
		args   = data['args'] if data.has_key('args') else None
		# except:
			# method = target = name = args = None
		
		return (target, method, name, args)
	
	# work out where to send a packet, send it there, and return result/error
	def dispatch(self, target, method, name, args):
		try:
			# ensure valid
			if not method:
				return {"error":"Missing method"}
			if not target:
				return {"error":"Target method"}
			
			# dispatch to ubus_server
			if target == 'ubus':
				if hasattr(self.ubus_server, method):
					return getattr(self.ubus_server, method)(*args)
			
			# dispatch to sequencer
			elif target == 'sequencer':
				if hasattr(self.sequencer, method):
					if args:
						return getattr(self.sequencer, method)(*args)
					else:
						return getattr(self.sequencer, method)()
			
			# dispatch to sound
			elif target == 'sound' or target == 'background_sound':
				if target == 'sound':
					sound = self.sequencer.get_sound(name)
				else:
					sound = self.sequencer.get_background_sound(name)
				
				if hasattr(sound, method):
					return getattr(sound, method)(*args)
		
		# catch any kind of dispatch error
		except KeyError as e:
			# e = sys.exc_info()
			print e
			return {"error":str(e[1])}

