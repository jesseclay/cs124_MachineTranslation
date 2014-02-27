
import collections, nltk

class MachineTranslation:

	def __init__(self):
		self.adjective = ['JJ', 'JJR', 'JJS']
		self.noun = ['NN', 'NNS', 'NNP', 'NNPS']

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

			directTranslation = " ".join(map(str, sentenceTranslation))
			adjNounSwapped = self.adjNounSwap(directTranslation)
			self.translation.append(adjNounSwapped)

	def adjNounSwap(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		pos = nltk.pos_tag(tokens)

		firstWord = pos[0]
		for i, word in enumerate(pos[1:]):
			if firstWord[1] in self.noun and word[1] in self.adjective:
				temp = tokens[i]
				tokens[i] = tokens[i+1]
				tokens[i+1] = temp
			firstWord = word

		return " ".join(map(str, tokens))

MT = MachineTranslation()
MT.translate()
print MT.translation

