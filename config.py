import json

# load in and parse the JSON config file
def load(file):
	# load config file
	fp = open(file)
	config = json.load(fp)
	fp.close()
	
	return config
