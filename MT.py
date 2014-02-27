# -*- coding: UTF-8 -*-

import collections, nltk, re
from nltk.corpus import cess_esp as cess
from nltk import BigramTagger as bt

class MachineTranslation:
	PUNCTUATION = [',', '.', '(', ')', '?']
	ADJECTIVE = ['JJ', 'JJR', 'JJS']
	NOUN = ['NN', 'NNS', 'NNP', 'NNPS']
	VERB = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
	NUMBER_PAT = "\d+"

	def __init__(self):
		cess_sents = cess.tagged_sents()
		self.bi_tag = bt(cess_sents)

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
			negationSwapped = self.negationSwap(sentence)
			tokens = nltk.word_tokenize(negationSwapped)
			for token in tokens:
				token = token.decode('utf-8')
				if token in self.PUNCTUATION or re.search(self.NUMBER_PAT, token):
					wordTranslation = token
				else:
					wordTranslation = self.dictionary[token]
				sentenceTranslation.append(wordTranslation)

			directTranslation = " ".join(map(str, sentenceTranslation))
			adjNounSwapped = self.adjNounSwap(directTranslation)
			self.translation.append(adjNounSwapped)

	def adjNounSwap(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = nltk.pos_tag(tokens)

		firstWord = pos[0]
		for i, word in enumerate(pos[1:]):
			if firstWord[1] in self.NOUN and word[1] in self.ADJECTIVE:
				temp = tokens[i]
				tokens[i] = tokens[i+1]
				tokens[i+1] = temp
			firstWord = word

		return " ".join(map(str, tokens))

	def negationSwap(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = self.bi_tag.tag(tokens)

		firstWord = pos[0]
		for i, word in enumerate(pos[1:]):
			if firstWord[0].lower() == "no" and word[1] is not None and (word[1].startswith('vs') or word[1].startswith('vm')):
				tokens[i] = tokens[i+1]
				tokens[i+1] = "not"
			firstWord = word

		firstWord = pos[0]
		secondWord = pos[1]
		for i, word in enumerate(pos[2:]):
			if firstWord[0].lower() == "no" and secondWord[1] is not None and secondWord[1].startswith('pp'):
				if word[1] is not None and (word[1].startswith('vs') or word[1].startswith('vm')):
					tokens[i] = tokens[i+1]
					tokens[i+1] = "does not"
			firstWord = word

		return " ".join(map(str, tokens))

MT = MachineTranslation()
MT.translate()
for i, translation in enumerate(MT.translation):
	print '{0}) {1}'.format(i + 1, translation)
