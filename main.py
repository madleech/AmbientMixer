import sys
import http
import ubus
import mixer
import audio
import config
import server
import threading
from sequencer import sequencer

import pygame
from pygame.locals import *

try:
	# load config file
	if len(sys.argv) <= 1:
		sys.exit("Usage: {} <config.json>".format(sys.argv[0]))
	
	# create sequencer
	seq = sequencer()
	
	# create UDP UBUS trigger interface
	ubus_server = ubus.ubus_listener(seq)
	
	# create HTTP management interface
	http_server = http.http_server(port=9988, sequencer=seq, ubus_server=ubus_server)
	
	# load config file
	settings = config.load(sys.argv[1])
	
	# configure sequencer
	if settings.has_key("sounds"):
		seq.setup_sounds(settings['sounds'])
	if settings.has_key("background_sounds"):
		seq.setup_background_sounds(settings['background_sounds'])
	
	# configure UBUS server
	if settings.has_key("ubus_mappings"):
		ubus_server.setup(settings['ubus_mappings'])
	
	# run servers on new threads
	t1 = threading.Thread(target=http_server.listen)
	t1.daemon = True
	t1.start()

	t2 = threading.Thread(target=ubus_server.listen)
	t2.daemon = True
	t2.start()
	
	# start sequencer running
	seq.run()

except KeyboardInterrupt:
	pygame.quit()
