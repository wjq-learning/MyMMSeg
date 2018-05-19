#coding=utf-8
import math

class Word(object):
    def __init__(self, text='', freq=0):
        self.text = text
        self.freq = freq
        self.length = len(self.text)


class Chunk(object):
    def __init__(self, w1, w2=None, w3=None):
        self.words = []
        self.words.append(w1)
        if w2:
            self.words.append(w2)
        if w3:
            self.words.append(w3)

    def totalWordLength(self):
        sum = 0
        for word in self.words:
            sum += word.length
        return sum

    def averageWordLength(self):
        average = float(self.totalWordLength())/float(len(self.words))
        return average

    def standardDeviation(self):
        sum = 0.0
        for word in self.words:
            sum += math.pow(word.freq-self.averageWordLength(), 2)
        stanDevia = sum / len(self.words)
        return stanDevia

    def wordFrequency(self):
        sum = 0.0
        for word in self.words:
            if word.length==1:
                sum += word.freq
        return sum


class ComplexCompare(object):
    def takeHightest(self, chunks, comparator):
        i = 1
        for j in range(1, len(chunks)):
            rlt = comparator(chunks[j], chunks[0])
            if rlt > 0:
                i = 0
            if rlt >= 0:
                chunks[i], chunks[j] = chunks[j], chunks[i]
                i += 1
        # i = 0
        # for j in range(1, len(chunks)):
        # 	rlt = comparator(chunks[j], chunks[0])
        # 	if rlt > 0:
        # 		i = 0
        # 		chunks[i], chunks[j] = chunks[j], chunks[i]
        # 	if rlt == 0:
        # 		i += 1
        # 		chunks[i], chunks[j] = chunks[j], chunks[i]
         # i += 1
        return chunks[0: i]

    def mmFilter(self, chunks):
        def comparator(a, b):
            return a.totalWordLength() - b.totalWordLength()
        return self.takeHightest(chunks, comparator)

    def lawlFilter(self, chunks):
        def comparator(a, b):
            return a.averageWordLength() - b.averageWordLength()
        return self.takeHightest(chunks, comparator)

    def svmlFilter(self, chunks):
        def comparator(a, b):
            return a.standardDeviation() - b.standardDeviation()
        return self.takeHightest(chunks, comparator)

    def logFreqFilter(self, chunks):
        def comparator(a, b):
            return a.wordFrequency() - b.wordFrequency()
        return self.takeHightest(chunks, comparator)

dictword = {}
maxWordLength = 0

def loadDictChars(filepath):
    global maxWordLength
    fsock = open(filepath, encoding='utf-8')
    for line in fsock.readlines():
        word, freq = line.split('\t')
        word = str(word)
        dictword[word] = (len(word), int(freq))
        maxWordLength = maxWordLength < len(word) and len(word) or maxWordLength
    fsock.close()

def loadDictWords(filepath):
    global maxWordLength
    fsock = open(filepath, encoding='utf-8')
    for line in fsock.readlines():
        word = str(line.strip())
        dictword[word] = (len(word), 0)
        maxWordLength = maxWordLength < len(word) and len(word) or maxWordLength
    fsock.close()

def getDictWord(word):
    result = dictword.get(word)
    if result:
        return Word(word, result[1])
    return None

def run():
    from os.path import join, dirname
    loadDictChars(join(dirname(__file__), 'data', 'char_freq.txt'))
    # print('loadDictChars Done!')
    loadDictWords(join(dirname(__file__), 'data', 'words.txt'))
    # print('loadDictWords Done!')


class Analysis:
    def __init__(self, text):
        if isinstance(text, str):
            self.text = text
        else:
            self.text = str(text, 'utf-8')
        self.pos = 0
        self.textLength = len(self.text)
        self.complexCompare = ComplexCompare()
        # self.cacheSize = 3
        # self.cache = []
        # self.cacheIndex = 0

        # for i in range(self.cacheSize):
        #     self.cache.append([-1, Word()])

        if not dictword:
            run()

    def __iter__(self):
        while True:
            token = self.getNextToken()
            if token == None:
                raise StopIteration
            yield token

    def getNextChar(self):
        return self.text[self.pos]

    def isChineseChar(self, character):
        return 0x4E00 <= ord(character) <= 0x9FA5

    def isASCIIChar(self, ch):
        import string
        if ch in string.whitespace:
            return False
        if ch in string.punctuation:
            return False
        return ch in string.printable

    def getNextToken(self):
        while self.pos < self.textLength:
            if self.isChineseChar(self.getNextChar()):
                token = self.getChineseWords()
            else:
                token = self.getASCIIWords() + '/'
            if len(token) > 0:
                return token
        return None

    def getASCIIWords(self):
        while self.pos < self.textLength:
            ch = self.getNextChar()
            if self.isASCIIChar(ch) or self.isChineseChar(ch):
                break
            self.pos += 1
        start = self.pos
        while self.pos < self.textLength:
            ch = self.getNextChar()
            if not self.isASCIIChar(ch):
                break
            self.pos += 1
        end = self.pos
        return self.text[start:end]

    def getChineseWords(self):
        chunks = self.createChunks()
        if len(chunks) > 1:
            chunks = self.complexCompare.mmFilter(chunks)
            chunks = self.complexCompare.lawlFilter(chunks)
            chunks = self.complexCompare.svmlFilter(chunks)
            chunks = self.complexCompare.logFreqFilter(chunks)
        if len(chunks) == 0:
            return ''
        words = chunks[0].words
        token = ""
        length = 0
        for word in words:
            if word.length != -1:
                token += word.text + "/"
                length += word.length
        self.pos += length
        return token

    def createChunks(self):
        chunks = []
        aPos = self.pos
        words1 = self.getMatchChineseWords()
        for word1 in words1:
            self.pos += len(word1.text)
            if self.pos < self.textLength:
                words2 = self.getMatchChineseWords()
                for word2 in words2:
                    self.pos += len(word2.text)
                    if self.pos < self.textLength:
                        words3 = self.getMatchChineseWords()
                        for word3 in words3:
                            if word3.length == -1:
                                chunk = Chunk(word1,word2)
                            else:
                                chunk = Chunk(word1,word2, word3)
                            chunks.append(chunk)
                    elif self.pos == self.textLength:
                        chunks.append(Chunk(word1,word2))
                    self.pos -= len(word2.text)
            elif self.pos == self.textLength:
                chunks.append(Chunk(word1))
            self.pos -= len(word1.text)
        self.pos = aPos
        # for chunk in chunks:
        #     print(chunk.words[0].text,chunk.words[1].text, chunk.words[2].text)
        return chunks

    def getMatchChineseWords(self):
        # for i in range(self.cacheSize):
        #     if self.cache[i][0]==self.pos:
        #         return self.cache[i][1]

        aPos= self.pos
        words = []
        index = 0
        while self.pos < self.textLength:
            if index >= maxWordLength:
                break
            if not self.isChineseChar(self.getNextChar()):
                break
            self.pos += 1
            index += 1
            text = self.text[aPos: self.pos]
            word = getDictWord(text)
            if word:
                words.append(word)
        self.pos = aPos
        if not words:
            word = Word()
            word.length = -1
            words.append(word)
        # self.cache[self.cacheIndex] = (self.pos, words)
        # self.cacheIndex += 1
        # if self.cacheIndex >= self.cacheSize:
        #     self.cacheIndex = 0
        return words

def cuttest(text):
    tmp = ""
    wlist = [word for word in Analysis(text)]
    for w in wlist:
        tmp += w
    print(tmp)
    print("==============================")
