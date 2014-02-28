# -*- coding: UTF-8 -*-

import collections, nltk, re, en
from nltk.corpus import cess_esp as cess
from nltk.corpus import brown
from nltk import UnigramTagger as ut
from nltk.model import NgramModel
from nltk.probability import LidstoneProbDist
from nltk import FreqDist
from nltk.corpus import wordnet

class MachineTranslation:
	PUNCTUATION = [',', '.', '(', ')', '?']
	ENG_ADJECTIVE = ['JJ', 'JJR', 'JJS']
	ENG_NOUN = ['NN', 'NNS', 'NNP', 'NNPS']
	ENG_VERB = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

	ESP_ADJECTIVE = ['a', 'q', 'o', '0', 'c', 's', 'f', 'p', 'n']
	ESP_NOUN = ['n']
	ESP_VERB = ['vm', 'vs']
	ESP_VERB_PAST = ['vmii', 'vmis', 'vsii', 'vsis']

	NUMBER_PAT = "\d+"
	OPEN_QUESTION_MARK = '\xc2\xbf'
	
	def __init__(self):
		cess_sents = cess.tagged_sents()
		self.uni_tag = ut(cess_sents)

		self.translation = []
		self.dictionary = collections.defaultdict(lambda: 0)
		dictionaryFile = open("Dictionary.txt", 'r')
		for translation in dictionaryFile:
			spanish, english = translation.split(" - ")
			spanish = spanish.decode('utf-8')
			self.dictionary[spanish] = collections.defaultdict(lambda: [])
			english = english.rstrip(';\n').split('; ')
			for pos in english:
				pos = pos.split(': ')
				self.dictionary[spanish][pos[0]] = pos[1].split(', ')

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

			pos = self.uni_tag.tag(tokens)
			for word in pos:
				candidate = word[0].decode('utf-8')
				if candidate in self.PUNCTUATION or re.search(self.NUMBER_PAT, candidate):
					wordTranslation = candidate
				elif (word[1] and any(word[1].startswith(adj) for adj in self.ESP_ADJECTIVE) and 
					'adjective' in self.dictionary[candidate]):
					wordTranslation = self.dictionary[candidate]['adjective'][0]
				elif (word[1] and any(word[1].startswith(noun) for noun in self.ESP_NOUN) and
					'noun' in self.dictionary[candidate]):
					wordTranslation = self.dictionary[candidate]['noun'][0]
				elif (word[1] and any(word[1].startswith(verb) for verb in self.ESP_VERB) and
					'verb' in self.dictionary[candidate]):
					wordTranslation = self.verbConjugation(candidate, word)
				else:
					wordTranslation = self.pluralADJ(candidate)
				sentenceTranslation.append(wordTranslation)

			directTranslation = " ".join(map(str, sentenceTranslation))
			adjNounSwapped = self.adjNounSwap(directTranslation)
			nounSwapped = self.nounSwap(adjNounSwapped)
			pronounAdded = self.addPronoun(nounSwapped)
			possessives = self.possessive(pronounAdded)
			removedDeterminers = self.removeDeterminers(possessives)
			capAndNum = self.capitalizationAndNumbers(removedDeterminers)
			removeExtraSpace = re.sub(r' \'s', '\'s', capAndNum)
			removeExtraSpace = re.sub(r' ,', ',', removeExtraSpace)
			if removeExtraSpace[-2:] == " .":
				removeExtraSpace = removeExtraSpace[:-2] + "."
			elif removeExtraSpace[-2:] == " ?":
				removeExtraSpace = removeExtraSpace[:-2] + "?"
			self.translation.append(removeExtraSpace)

	# if question is a yes or no question, swap the order of first two words
	def questionSwap(self, sentence):
		sentence = sentence.lstrip(self.OPEN_QUESTION_MARK)
		#tokens = nltk.word_tokenize(sentence)
		#pos = self.uni_tag.tag(tokens)
		#return " ".join(map(str, tokens))
		return sentence

	# reverse the order of negation words and their objects
	def negationSwap(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = self.uni_tag.tag(tokens)

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
			if firstWord[1] in self.ENG_NOUN and secondWord[0]=='of' and word[1] in ['NNP', 'NNPS']:
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
			if firstWord[1] in self.ENG_NOUN and word[1] in self.ENG_ADJECTIVE:
				temp = tokens[i]
				tokens[i] = tokens[i+1]
				tokens[i+1] = temp
			firstWord = word

		return " ".join(map(str, tokens))

	def addPronoun(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = nltk.pos_tag(tokens)

		firstWord = pos[0]
		for i, word in enumerate(pos[1:]):
			if firstWord[1] not in self.ENG_NOUN and firstWord[0] != 'have' and firstWord[1] not in ['DT', 'TO', 'WP', 'RB', 'PRP', 'VBZ', '.', ','] and (word[1] in self.ENG_VERB or word[0]=='have'):
				if firstWord[1] == 'VBP' or (wordnet.synsets(word[0]) and not word[0].endswith('s')):
					tokens[i+1] = "they " + tokens[i+1]
				else:
					tokens[i+1] = "it " + tokens[i+1]
			firstWord = word

		if pos[0][1] in self.ENG_VERB or pos[0][0]=='have':
			if pos[0][1] == 'VBP' or (wordnet.synsets(word[0]) and not word[0].endswith('s')):
				tokens[0] = "They " + tokens[0]
			else:
				tokens[0] = "It " + tokens[0]

		return " ".join(map(str, tokens))

	def pluralADJ(self, token):
		translation = self.dictionary[token]['default'][0]
		pos = self.uni_tag.tag(nltk.word_tokenize(token))
		if pos[0][1] is not None and pos[0][1].startswith('a') and 'p' in pos[0][1]:
			if translation.endswith('s'):
				if wordnet.synsets(translation[:-1]):
					translation = translation[:-1]
		return translation

	def removeDeterminers(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = nltk.pos_tag(tokens)

		removeOf = []

		firstWord = pos[0]
		for i, word in enumerate(pos[1:]):
			if firstWord[1] in ['DT'] and word[1] in ['NNP', 'NNPS', 'NNS']:
				removeOf.append(i)
			firstWord = word

		if len(removeOf) != 0:
			for i in reversed(removeOf):
				tokens.pop(i)

		return " ".join(map(str, tokens))

	def capitalizationAndNumbers(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		tokens[0] = tokens[0].capitalize()

		pos = nltk.pos_tag(tokens)

		days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
		months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

		for i, word in enumerate(pos):
			if word[1] in ['NNP', 'NNPS']:
				tokens[i] = tokens[i].capitalize()

			if word[1] in ['CD']:
				tokens[i] = re.sub(r'\.', ',', tokens[i])

			if word[0] in days or word[0] in months:
				tokens[i] = tokens[i].capitalize()

		newTokens = []
		for i, token in enumerate(tokens):
			if token.lower() == 'a' and i+1<len(tokens):
				if any(tokens[i+1].startswith(vp) for vp in ['a', 'e', 'i', 'o', 'u']):
					if i==0:
						newTokens.append('An')
					else:
						newTokens.append('an')
				else:
					newTokens.append(token)
			else:
				newTokens.append(token)

		return " ".join(map(str, newTokens))

	def verbConjugation(self, candidate, word):
		wordTranslation = en.verb.present(self.dictionary[candidate]['verb'][0], person=word[1][4])
		
		if word[1][2] == 'p':
			wordTranslation = en.verb.present_participle(self.dictionary[candidate]['verb'][0])

		if word[1][3] == 's':
			wordTranslation = en.verb.past(self.dictionary[candidate]['verb'][0], person=word[1][4])

			if word[1][2] == 'p':
				wordTranslation = en.verb.past_participle(self.dictionary[candidate]['verb'][0])

		return wordTranslation

MT = MachineTranslation()
MT.translate()
for i, translation in enumerate(MT.translation):
	print '{0}) {1}'.format(i + 1, translation)
