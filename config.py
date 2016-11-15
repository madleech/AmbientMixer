# coding=utf-8

import json
import time
import os.path

class config:
	_name = ''
	
	def __init__(self, sequencer, filename=None):
		self.sequencer = sequencer
		self.filename = filename
		if os.path.exists(self.filename):
			self.load()
	
	# load in and parse the JSON config file
	def load(self):
		# load config file
		fp = open(self.filename)
		config = json.load(fp)
		fp.close()
		
		return self.apply(config)
	
	# save config to a local JSON file
	def save(self):
		fp = open(self.filename, 'w')
		json.dump(self.get(), fp)
		fp.close()
		print u'✓ Saved configuration to {}'.format(self.filename).encode('utf-8')
	
	def periodic_save(self):
		while True:
			time.sleep(10)
			self.save()
	
	def set(self, json_data):
		config = json.loads(json_data)
		return self.apply(config)
	
	# apply a config
	def apply(self, settings):
		if settings.has_key("name"):
			self._name = settings['name']
		
		# configure sequencer
		if settings.has_key("sounds"):
			self.sequencer.setup_sounds(settings['sounds'])
		if settings.has_key("background_sounds"):
			self.sequencer.setup_background_sounds(settings['background_sounds'])
		if settings.has_key("mappings"):
			self.sequencer.setup_mappings(settings['mappings'])
		
		# success
		return True
	
	def get(self):
		data = {
			"name":self._name,
			"sounds":[],
			"background_sounds":[],
			"mappings":[]
		}
		# configure sequencer
		for key, sound in self.sequencer.sounds.items():
			data['sounds'].append(sound.get_config())
		for key, sound in self.sequencer.background_sounds.items():
			data['background_sounds'].append(sound.get_config())
		
		# configure UBUS server
		data['mappings'] = self.sequencer.mappings
		
		return data
