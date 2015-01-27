# coding=utf-8

# sequencer
# - load in an array of sounds into channels
# - each channel has:
#   - name
#   - file
#   - loop / frequency

import os
import re
import math
import time
import random
import os.path
import subprocess
import pygame.mixer

# several related sounds that are played randomly, but never at the same time
class sound:
	_length = 0
	_playing = False
	_started_at = 0
	_volume = 0
	_frequency = 0
	_period = 0
	_filenames = []
	_sounds = []
	_sound = None
	_mute = False
	_play_times = []
	_next_generate_times_at = 0
	
	def __init__(self, name, files, volume, loop, frequency, period):
		# properties
		self._name = name
		self._next_generate_times_at = time.time()
		
		if loop and frequency > 0:
			frequency = 0
		
		for file in files:
			if os.path.exists(file) == False:
				raise Exception("File not found: " + file)
		
		# file converted, load into pygame sound
		self._filenames = [convert_to_wav(file) for file in files]
		self._sounds = [pygame.mixer.Sound(file) for file in self._filenames]
		self._volume = float(volume) / 100
		self.loop(loop)
		self.freq(frequency, period)
		
		# kick things off
		self.calculate_play_times()
	
	# ACCESS / CONFIG
	
	def get_config(self):
		return {
			"name": self._name,
			"filenames": self._filenames,
			"volume": int(self._volume * 100),
			"frequency": int(self._frequency),
			"period": int(self._period),
			"loop": self._loop			
		}
	
	def update_config(self, attributes):
		for key, value in attributes.items():
			if key == 'filenames':
				self._filenames = value
			elif key == 'name':
				self._name = value
			elif key == 'volume':
				self.vol(value)
			elif key == 'frequency':
				self.freq(value, self._period)
			elif key == 'period':
				self.freq(self._frequency, value)
			elif key == 'loop':
				self.loop(value)
			elif key == 'filenames':
				# stop all sounds
				for sound in self._sounds:
					sound.stop()
				# replace with new sounds
				self._filenames = [convert_to_wav(file) for file in filenames]
				self._sounds = [pygame.mixer.Sound(file) for file in self._filenames]
				# regenerate play times
				self.calculate_play_times()
				
	
	# CONTROL
	
	def random_sound(self):
		return random.choice(self._sounds)
	
	def play(self):
		# print 'play: {}'.format(self._name)
		if self.is_playing():
			self._sound.fadeout(1000)
		
		if self._sound == None:
			self._sound = self.random_sound()
		
		self._playing = True
		self._started_at = time.time()
		self._sound.set_volume(self.get_playback_vol())
		print u'► {} ({})'.format(self._name, self._sound)
		
		if self._loop:
			self._frequency = 0
			self._sound.play(-1)
		else:
			self._sound.play()
		
		self._sound = None
	
	def play_sound_at_index(self, index):
		for sound in self._sounds:
			sound.stop()
		self._sounds[index].play()
	
	def stop_sound_at_index(self, index):
		self._sounds[index].stop()
	
	def mute(self, state):
		self._mute = state
		for sound in self._sounds:
			sound.set_volume(self.get_playback_vol())
	
	def get_playback_vol(self):
		if self._mute:
			return 0
		else:
			return self._volume
	
	def fadeout(self, amount=2500):
		self._sound.fadeout(amount)
		self.stop()
		time.sleep(amount / 1000)
	
	# stop a looped single sound -> stop playing
	# stop a looped multisound -> stop playing
	# stop a random sound -> don't play any more?
	def stop(self):
		# print 'stop: {}'.format(self._name)
		for sound in self._sounds:
			sound.stop()
		self._playing = False
		if self._loop == True:
			self._frequency = -1
	
	def loop(self, enable):
		self._loop = bool(enable)
		if self._loop == True:
			self._frequency = 0
	
	def freq(self, freq, period):
		self._frequency = freq
		self._period = period
		if self._frequency > 0:
			self._loop = False
	
	def vol(self, vol):
		self._volume = float(vol) / 100
		for sound in self._sounds:
			sound.set_volume(self.get_playback_vol())
	
	# INTERNAL STATE
	
	def play_if_required(self):
		# ignore stopped/disabled sounds
		if self._frequency == 0 or self._period == 0:
			return
		
		# need to regenerate play time
		if self._next_generate_times_at <= time.time() and self._frequency > 0 and self._period > 0:
			self.calculate_play_times()
		
		# time to play
		if self.time_to_play() and self.is_playing() == False:
			self.play()
	
	def time_to_play(self):
		if len(self._play_times) == 0:
			return False
		
		if self._play_times[0]['time'] <= time.time():
			self.set_sound(self._play_times[0]['sound'])
			del self._play_times[0] # remove this time
			return True
	
	def set_sound(self, index):
		self._sound = self._sounds[index]
	
	# return num sound indexes in a random order
	# if num > num_sounds, shuffle again and add to list, etc
	def random_sound_orders(self, num):
		result = []
		indexes = xrange(0, len(self._sounds))
		rand_indexes = []
		
		while len(result) < num:
			# generate more indexes?
			if len(rand_indexes) == 0:
				rand_indexes = random.sample(indexes, len(self._sounds))
			# append another random index to list
			result.append(rand_indexes.pop())
		return result
	
	# calculate times to play
	# 2 per 10mins = create bin 10mins long, place time randomly inside bin
	def calculate_play_times(self):
		if self._frequency <= 0 or self._period <= 0:
			return
		
		start = self._next_generate_times_at
		end = start + self._period
		num_plays = self._frequency
		
		# 1: create bins
		self._play_times = []
		for i in range(0, num_plays):
			self._play_times.append({'time': 0, 'sound': 0})
		
		# 2: assign sounds
		random_indexes = self.random_sound_orders(num_plays)
		for i in range(0, num_plays):
			self._play_times[i]['sound'] = random_indexes[i]
		
		# 3: calculate total time spent playing
		total_time = 0
		for i in range(0, num_plays):
			total_time += math.ceil(self._sounds[self._play_times[i]['sound']].get_length())
		
		# 4: assign play times
		remaining_time = int(self._period - total_time)
		
		# 4.1: ensure not too close together
		if remaining_time < num_plays:
			remaining_time = num_plays+1
		# 4.2: assign random starting inside this list
		times = random.sample(xrange(0, remaining_time), num_plays)
		# 4.3: sort times largest to smallest (so when we pop we get smallest time)
		times.sort()
		times.reverse()
		print '  [{}] frequency: {} every {}s, total time: {}s, remaining time: {}s, times: {}, starting at {}'.format(self._name, self._frequency, self._period, total_time, remaining_time, times, time.strftime('%H:%M:%S', time.localtime(start)))
		
		# 4.4: go through times, set each sound to start at this time, increase offset time by its length
		offset = 0
		for i in range(0, num_plays):
			self._play_times[i]['time'] = start + times.pop() + offset
			offset += self._sounds[self._play_times[i]['sound']].get_length()
		
		# 5: set next generate time
		self._next_generate_times_at = end
	
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
		for i, time in enumerate(self._play_times):
			self._play_times[i]['time'] += delay
		self._next_generate_times_at += delay


# longer background music
class background_sound:
	_enabled = True
	_volume = 0
	
	def __init__(self, name, filename, volume):
		if os.path.exists(filename) == False:
			raise Exception("File not found: " + filename)
		
		# properties
		self._filename = convert_to_wav(filename, True)
		self._name = name
		
		self.vol(volume)
		
		# start playing if first one
		if pygame.mixer.music.get_busy() == False:
			self.play()
	
	# MANAGE
	
	def update_config(self, attributes):
		for key, value in attributes.items():
			if key == 'filename':
				self._filename = value
			elif key == 'name':
				self._name = value
			elif key == 'volume':
				self.vol(value)
	
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

def converted_filename(filename):
	dir = '/tmp/converted'
	converted = re.sub('(.+)\.[a-z0-9A-Z]+', dir + r'/\1.wav', os.path.basename(filename))
	
	# create output dir
	if os.path.exists(dir) == False:
		os.mkdir(dir)
	
	return converted

# check format is correct - wav, 44khz, 16bit
def convert_to_wav_sox(filename, fade = False):
	converted = converted_filename(filename)
	
	# convert if required
	if os.path.isfile(converted) == False:
		if fade:
			cmd = ['sox', filename, '-b 16', '-r 44k', converted, 'fade 0:5 0 0:5']
		else:
			cmd = ['sox', filename, '-b 16', '-r 44k', converted]
		subprocess.call(cmd)
	
	return converted

def convert_to_wav(filename, fade = False):
	converted = converted_filename(filename)
	
	# convert if required
	if os.path.isfile(converted) == False:
		script = os.path.dirname(os.path.realpath(__file__)) + '/convert.sh'
		if fade:
			cmd = [script, filename, converted, "fade"]
		else:
			cmd = [script, filename, converted]
		subprocess.call(cmd)
	
	return converted

