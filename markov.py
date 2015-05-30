from collections import defaultdict, deque
from itertools import chain, tee
from pprint import pprint
import random
import os,sys

class MarkovChainText(object):
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
        
        # Remove Media Ommited
        bad_words = ['<Media','omitted>']
        words = [w for w in words if w not in bad_words]
        return words

    def yield_trigrams(self):
        if len(self.words) < self.chain_length:
            return

        for i in range(len(self.words) - self.chain_length):
            yield_chain = [self.words[i+j] for j in range(self.chain_length)]
            yield (tuple(yield_chain[:-1]),yield_chain[-1])

    def wordbase(self):
        for w,wlast in self.yield_trigrams():
            self.word_cache[w].append(wlast)
        
    def generate_tweet(self, min_chars=10, max_chars=340):
        seed = random.randint(0, len(self.words) - self.chain_length)
        w = deque([self.words[seed+j] for j in range(self.chain_length - 1)])
        tweet = '  '
        
        # loop until it's a sentence
        while tweet[-2] not in '.!?':
            w.append(random.choice(self.word_cache[tuple(w)]))            
            tweet += (w.popleft() + ' ')

        # if it's too short or too long, try again
        if len(tweet) < min_chars or len(tweet) > max_chars:
            tweet = self.generate_tweet()
        return tweet.strip()
        
        #%%
class MarkovChainChat(object):
    def __init__(self, doc, people, **kwargs):
        self.chain_length = kwargs['num'] if 'num' in kwargs.keys() else 3
        self.speaker_cache = defaultdict(list)
        self.speaker_personal = defaultdict(list)
        self.gen_1 = self.yield_record(doc, people)
        self.gen_1, self.gen_2 = tee(self.gen_1)
        self.speakers = [r[1] for r in self.gen_1]
        self.speaker_personal_base = self.speaker_personal_base()        
        self.speakerbase = self.speakerbase()
        

    def yield_record(self, doc, people):
        '''Reads a chat line by line and creates a table in a shape of list
        of lists:
        |Date|Speaker|Content|
        Yields one record every iteration'''
        speakers = [line.strip() for line in people]
        record = None
        for line in doc:
            if any(name in line for name in speakers):
                if record:
                    yield (record)
                record = line.split(" - ",1)
                rec1, rec2 = record[1].split(": ",1)
                record = [record[0], rec1, rec2]
            elif record:
                record[2] += " {}".format(line)
            else:
                continue         

    def yield_trigrams(self):
        if len(self.speakers) < self.chain_length:
            return

        for i in range(len(self.speakers) - self.chain_length):
            yield_chain = [self.speakers[i+j] for j in range(self.chain_length)]
            yield (tuple(yield_chain[:-1]),yield_chain[-1])
            
    def speakerbase(self):
        for w,wlast in self.yield_trigrams():
            self.speaker_cache[w].append(wlast)
    
    def speaker_personal_base(self):
        for rec in self.gen_2:
            self.speaker_personal[rec[1]].append(rec[2])
            
    def generate_speak(self, chat_windows = 1):
        print self.speakers        
        print 'OK'
        speaker = random.choice(self.speakers)
        print speaker
        return "{}: {}".format(speaker,
            MarkovChainText(self.speaker_personal[speaker]).generate_tweet())
        
#%%
def main():
    os.chdir('D:/Code/kubutz')
    doc       = open('Chat.txt', 'r')
    people    = open('people.txt', 'r')
    chat = MarkovChainChat(doc, people, num = 3)
    with open ('tweet.txt','w') as outfile:
        outfile.write("{}\n\n".format(chat.generate_speak()))
    doc.close()
    people.close()

if __name__ == '__main__':
    main()
