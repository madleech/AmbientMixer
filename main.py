import sys
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
	ser = server.server()
	
	# run on new thread
	t = threading.Thread(target=ser.listen, args=(9988, seq.command))
	t.daemon = True
	t.start()
	
	# start sequencer running
	seq.run()
	
except KeyboardInterrupt:
	pygame.quit()
