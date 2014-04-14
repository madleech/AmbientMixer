from os import walk

def list(path):
	f = []
	for (dirpath, dirnames, filenames) in walk(path):
		for file in filenames:
			f.append(path + '/' + file)
		break
	return f

