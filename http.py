import cgi
import sys
import json
import logging
import BaseHTTPServer


# decode HTTP posts
class PostHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_POST(self):
		# is this a multi-part post?
		if self.headers['Content-Type'].find('multipart/form-data') > -1:
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={
					'REQUEST_METHOD':'POST',
					'CONTENT_TYPE':self.headers['Content-Type'],
				}
			)
			
			# get JSON
			json_data = form['json'].value
			
			# is a file upload too?
			if (form.has_key('file') and form['file'].filename):
				# place file into sounds/ under its filename
				filename = "sounds/" + form['file'].filename
				print "File uploaded to {}".format(filename)
				fp = open(filename, 'wb')
				while True:
					chunk = form['file'].file.read(8192)
					if len(chunk) == 0:
						break
					else:
						fp.write(chunk)
				fp.close()
		
		# not a form style post, so just get raw data
		else:
			# get JSON
			content_len = int(self.headers.getheader('content-length', 0))
			json_data = self.rfile.read(content_len)
		
		# begin response
		self.send_response(200)
		self.end_headers()
		
		print json_data
		
		# decode packet
		target, method, name, args = self.server.decode(json_data)
		
		# dispatch to appropriate handler
		result = self.server.dispatch(target, method, name, args)
		
		# return response, close connection with client
		self.wfile.write(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
	
	def log_message(self, format, *args):
		return


class http_server:
	port = None
	sequencer = None
	ubus_server = None
	
	def __init__(self, port, sequencer, ubus_server, config_manager):
		self.port = port
		self.sequencer = sequencer
		self.ubus_server = ubus_server
		self.config_manager = config_manager
	
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
			
			# dispatch to config manager
			if target == 'config':
				if hasattr(self.config_manager, method):
					return getattr(self.config_manager, method)(*args)			
			
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

