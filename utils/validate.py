import os

#List of files that are required for bot feature functionality
#Any files listed not present in the res folder will be automatically created
files = ['terms.txt', 'tally.json', 'tags.json', 'filesources.json', 'serverids.json']

def validate():
	try:
		if os.path.exists("res/") == False:
			print("Creating resource directory")
			os.mkdir("res/")
		if os.listdir("res/") != sorted(files):
			for file in list(set(files) - set(os.listdir("res/"))):
				print(files,os.listdir("res/"),file)
				open("res/{}".format(file), 'a').close()
				print(f"Created {file}")
		return True
	except:
		return False

validate()