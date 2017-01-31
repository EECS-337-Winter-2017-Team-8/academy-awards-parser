# Name: 
# Date:
# Description:
#
#

import math, os, pickle, re, string, nltk

class Bayes_Classifier:

   def __init__(self):
      """This method initializes and trains the Naive Bayes Sentiment Classifier.  If a 
      cache of a trained classifier has been stored, it loads this cache.  Otherwise, 
      the system will proceed through training.  After running this method, the classifier 
      is ready to classify input text."""
      try:
         self.goodDict = self.load("goodDict.dict")
         self.badDict = self.load("badDict.dict")
         featureNums = self.load("featureNums.dict")
         self.numGoodFeatures = featureNums.get('good')
         self.numBadFeatures = featureNums.get('bad')
      except:
         self.goodDict = {}
         self.badDict = {}
         self.numGoodFeatures = 0
         self.numBadFeatures = 0
         self.train()

   def train(self, data = None):   
      """Trains the Naive Bayes Sentiment Classifier. Optionally takes
         a list of data, but if none is provided, scrapes data from
         the location provided in the global variable REVIEW_DIR."""
      self.goodDict = {}
      self.badDict = {}
      if data == None:
         names = returnNames(REVIEW_DIR)
      else:
         names = data
      for name in names:
         words = self.tokenize(self.loadFile(REVIEW_DIR + name))
         if name.split('-')[1] == '1':
            # is a bad review
            for word in words:
               dictIncrement(self.badDict, word)
               realTimeSmooth(self.goodDict, word)
         elif name.split('-')[1] == '5':
            # is a good review
            for word in words:
               dictIncrement(self.goodDict, word)
               realTimeSmooth(self.badDict, word)
      self.numGoodFeatures = sum(self.goodDict.values())
      self.numBadFeatures = sum(self.badDict.values())
      self.save(self.goodDict, "goodDict.dict")
      self.save(self.badDict, "badDict.dict")
      featureNums = {'good': self.numGoodFeatures, 'bad': self.numBadFeatures}
      self.save(featureNums, "featureNums.dict")
    
   def loadFile(self, sFilename):
      """Given a file name, return the contents of the file as a string."""
      f = open(sFilename, "r")
      sTxt = f.read()
      f.close()
      return sTxt

   def save(self, dObj, sFilename):
      """Given an object and a file name, write the object to the file using pickle."""
      f = open(sFilename, "w")
      p = pickle.Pickler(f)
      p.dump(dObj)
      f.close()

   def load(self, sFilename):
      """Given a file name, load and return the object stored in the file."""
      f = open(sFilename, "r")
      u = pickle.Unpickler(f)
      dObj = u.load()
      f.close()
      return dObj

   def tokenize(self, sText): 
      """Given a string of text sText, returns a list of the individual tokens that
      occur in that string (in order)."""
      lTokens = []
      sToken = ""
      for c in sText:
         if re.match("[a-zA-Z0-9]", str(c)) != None or c == "\"" or c == "_" or c == "-":
            sToken += c
         else:
            if sToken != "":
               for mark in string.punctuation:
                  sToken = sToken.strip(mark)
               lTokens.append(sToken.lower())
               sToken = ""
            if c.strip() != "":
               lTokens.append(str(c.strip()))
      if sToken != "":
         for mark in string.punctuation:
            sToken = sToken.strip(mark)
         lTokens.append(sToken.lower())
      return lTokens

   def classify(self, sText):
      cutoff = 1
      words = self.tokenize(sText)
      prob_pos = 0
      prob_neg = 0
      for word in words:
         num_good = self.goodDict.get(word)
         num_bad = self.badDict.get(word)
         if num_good == None:
            prob_word_if_pos = float(1) / self.numGoodFeatures
         else:
            prob_word_if_pos = float(num_good) / self.numGoodFeatures
         if num_bad == None:
            prob_word_if_neg = float(1) / self.numBadFeatures
         else:
            prob_word_if_neg = float(num_bad) / self.numBadFeatures
         prob_pos += math.log(prob_word_if_pos, 2)
         prob_neg += math.log(prob_word_if_neg, 2)
      if prob_pos * cutoff >= prob_neg:
         return "positive"
      elif prob_neg * cutoff >= prob_pos:
         return "negative"
      else:
         return "neutral"

   def classifyAll(self, names):
      """ Classifies all the reviews passed in as names """
      classifications = {}
      for name in names:
         classification = self.classify(self.loadFile(REVIEW_DIR + name))
         temp = {name: classification}
         classifications.update(temp)
      return classifications

   def count(self, list_of_strings):
      pos_score = 0
      neutral_score = 0
      neg_score = 0
      for string in list_of_strings:
         classification = self.classify(string)
         if classification == "positive":
            pos_score += 1
         elif classification == "negative":
            neg_score += 1
         else:
            neutral_score += 1
      return (pos_score, neutral_score, neg_score)

def dictIncrement(d, k):
   """ Increments the value stored for a key. """
   if d.has_key(k):
      temp = {k: d.pop(k) + 1}
      d.update(temp)
   else:
      temp = {k: 2}
      d.update(temp)

def realTimeSmooth(d, k):
   """ Conducts add-one smoothing. """
   if not d.has_key(k):
      temp = {k: 1}
      d.update(temp)

def returnNames(scanDir):
   IFileList = []
   for fFileObj in os.walk(scanDir):
      IFileList = fFileObj[2]
      break
   return IFileList

REVIEW_DIR="movies_reviews/"
myBayes = Bayes_Classifier()
# Only run .train() when starting the system for the first time.
# On subsequent runs it uses saved data to avoid long training
# times.
myBayes.train()
my_strings_about_topic = []
myBayes.count(my_strings_about_topic)
