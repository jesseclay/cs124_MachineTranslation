
import collections

class MachineTranslation:

	def __init__(self):
		self.dictionary = collections.defaultdict(lambda: 0)
		dictionaryFile = open("Dictionary.txt", 'r')
		for translation in dictionaryFile:
			spanish, english = translation.split(" - ")
			self.dictionary[spanish] = english.rstrip('\n')

MT = MachineTranslation()
