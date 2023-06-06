import os
import json
from json.decoder import JSONDecodeError

def load():
	tally = {}
	tags = {}
	with open('res/terms.txt', 'r') as x:
		terms = x.read().split(",")
	try:
		with open('res/tally.json', 'r') as x:
			tally = json.load(x)
	except JSONDecodeError:
		pass
	try:
		with open('res/tags.json', 'r') as x:
			tags = json.load(x)
	except JSONDecodeError:
		pass

	return terms, tally, tags

async def save(message, **kwargs):
	try:
		if "tally" in kwargs.keys():
			with open('res/tally.json', 'w') as x:
				json.dump(kwargs["tally"], x, indent=4)
	except Exception as e:
		print(e)
	try:
		if "tags" in kwargs.keys():
			with open('res/tags.json', 'w') as x:
				json.dump(kwargs["tags"], x, indent=4)
	except Exception as e:
		print(e)