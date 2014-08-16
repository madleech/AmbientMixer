import time
import audio
import os.path
import pygame.mixer

class sequencer:
	sounds = {}
	background_sounds = {}
	
	def __init__(self):
		pygame.mixer.init(44100, -16, 2, 2048)
	
	# load in each defined sound
	def setup_sounds(self, sounds):
		for sound in sounds:
			self.sounds[sound['name']] = audio.sound(sound['name'], sound['filename'], sound['volume'], sound['loop'], sound['frequency'])
			#print "{}: {}".format(sound['name'], os.path.basename(filename))
	
	# load in each backgound sound file
	def setup_background_sounds(self, sounds):
		for sound in sounds:
			self.background_sounds[sound['name']] = audio.background_sound(sound['name'], sound['filename'], sound['volume'])
			#print "{}: {}".format(sound['name'], os.path.basename(filename))
	
	def has_sound(self, name):
		return self.sounds.has_key(name)
	
	def has_background_sound(self, name):
		return self.background_sounds.has_key(name)
	
	def get_sound(self, name):
		if not self.has_sound(name):
			return None
		else:
			return self.sounds[name]
	
	def get_background_sound(self, name):
		if not self.has_background_sound(name):
			return None
		else:
			return self.background_sounds[name]
	
	def get_config(self):
		data = {"sounds":[], "background_sounds":[]}
		for key, sound in self.sounds.items():
			data['sounds'].append(sound.get_config())
		for key, sound in self.background_sounds.items():
			data['background_sounds'].append(sound.get_config())
		return data
	
	# main run loop
	def run(self):
		while True:
			# pause so we don't use 100% CPU
			adjustment = self.sleep(0.5)
			if adjustment > 0:
				# delay next play of sounds to account for slip in clock
				for sound in self.sounds:
					self.sounds[sound].delay_by(adjustment)
			for sound in self.sounds:
				self.sounds[sound].play_if_required()
	
	# detect if computer has paused for a long time
	def sleep(self, delay):
		start = time.time()
		time.sleep(delay)
		end = time.time()
		# slept for longer than expected?
		slip = int(end - start)
		if (slip > 0):
			print "Time slipped by {}".format(slip)
		return slip
