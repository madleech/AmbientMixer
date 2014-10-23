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

# a single sound sample
class sound:
	_length = 0
	_next_play = 0
	_playing = False
	_started_at = 0
	_volume = 0
	_frequency = 0
	
	def __init__(self, name, filename, volume, loop, frequency):
		# properties
		self._name = name
		
		if loop:
			frequency = 0
		
		# file converted, load into pygame sound
		self._filename = convert_to_wav(filename)
		self._sound = pygame.mixer.Sound(self._filename)
		self._length = self._sound.get_length()
		self.vol(volume)
		self.loop(loop)
		self.freq(frequency)

	
	# ACCESS / CONFIG
	
	def get_config(self):
		return {
			"name": self._name,
			"filename": self._filename,
			"volume": int(self._volume * 100),
			"frequency": int(self._frequency * 100),
			"loop": self._loop
		}
	
	# CONTROL
	
	def play(self):
		# print 'play: {}'.format(self._name)
		self._playing = True
		self._started_at = time.time()
		if self._loop:
			self._frequency = 0
			self._sound.play(-1)
		else:
			self._sound.play()
	
	def stop(self):
		# print 'stop: {}'.format(self._name)
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
		if self._frequency > 0:
			self._loop = False
	
	def vol(self, vol):
		self._volume = float(vol) / 100
		self._sound.set_volume(self._volume)
	
	# INTERNAL STATE
	
	def play_if_required(self):
		# disabled
		if self._frequency == 0 and self._loop == False:
			return
		
		# ignore stopped looping sounds
		if self._frequency <= 0 and self._loop == True:
			return
		
		if self._next_play == 0 and self._frequency > 0:
			self._next_play = time.time() + random.uniform(2, 10 / self._frequency)
			# print 'Next play of {} in {}s'.format(self._name, int(self._next_play - time.time()))
		
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
	
	def delay_by(self, delay):
		self._next_play += delay


# longer background music
class background_sound:
	_enabled = True
	_volume = 0
	
	def __init__(self, name, filename, volume):
		# properties
		self._filename = convert_to_wav(filename, True)
		self._name = name
		
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
	
	def get_config(self):
		return {
			"name": self._name,
			"filename": self._filename,
			"volume": int(self._volume * 100)
		}
	
	# CONTROL
	
	def play(self):
		# print 'play: {}'.format(self._name)
		if pygame.mixer.music.get_busy():
			pygame.mixer.music.fadeout(5000)
		pygame.mixer.music.load(self._filename)
		pygame.mixer.music.play(-1)
	
	def stop(self):
		# print 'stop: {}'.format(self._name)
		pygame.mixer.music.fadeout(5000)
		self._enabled = False
	
	def vol(self, vol):
		self._volume = float(vol) / 100
		pygame.mixer.music.set_volume(self._volume)
	
	# INTERNAL STATE
	
	def is_playing(self):
		return pygame.mixer.music.get_busy()


# several related sounds that are played randomly, but never at the same time
class related_sounds:
	_length = 0
	_next_play = 0
	_playing = False
	_started_at = 0
	_volume = 0
	_frequency = 0
	_filenames = []
	_sounds = []
	
	def __init__(self, name, files, volume, loop, frequency):
		# properties
		self._name = name
		
		if loop:
			frequency = 0
		
		# file converted, load into pygame sound
		self._filenames = [convert_to_wav(file) for file in files]
		self._sounds = [pygame.mixer.Sound(file) for file in self._filenames]
		self._volume = float(volume) / 100
		self.loop(loop)
		self.freq(frequency)

	
	# ACCESS / CONFIG
	
	def get_config(self):
		return {
			"name": self._name,
			"filenames": self._filenames,
			"volume": int(self._volume * 100),
			"frequency": int(self._frequency * 100),
			"loop": self._loop			
		}
	
	# CONTROL
	
	def random_sound(self):
		return random.choice(self._sounds)
		i = random.randrange(0, len(self._sounds))
		print i, self._filenames[i]
		return self._sounds[i]
	
	def play(self):
		# print 'play: {}'.format(self._name)
		if self.is_playing():
			self._sound.fadeout(1000)
		
		self._playing = True
		self._started_at = time.time()
		self._sound = self.random_sound()
		self._length = self._sound.get_length()
		self._sound.set_volume(self._volume)
		
		if self._loop:
			self._frequency = 0
			self._sound.play(-1)
		else:
			self._sound.play()
	
	def stop(self):
		# print 'stop: {}'.format(self._name)
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
			# print 'Next play of {} in {}s'.format(self._name, int(self._next_play - time.time()))
		
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
	
	def delay_by(self, delay):
		self._next_play += delay


# check format is correct - wav, 44khz, 16bit
def convert_to_wav(filename, fade = False):
	converted = re.sub('(.+)\.[a-z0-9A-Z]+', r'converted/\1.wav', os.path.basename(filename))
	
	# create output dir
	if os.path.exists('converted') == False:
		os.mkdir('converted')
	
	# convert if required
	if os.path.isfile(converted) == False:
		print 'converting {} to standard format'.format(filename)
		if fade:
			subprocess.call(['sox', filename, '-b 16', '-r 44k', converted, 'fade 0:5 0 0:5'])
		else:
			subprocess.call(['sox', filename, '-b 16', '-r 44k', converted])
	
	return converted