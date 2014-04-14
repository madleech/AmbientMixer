# sequencer
# - load in an array of sounds into channels
# - each channel has:
#   - name
#   - file
#   - loop / frequency

import re
import time
import random
import os.path
import subprocess
import pygame.mixer

class sound:
	_length = 0
	_next_play = 0
	_playing = False
	_started_at = 0
	
	def __init__(self, id, filename, volume, loop, frequency):
		# properties
		self._loop      = bool(loop)
		self._frequency = float(frequency) / 100
		self._id        = id
		
		# check format is correct - wav, 44khz, 16bit
		converted = re.sub('([a-z0-9A-Z\-_]+)\-([0-9]+)-(loop|[0-9]+)\.[a-z0-9A-Z]+', r'converted/\1-\2-\3.wav', os.path.basename(filename))
		
		# convert if required
		if os.path.isfile(converted) == False:
			print 'converting {} to standard format'.format(filename)
			subprocess.call(['sox', filename, '-b 16', '-r 44k', converted])
		
		# file converted, load into pygame sound
		self._sound = pygame.mixer.Sound(converted)
		self._length = self._sound.get_length()
		self._sound.set_volume(float(volume) / 100)
		
		print 'new sound(id:{}, len:{}, loop:{}, freq:{})'.format(self._id, self._length, self._loop, self._frequency)
	
	def play(self):
		print 'play: {}'.format(self._id)
		self._playing = True
		self._started_at = time.time()
		if self._loop:
			self._sound.play(-1)
		else:
			self._sound.play()
	
	def stop(self):
		print 'stop: {}'.format(self._id)
		self._sound.stop()
		self._playing = False
	
	def play_if_required(self):
		if self._next_play == 0 and self._frequency > 0:
			self._next_play = time.time() + random.uniform(2, 10 / self._frequency)
			print 'Next play of {} in {}s'.format(self._id, int(self._next_play - time.time()))
		
		if self._next_play <= time.time() and self.is_playing() == False:
			self.play()
			self._next_play = 0
	
	def is_playing(self):
		# not started yet
		if self._playing == False:
			return False
		# has started and is a loop
		elif self._loop == True:
			return True
		# isn't a loop and has finished playing
		elif self._started_at + self._length < time.time():
			return False
		# otherwise must be playing
		else:
			return True

class sequencer:
	_channels = []
	
	def __init__(self):
		pygame.mixer.init(44100, -16, 2, 2048)
	
	def load(self, files):
		# look at file name to work out what to do?
		for filename in files:
			match = re.match('([a-z0-9A-Z\-_]+)\-([0-9]+)-(loop|[0-9]+)\.[a-z0-9A-Z]+', os.path.basename(filename))
			if match:
				name, volume, loop = match.groups()
				if loop == 'loop':
					frequency = 0
					loop = True
				else:
					frequency = loop
					loop = False
				
				self.add(name, filename, volume, loop, frequency)
			else:
				print 'could not extract data from {}'.format(filename)
	
	def add(self, name, filename, volume, loop, frequency):
		if loop:
			frequency = 0
		self._channels.append(sound(name, filename, volume, loop, frequency))
	
	def channels(self):
		for sound in self._channels:
			print sound
	
	def command(self, id, action):
		sound = self._channels[id]
		if action == 'play':
			sound.play()
		if action == 'stop':
			sound.stop()
	
	def run(self):
		while True:
			for sound in self._channels:
				sound.play_if_required()
			time.sleep(0.5)
