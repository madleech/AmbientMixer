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
	_volume = 0
	_frequency = 0
	
	def __init__(self, id, filename, volume, loop, frequency):
		# properties
		self._id = id
		
		self._filename = self.convert(filename)
		
		# file converted, load into pygame sound
		self._sound = pygame.mixer.Sound(self._filename)
		self._length = self._sound.get_length()
		self.vol(volume)
		self.loop(loop)
		self.freq(frequency)
	
	# MANAGE
	
	# check format is correct - wav, 44khz, 16bit
	def convert(self, filename):
		converted = re.sub('(.+)\.[a-z0-9A-Z]+', r'converted/\1.wav', os.path.basename(filename))
		
		# convert if required
		if os.path.isfile(converted) == False:
			print 'converting {} to standard format'.format(filename)
			subprocess.call(['sox', filename, '-b 16', '-r 44k', converted])
		
		return converted
	
	# ACCESS / CONFIG
	
	def id(self):
		return self._id
	
	def get_config(self):
		return {
			"name": self._id,
			"filename": self._filename,
			"volume": int(self._volume * 100),
			"frequency": int(self._frequency * 100),
			"loop": self._loop			
		}
	
	# CONTROL
	
	def play(self):
		# print 'play: {}'.format(self._id)
		self._playing = True
		self._started_at = time.time()
		if self._loop:
			self._frequency = 0
			self._sound.play(-1)
		else:
			self._sound.play()
	
	def stop(self):
		# print 'stop: {}'.format(self._id)
		self._sound.stop()
		self._playing = False
		if self._loop == True:
			self._frequency = -1
	
	def loop(self, enable):
		self._loop = bool(enable)
		if self._loop == True:
			self._frequency = 0
	
	def freq(self, freq):
		self._frequency = float(freq) / 100
		self._loop = False
	
	def vol(self, vol):
		self._volume = float(vol) / 100
		self._sound.set_volume(self._volume)
	
	# INTERNAL STATE
	
	def play_if_required(self):
		if self._frequency == 0 and self._loop == False:
			return
		
		# ignore stopped looping sounds
		if self._frequency < 0 and self._loop == True:
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


class music:
	_enabled = True
	_volume = 0
	
	def __init__(self, id, filename, volume):
		# properties
		self._filename = self.convert(filename)
		self._id = id
		
		# file converted, load into pygame sound
		pygame.mixer.music.load(self._filename)
		self.vol(volume)
	
	# MANAGE
	
	# check format is correct - ogg
	def convert(self, filename):
		converted = re.sub('(.+)\.[a-z0-9A-Z]+', r'converted/\1.wav', os.path.basename(filename))
		
		# convert if required
		if os.path.isfile(converted) == False:
			print 'converting {} to standard format'.format(filename)
			# sox sounds/twilight.mp3 -t wav - | oggenc --raw - > test.gg
			# cmd = ['sox', filename, '-t wav', '-', 'fade 0:5 0 0:5', '|', 'oggenc', '--raw', '-', '-o', converted]
			subprocess.call(['sox', filename, '-b 16', '-r 44k', converted])
		
		return converted
	
	# ACCESS / CONFIG
	
	def id(self):
		return self._id
	
	def get_config(self):
		return {
			"name": self._id,
			"filename": self._filename,
			"volume": int(self._volume * 100)
		}
	
	# CONTROL
	
	def play(self):
		# print 'play: {}'.format(self._id)
		pygame.mixer.music.play(-1)
	
	def stop(self):
		# print 'stop: {}'.format(self._id)
		pygame.mixer.music.fadeout(5000)
		self._enabled = False
	
	def vol(self, vol):
		self._volume = float(vol) / 100
		pygame.mixer.music.set_volume(self._volume)
	
	def play_if_required(self):
		if self.is_playing() == False and self._enabled == True:
			self.play()
	
	def is_playing(self):
		return pygame.mixer.music.get_busy()


class sequencer:
	sounds = {}
	name = None
	
	def __init__(self):
		pygame.mixer.init(44100, -16, 2, 2048)
	
	def setup(self, configfile):
		# load config file
		fp = open(configfile)
		config = json.load(fp)
		fp.close()
		
		self.name = config['name']
		
		# turn config into sounds
		for sound in config['sounds']:
			if sound['id'] == 'music':
				self.add_music(sound['name'], sound['filename'], sound['volume'])
			else:
				self.add_sound(sound['id'], sound['name'], sound['filename'], sound['volume'], sound['loop'], sound['frequency'])
	
	def add_sound(self, id, nicename, filename, volume, loop, frequency):
		# adjust freq if looping
		if loop:
			frequency = 0
		# check not double assigning
		id = str(id)
		if self.sounds.has_key(id) == False:
			self.sounds[id] = sound(nicename, filename, volume, loop, frequency)
			print "{}: {}".format(id, os.path.basename(filename))
		else:
			print "Error loading {} as id {} is already taken by {}".format(filename, id, self.sounds[id].id())
	
	def add_music(self, nicename, filename, volume):
		# check not double assigning
		self.sounds["music"] = music(nicename, filename, volume)
		print "music: {}".format(os.path.basename(filename))
	
	def command(self, action, id, val):
		# print action, id, val
		if action == 'dump':
			data = {"name":self.name, "sounds":[]}
			for id, sound in self.sounds.items():
				snd_config = sound.get_config()
				snd_config['id'] = id
				data['sounds'].append(snd_config)
			print json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
			return True
		
		id = str(id)
		# map 0xFFFF to music channel
		if (id == "65535"):
			id = "music"
		
		if self.sounds.has_key(id) == False:
			print "{}: {} - no such index".format(action, id)
			return False
		sound = self.sounds[id]
		
		if action == 'play':
			sound.play()
		if action == 'stop':
			sound.stop()
		if action == 'loop':
			sound.loop(val)
		if action == 'vol':
			sound.vol(val)
		if action == 'freq':
			sound.freq(val)
	
	def run(self):
		while True:
			for sound in self.sounds:
				self.sounds[sound].play_if_required()
			time.sleep(0.5)
