
import collections, nltk

class MachineTranslation:

	def __init__(self):
		self.translation = []
		self.dictionary = collections.defaultdict(lambda: 0)
		dictionaryFile = open("Dictionary.txt", 'r')
		for translation in dictionaryFile:
			spanish, english = translation.split(" - ")
			self.dictionary[spanish] = english.rstrip('\n')

		self.sentences = []
		sentencesFile = open("DevSet.txt", 'r')
		for sentence in sentencesFile:
			self.sentences.append(sentence.rstrip('\n'))

	def translate(self):
		for sentence in self.sentences:

			sentenceTranslation = []
			tokens = nltk.word_tokenize(sentence)
			for token in tokens:
				wordTranslation = self.dictionary[token]
				sentenceTranslation.append(wordTranslation)
			self.translation.append(" ".join(map(str, sentenceTranslation)))

	def showTranslation(self):
		for sentence in self.translation:
			print sentence

MT = MachineTranslation()
MT.translate()
MT.showTranslation()

