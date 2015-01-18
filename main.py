import sys
import http
import ubus
# import mixer
import audio
import server
import threading
from config import config
from sequencer import sequencer

import pygame
from pygame.locals import *

try:
	# load config file
	# if len(sys.argv) <= 1:
	#	sys.exit("Usage: {} <config.json>".format(sys.argv[0]))
	
	# create sequencer
	seq = sequencer()
	
	# create UDP UBUS trigger interface
	ubus_server = ubus.ubus_listener(seq)
	
	# create a config manager
	config_manager = config(sequencer=seq, ubus_server=ubus_server)
	
	# create HTTP management interface
	http_server = http.http_server(port=9988, sequencer=seq, ubus_server=ubus_server, config_manager=config_manager)
	
	# load config file
	if len(sys.argv) > 1:
		config_manager.load(sys.argv[1])
	
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
