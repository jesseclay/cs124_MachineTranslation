# -*- coding: UTF-8 -*-

import collections, nltk

class MachineTranslation:

	def __init__(self):
		self.translation = []
		self.dictionary = collections.defaultdict(lambda: 0)
		dictionaryFile = open("Dictionary.txt", 'r')
		for translation in dictionaryFile:
			spanish, english = translation.split(" - ")
			self.dictionary[spanish.decode('utf-8')] = english.rstrip('\n')

		self.sentences = []
		sentencesFile = open("DevSet.txt", 'r')
		for sentence in sentencesFile:
			self.sentences.append(sentence.rstrip('\n'))

	def translate(self):
		for sentence in self.sentences:
			sentenceTranslation = []
			tokens = nltk.word_tokenize(sentence)
			for token in tokens:
				token = token.decode('utf-8')
				wordTranslation = self.dictionary[token]
				sentenceTranslation.append(wordTranslation)
			print sentenceTranslation
			self.translation.append(" ".join(map(str, sentenceTranslation)))

MT = MachineTranslation()
MT.translate()