import json

class config:
	def __init__(self, sequencer, ubus_server):
		self.sequencer = sequencer
		self.ubus_server = ubus_server
	
	# load in and parse the JSON config file
	def load(self, file):
		# load config file
		fp = open(file)
		config = json.load(fp)
		fp.close()
		
		return self.apply(config)
	
	def set(self, json_data):
		config = json.loads(json_data)
		return self.apply(config)
	
	# apply a config
	def apply(self, settings):
		# configure sequencer
		if settings.has_key("sounds"):
			self.sequencer.setup_sounds(settings['sounds'])
		if settings.has_key("background_sounds"):
			self.sequencer.setup_background_sounds(settings['background_sounds'])
		
		# configure UBUS server
		if settings.has_key("ubus_mappings"):
			self.ubus_server.setup(settings['ubus_mappings'])
	
	def get(self):
		data = {
			"sounds":[], 
			"background_sounds":[],
			"ubus_mappings":[]
		}
		# configure sequencer
		for key, sound in self.sequencer.sounds.items():
			data['sounds'].append(sound.get_config())
		for key, sound in self.sequencer.background_sounds.items():
			data['background_sounds'].append(sound.get_config())
		
		# configure UBUS server
		data['ubus_mappings'] = self.ubus_server.get_config()
		
		return data

