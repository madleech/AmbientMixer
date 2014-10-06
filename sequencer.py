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
			if sound.has_key('filenames'):
				self.sounds[sound['name']] = audio.related_sounds(sound['name'], sound['filenames'], sound['volume'], sound['loop'], sound['frequency'])
			else:
				self.sounds[sound['name']] = audio.sound(sound['name'], sound['filename'], sound['volume'], sound['loop'], sound['frequency'])
	
	# load in each backgound sound file
	def setup_background_sounds(self, sounds):
		for sound in sounds:
			self.background_sounds[sound['name']] = audio.background_sound(sound['name'], sound['filename'], sound['volume'])
	
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
			adjustment = sleep(0.5)
			for sound in self.sounds:
				if adjustment > 0:
				# delay next play of sounds to account for slip in clock
					self.sounds[sound].delay_by(adjustment)
				else:
					self.sounds[sound].play_if_required()

	
# detect if computer has paused for a long time
def sleep(delay):
	start = time.time()
	time.sleep(delay)
	end = time.time()
	# slept for longer than expected?
	slip = int(end - start)
	if (slip > 0):
		print "Time slipped by {}".format(slip)
	return slip
