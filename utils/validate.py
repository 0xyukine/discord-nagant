import os

files = ['terms.txt', 'tally.json', 'tags.json']

def validate():
	try:
		if os.path.exists("res/") == False:
			print("Creating resource directory")
			os.mkdir("res/")
		if os.listdir("res/") != sorted(files):
			print("Creating files")
			for file in list(set(files) - set(os.listdir("res/"))):
				print(files,os.listdir("res/"),file)
				open("res/{}".format(file), 'a').close()
		return True
	except:
		return False

validate()