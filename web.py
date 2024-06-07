# coding=utf-8

import os
import re
import cgi
import sys
import json
import logging
import http.server

# decode HTTP posts
class PostHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		basedir = os.path.dirname(os.path.realpath(__file__))
		
		if self.path == "/":
			self.path = "/index.html"
		
		match = re.search('^(.+)\\?', self.path)
		if match:
			self.path = match.group(1)
		
		try:
			sendReply = False
			if self.path.endswith(".html"):
				mimetype = 'text/html'
				sendReply = True
			if self.path.endswith(".png"):
				mimetype = 'image/png'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype = 'image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype = 'image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype = 'application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype = 'text/css'
				sendReply = True
			if self.path.endswith(".otf"):
				mimetype = 'application/x-font-otf'
				sendReply = True
			if self.path.endswith(".woff"):
				mimetype = 'application/x-font-woff'
				sendReply = True
			if self.path.endswith(".ttf"):
				mimetype = 'application/x-font-ttf'
				sendReply = True
			
			if sendReply == True:
				print('➝ GET {}'.format(self.path))
				#Open the static file requested and send it
				f = open(os.sep.join([basedir, 'gui', self.path]), "rb")
				self.send_response(200)
				self.send_header('Content-type', mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return
		
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
	
	def do_OPTIONS(self):
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')
		self.send_header('Access-Control-Max-Age', '1728000')
		self.end_headers()
	
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
			if ('file' in form):
				files = form['file']
				if isinstance(files, list) == False:
					files = [files]
				for file in files:
					if (file.filename):
						# place file into sounds dir under its filename
						filename = file.filename
						print("-> file uploaded to {}/{}".format(os.getcwd(), filename))
						fp = open(filename, 'wb')
						while True:
							chunk = file.file.read(8192)
							if len(chunk) == 0:
								break
							else:
								fp.write(chunk)
						fp.close()
		
		# not a form style post, so just get raw data
		else:
			# get JSON
			content_len = int(self.headers['content-length'])
			json_data = self.rfile.read(content_len)
		
		# begin response
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.end_headers()
		
		print('-> {}'.format(json_data))
		
		# decode packet
		target, method, name, args = self.server.decode(json_data)
		
		# dispatch to appropriate handler
		try:
			result = self.server.dispatch(target, method, name, args)
		except Exception as e:
			result = {'error': str(e)}
		
		# return response, close connection with client
		self.wfile.write(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf-8'))
	
	def log_message(self, format, *args):
		return


class http_server:
	port = None
	sequencer = None
	
	def __init__(self, port, sequencer, config_manager):
		self.port = port
		self.sequencer = sequencer
		self.config_manager = config_manager
	
	def listen(self):
		server = http.server.HTTPServer(('0.0.0.0', self.port), PostHandler)
		# set up callbacks for processing from handler
		server.sequencer = self.sequencer
		server.decode = self.decode
		server.dispatch = self.dispatch
		# start server
		print('✓ HTTP server listening on port {}'.format(self.port))
		server.serve_forever()
	
	# packet format: {method:<method>, target:<sequencer, sound, background_sound>, [name:sound name], args:[args]}
	def decode(self, packet):
		#try:
		data   = json.loads(packet)
		target = data['target']
		method = data['method']
		name   = data['name'] if 'name' in data else None
		args   = data['args'] if 'args' in data else None
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
			error = "No such key {} while dispatching method {} to target {}".format(e, method, target)
			print(e)
			return {"error":error}
