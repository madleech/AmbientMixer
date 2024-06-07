import time
import audio
import os.path
import pygame.mixer

class sequencer:
	sounds = {}
	background_sounds = {}
	mappings = []
	_mute = False
	
	def __init__(self):
		pygame.mixer.init(44100, -16, 2, 2048)
	
	# load in mappings
	def setup_mappings(self, mappings):
		self.mappings = mappings
	
	# load in each defined sound
	def setup_sounds(self, sounds, replace=True):
		# fade out old sounds
		if replace:
			for key, sound in list(self.sounds.items()):
				if sound.is_playing():
					print('Fading out {}...'.format(key))
					sound.fadeout()
				del self.sounds[key]
		
		# add new sounds
		for sound in sounds:
			if 'filename' in sound:
				sound['filenames'] = [sound['filename']]
			self.sounds[sound['name']] = audio.sound(sound['name'], sound['filenames'], sound['volume'], sound['loop'], sound['frequency'], sound['period'])
		
		# return config
		return self.get_config()['sounds']
	
	# load in each backgound sound file
	def setup_background_sounds(self, sounds, replace=True):
		# fade out old sounds
		if replace:
			for key, sound in list(self.background_sounds.items()):
				if sound.is_playing():
					sound.stop()
				del self.background_sounds[key]
		
		# add new sounds
		for sound in sounds:
			self.background_sounds[sound['name']] = audio.background_sound(sound['name'], sound['filename'], sound['volume'])
		
		# return config
		return self.get_config()['background_sounds']
	
	def has_sound(self, name):
		return name in self.sounds
	
	def has_background_sound(self, name):
		return name in self.background_sounds
	
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
		data = {"mappings":self.mappings, "sounds":[], "background_sounds":[]}
		for key, sound in list(self.sounds.items()):
			data['sounds'].append(sound.get_config())
		for key, sound in list(self.background_sounds.items()):
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
		if 'name' in attrs:
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
		if 'name' in attrs:
			del self.background_sounds[name]
			self.background_sounds[attrs['name']] = sound
	
	def mute(self, state):
		print('Muting: {}'.format(state))
		self._mute = state
		if state == True:
			pygame.mixer.pause()
		else:
			pygame.mixer.unpause()
	
	# given a set of data, convert it into a sound and action
	# - data is a hash
	def dispatch(self, data):
		for mapping in self.mappings:
			# mapping is listening for this loco and function
			if self.mapping_matches_packet(data, mapping):
				self.dispatch_action(mapping["action"], mapping["sound"])
	
	# does a mapping match a packet?
	# a blank match clause will match all packets
	def mapping_matches_packet(self, data, mapping):
		for key, value in mapping["match"].items():
			if key not in data:
				return False
			if isinstance(value, list) and data[key] not in value:
				return False
			if not isinstance(value, list) and data[key] != value:
				return False
		return True
	
	def dispatch_action(self, action, sound_name):
		sound = self.get_sound(sound_name)
		if not sound:
			print("No sound in sequencer named {}".format(sound_name))
			return
		
		if action == "play":
			print("Playing {}".format(sound_name))
			sound.play()
		elif action == "stop":
			print("Stopping {}".format(sound_name))
			sound.stop();
		else:
			print("Unknown action: {}".format(action))
			return
		
	# main run loop
	def run(self):
		while True:
			# pause so we don't use 100% CPU
			adjustment = sleep(0.5)
			for key, sound in list(self.sounds.items()):
				if adjustment > 0:
				# delay next play of sounds to account for slip in clock
					sound.delay_by(adjustment)
				elif self._mute == False:
					sound.play_if_required()

	
# detect if computer has paused for a long time
def sleep(delay):
	start = time.time()
	time.sleep(delay)
	end = time.time()
	# slept for longer than expected?
	slip = int(end - start)
	if (slip > delay):
		print("Time slipped by {}".format(slip))
	return slip - delay
