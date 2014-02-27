# -*- coding: UTF-8 -*-

import collections, nltk, re
from nltk.corpus import cess_esp as cess
from nltk.corpus import brown
from nltk import BigramTagger as bt
from nltk.model import NgramModel
from nltk.probability import LidstoneProbDist
from nltk import FreqDist
from pattern.en import conjugate

class MachineTranslation:
	PUNCTUATION = [',', '.', '(', ')', '?']
	ADJECTIVE = ['JJ', 'JJR', 'JJS']
	NOUN = ['NN', 'NNS', 'NNP', 'NNPS']
	VERB = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
	VERB_PAST = ['VBD', 'VBN']
	NUMBER_PAT = "\d+"
	OPEN_QUESTION_MARK = '\xc2\xbf'
	
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
			questionSwapped = sentence
			if sentence.startswith(self.OPEN_QUESTION_MARK):
				questionSwapped = self.questionSwap(sentence)
			negationSwapped = self.negationSwap(questionSwapped)
			tokens = nltk.word_tokenize(negationSwapped)

			pos = self.bi_tag.tag(tokens)
			print pos
			for word in pos:
				candidate = word[0].decode('utf-8')
				if candidate in self.PUNCTUATION or re.search(self.NUMBER_PAT, candidate):
					wordTranslation = candidate
				elif word[1] in self.VERB_PAST:
					print 'PAST VERB!!'
					wordTranslation = self.dictionary[candidate] + 'ed'
				else:
					wordTranslation = self.dictionary[candidate]
				sentenceTranslation.append(wordTranslation)

			directTranslation = " ".join(map(str, sentenceTranslation))
			adjNounSwapped = self.adjNounSwap(directTranslation)
			nounSwapped = self.nounSwap(adjNounSwapped)
			possessives = self.possessive(nounSwapped)
			self.translation.append(possessives)

	# if question is a yes or no question, swap the order of first two words
	def questionSwap(self, sentence):
		sentence = sentence.lstrip(self.OPEN_QUESTION_MARK)
		#tokens = nltk.word_tokenize(sentence)
		#pos = self.bi_tag.tag(tokens)
		#return " ".join(map(str, tokens))
		return sentence

	# reverse the order of negation words and their objects
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
			firstWord = secondWord
			secondWord = word

		return " ".join(map(str, tokens))

	# switch position of possessive words to use apostrophe notation
	def possessive(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = nltk.pos_tag(tokens)

		removeOf = []

		firstWord = pos[0]
		secondWord = pos[1]
		for i, word in enumerate(pos[2:]):
			if firstWord[1] in self.NOUN and secondWord[0]=='of' and word[1] in ['NNP', 'NNPS']:
				temp = tokens[i]
				tokens[i] = tokens[i+2] + "'s"
				tokens[i+2] = temp
				removeOf.append(i+1)
			firstWord = secondWord
			secondWord = word

		if len(removeOf) != 0:
			for i in reversed(removeOf):
				tokens.pop(i)

		return " ".join(map(str, tokens))

	# fixes the "number of telephone" to "telephone number" example
	def nounSwap(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = nltk.pos_tag(tokens)

		removeOf = []

		firstWord = pos[0]
		secondWord = pos[1]
		for i, word in enumerate(pos[2:]):
			if firstWord[1] in ['NN', 'NNS'] and secondWord[0]=='of' and word[1] in ['NN', 'NNS']:
				temp = tokens[i]
				tokens[i] = tokens[i+2]
				tokens[i+2] = temp
				removeOf.append(i+1)
			firstWord = secondWord
			secondWord = word

		if len(removeOf) != 0:
			for i in reversed(removeOf):
				tokens.pop(i)

		return " ".join(map(str, tokens))

	def ngram(self, words):
		words = ['of', 'from', 'by', 'with', 'in']
		model = NgramModel(3, brown.words()) 
		for word in words:
			print "a judge "+word+" Miami"
		 	print model.prob(word, ["a judge "+word+" Miami"])

	# reverses order of adjacent adjectives and nouns
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

MT = MachineTranslation()
MT.translate()
for i, translation in enumerate(MT.translation):
	print '{0}) {1}'.format(i + 1, translation)
