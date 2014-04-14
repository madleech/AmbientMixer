import sys
import mixer
import files
import sounds
import server
import threading

import pygame
from pygame.locals import *

def cb(command, id):
	seq.command(id, command)

try:
	# load lists of sounds
	if len(sys.argv) > 1:
		dir = sys.argv[1]
	else:
		dir = 'sounds'
	
	sound_files = files.list(dir)
	
	# load sounds into sequencer
	seq = sounds.sequencer()
	seq.load(sound_files)
	
	# create server
	ser = server.server()
	# run on new thread
	t = threading.Thread(target=ser.listen, args=(9988, cb))
	t.daemon = True
	t.start()
	
	# now run
	seq.run()
	
except KeyboardInterrupt:
	pygame.quit()
