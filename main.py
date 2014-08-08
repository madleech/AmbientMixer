import sys
import ubus
import mixer
import audio
import server
import threading

import pygame
from pygame.locals import *

try:
	# load config file
	if len(sys.argv) <= 1:
		sys.exit("Usage: {} <config.json>".format(sys.argv[0]))
	
	# create sequencer
	seq = audio.sequencer()
	
	# load config into sequencer
	configfile = sys.argv[1]
	seq.setup(configfile)
	
	# create server
	tcp_server = server.tcp_server(9988, seq.command)
	# udp_server = server.udp_server(9999, seq.command)
	ubus_server = ubus.ubus_listener(1, seq.command)
	
	# run on new thread
	t1 = threading.Thread(target=tcp_server.listen)
	t1.daemon = True
	t1.start()

	t2 = threading.Thread(target=ubus_server.listen)
	t2.daemon = True
	t2.start()
	
	# start sequencer running
	seq.run()
	
except KeyboardInterrupt:
	pygame.quit()
