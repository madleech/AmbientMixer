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
	def setup_sounds(self, sounds, replace=True):
		# fade out old sounds
		if replace:
			for key, sound in self.sounds.items():
				if sound.is_playing():
					print 'Fading out {}...'.format(key)
					sound.fadeout()
				del self.sounds[key]
		
		# add new sounds
		for sound in sounds:
			if sound.has_key('filename'):
				sound['filenames'] = [sound['filename']]
			self.sounds[sound['name']] = audio.sound(sound['name'], sound['filenames'], sound['volume'], sound['loop'], sound['frequency'], sound['period'])
		
		# return config
		return self.get_config()['sounds']
	
	# load in each backgound sound file
	def setup_background_sounds(self, sounds, replace=True):
		# fade out old sounds
		if replace:
			for key, sound in self.background_sounds.items():
				if sound.is_playing():
					sound.stop()
				del self.background_sounds[key]
		
		# add new sounds
		for sound in sounds:
			self.background_sounds[sound['name']] = audio.background_sound(sound['name'], sound['filename'], sound['volume'])
		
		# return config
		return self.get_config()['background_sounds']
	
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
	
	def remove_sound(self, key):
		if self.has_sound(key):
			self.sounds[key].fadeout(500)
			del self.sounds[key]
		return True
	
	def get_config(self):
		data = {"sounds":[], "background_sounds":[]}
		for key, sound in self.sounds.items():
			data['sounds'].append(sound.get_config())
		for key, sound in self.background_sounds.items():
			data['background_sounds'].append(sound.get_config())
		return data
	
	def update_sound_config(self, name, attrs):
		# get sound
		sound = self.get_sound(name)
		if sound == None:
			raise Exception("Sound {} not found".format(name))
		# adjust config
		sound.update_config(attrs)
		# rename if required
		if attrs.has_key('name'):
			del self.sounds[name]
			self.sounds[attrs['name']] = sound
	
	def update_background_sound_config(self, name, attrs):
		# get sound
		sound = self.get_background_sound(name)
		if sound == None:
			raise Exception("Sound {} not found".format(name))
		# adjust config
		sound.update_config(attrs)
		# rename if required
		if attrs.has_key('name'):
			del self.background_sounds[name]
			self.background_sounds[attrs['name']] = sound
	
	def mute(self, state):
		print 'Muting: {}'.format(state)
		if state == True:
			pygame.mixer.pause()
		else:
			pygame.mixer.unpause()
	
	# main run loop
	def run(self):
		while True:
			# pause so we don't use 100% CPU
			adjustment = sleep(0.5)
			for key, sound in self.sounds.items():
				if adjustment > 0:
				# delay next play of sounds to account for slip in clock
					sound.delay_by(adjustment)
				else:
					sound.play_if_required()

	
# detect if computer has paused for a long time
def sleep(delay):
	start = time.time()
	time.sleep(delay)
	end = time.time()
	# slept for longer than expected?
	slip = int(end - start)
	if (slip > delay):
		print "Time slipped by {}".format(slip)
	return slip - delay
