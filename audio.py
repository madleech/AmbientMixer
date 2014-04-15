# sequencer
# - load in an array of sounds into channels
# - each channel has:
#   - name
#   - file
#   - loop / frequency

import re
import time
import json
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
		converted = re.sub('(.+)\.[a-z0-9A-Z]+', r'converted/\1.wav', os.path.basename(filename))
		
		# convert if required
		if os.path.isfile(converted) == False:
			print 'converting {} to standard format'.format(filename)
			subprocess.call(['sox', filename, '-b 16', '-r 44k', converted])
		
		# file converted, load into pygame sound
		self._sound = pygame.mixer.Sound(converted)
		self._length = self._sound.get_length()
		self._sound.set_volume(float(volume) / 100)
		
		# print '{}: {} ({}s)'.format(self._id, filename, self._length)
	
	def id(self):
		return self._id
	
	def play(self):
		# print 'play: {}'.format(self._id)
		self._playing = True
		self._started_at = time.time()
		if self._loop:
			self._sound.play(-1)
		else:
			self._sound.play()
	
	def stop(self):
		# print 'stop: {}'.format(self._id)
		self._sound.stop()
		self._playing = False
	
	def loop(self, enable):
		self._loop = enable
		if enable == True:
			self._frequency = 0
	
	def freq(self, freq):
		self._frequency = freq
		self._loop = False
	
	def vol(self, vol):
		self._sound.set_volume(float(vol) / 100)
	
	def play_if_required(self):
		if self._frequency == 0 and self._loop == False:
			return
		
		if self._next_play == 0 and self._frequency > 0:
			self._next_play = time.time() + random.uniform(2, 10 / self._frequency)
			# print 'Next play of {} in {}s'.format(self._id, int(self._next_play - time.time()))
		
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
	_channels = {}
	
	def __init__(self):
		pygame.mixer.init(44100, -16, 2, 2048)
	
	def setup(self, configfile):
		# load config file
		fp = open(configfile)
		config = json.load(fp)
		fp.close()
		
		# turn config into sounds
		for sound in config['sounds']:
			self.add(sound['id'], sound['filename'], sound['volume'], sound['loop'], sound['frequency'])
	
	def add(self, id, filename, volume, loop, frequency):
		# adjust freq if looping
		if loop:
			frequency = 0
		# check not double assigning
		id = str(id)
		if self._channels.has_key(id) == False:
			self._channels[id] = sound(os.path.basename(filename), filename, volume, loop, frequency)
			print "{}: {}".format(id, os.path.basename(filename))
		else:
			print "Error loading {} as id {} is already taken by {}".format(filename, id, self._channels[id].id())
	
	def command(self, action, id, val):
		id = str(id)
		if self._channels.has_key(id) == False:
			print "{}: {} - no such index".format(action, id)
			return False
		sound = self._channels[id]
		
		if action == 'play':
			sound.play()
		if action == 'stop':
			sound.stop()
		if action == 'loop':
			sound.loop(bool(val))
		if action == 'vol':
			sound.vol(int(val))
		if action == 'freq':
			sound.freq(int(val))
	
	def run(self):
		while True:
			for sound in self._channels:
				self._channels[sound].play_if_required()
			time.sleep(0.5)
