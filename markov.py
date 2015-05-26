from collections import defaultdict, deque
from itertools import chain
import random
import os,sys

class MarkovChain(object):
    def __init__(self, documents, num=3):
        self.chain_length = num
        self.word_cache = defaultdict(list)
        self.words = self.documents_to_words(documents)
        self.word_size = len(self.words)
        self.wordbase = self.wordbase()
    
    def documents_to_words(self, documents):
        """Returns a list of words used in a given list of documents."""
        words = []
        for document in documents:
            if document:
                words.append(self.tokenize(document))
        #Chain
        return list(chain.from_iterable(words))
    
    def tokenize(self, document):
        # don't want empty spaces
        words = [w.strip() for w in document.split() if w.strip() != '']
        # Make many ???? into one ?
        return words

    def yield_trigrams(self):
        if len(self.words) < self.chain_length:
            return

        for i in range(len(self.words) - self.chain_length):
            yield_chain = [self.words[i+j] for j in range(self.chain_length)]
            yield (deque(yield_chain))

    def wordbase(self):
        for w1, w2, w3 in self.yield_trigrams():
            self.word_cache[(w1, w2)].append(w3)

    def generate_tweet(self, min_chars=100, max_chars=140):
        seed = random.randint(0, len(self.words) - 3)
        w1, w2 = self.words[seed], self.words[seed + 1]
        tweet = '  '

        # loop until it's a sentence
        while tweet[-2] not in '.!?':
            tweet += (w1 + ' ')
            w1, w2 = w2, random.choice(self.word_cache[(w1, w2)])

        # if it's too short or too long, try again
        if len(tweet) < min_chars or len(tweet) > max_chars:
            tweet = self.generate_tweet()
        return tweet.strip()
#%%
def create_people():
    with open('people.txt','r') as people_file:
        people = [line for line in people_file]
    f = open('chat.txt','r')
    with open('result.txt','w') as out:
        out.write(f.readline())
    
    
    

#%%
def main():
    os.chdir('D:/Code/kubutz')
    with open('chat.txt') as f:
        text = [line for line in f]
    tweet = MarkovChain(text).generate_tweet()
    print(tweet)

if __name__ == '__main__':
    main()
