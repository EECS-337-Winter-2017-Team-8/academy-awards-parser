# Name: 
# Date:
# Description:
#
#

import math, os, pickle, re, string, nltk
from nltk import *
from nltk.stem import *
from nltk.stem.porter import *

class Bayes_Classifier:

   def __init__(self):
      """This method initializes and trains the Naive Bayes Sentiment Classifier.  If a 
      cache of a trained classifier has been stored, it loads this cache.  Otherwise, 
      the system will proceed through training.  After running this method, the classifier 
      is ready to classify input text."""
      # Tunable Parameters
      self.word_types_to_cull = ["''", "(", ")", ",", "--", ".", ":",
                                 "CC", "IN",
                                 "SYM", "TO", "WDT", "WP", "WP$", "WRB", "``"]
      # Attempt to load the training data for the classifier
      try:
         self.goodDict = self.load("goodDictBest.dict")
         self.badDict = self.load("badDictBest.dict")
         featureNums = self.load("featureNumsBest.dict")
         self.numGoodFeatures = featureNums.get('good')
         self.numBadFeatures = featureNums.get('bad')
      # Re-train the classifier if the data can't be loaded
      except:
         self.goodDict = {}
         self.badDict = {}
         self.numGoodFeatures = 0
         self.numBadFeatures = 0
         self.train()

   def tokenizeAndStrip(self, sText):
      try:
         tokens = word_tokenize(sText)
         tokens = nltk.pos_tag(tokens)
         tokens = stripPOS(tokens, self.word_types_to_cull)
         lowercase = []
         for token in tokens:
            lowercase += [token[0].lower()]
         tokens = lowercase
         stemmer = PorterStemmer()
         stems = []
         for token in tokens:
            stems.append(stemmer.stem(token))
         tokens = stems
      except:
         tokens = []
      return tokens

   def loadAndStrip(self, name):
      tokens = self.tokenizeAndStrip(self.loadFile(REVIEW_DIR + name))
      return tokens

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
         tokens = self.loadAndStrip(name)
         if name.split('-')[1] == '1':
            # is a bad review
            for token in tokens:
               dictIncrement(self.badDict, token)
               realTimeSmooth(self.goodDict, token)
         elif name.split('-')[1] == '5':
            # is a good review
            for token in tokens:
               dictIncrement(self.goodDict, token)
               realTimeSmooth(self.badDict, token)
      self.numGoodFeatures = sum(self.goodDict.values())
      self.numBadFeatures = sum(self.badDict.values())
      self.save(self.goodDict, "goodDictBest.dict")
      self.save(self.badDict, "badDictBest.dict")
      featureNums = {'good': self.numGoodFeatures, 'bad': self.numBadFeatures}
      self.save(featureNums, "featureNumsBest.dict")      

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
         
   def classify(self, sText):
      """Given a target string sText, this function returns the most likely
         document class to which the target string belongs (i.e., positive,
         negative or neutral)."""
      # Tunable Parameters
      cutoff = 1
      
      # Tokenize and Clean the Input
      tokens = self.tokenizeAndStrip(sText)
      # Initialize Counter Variables
      prob_pos = 0
      prob_neg = 0
      for token in tokens:
         num_good = self.goodDict.get(token)
         num_bad = self.badDict.get(token)
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

def stripPOS(tokens, pos):
   """Given a list of pos-tagged tokens from nltk, strips the ones which match
      any of the parts of speech passed in as a second list."""
   result = []
   for token in tokens:
      if token[1] not in pos:
         result += [token]
   return result
         

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

def calcGroupStats(names, classifications):
   """ Given a set of names and classifications, returns stats in
       the format (Accuracy, Precision, Recall, F1) """

   # Initialize Counting Statistics
   num_total = 0
   num_correct_pos = 0
   num_correct_neg = 0
   num_incorrect_pos = 0
   num_incorrect_neg = 0
   num_actual_pos = 0
   num_actual_neg = 0

   for name in names:
      num_total += 1
      classification = classifications.get(name)
      if name.split('-')[1] == '1':
         num_actual_neg += 1
         if classification == "negative":
            num_correct_neg += 1
         elif classification == "positive":
            num_incorrect_pos += 1
      elif name.split('-')[1] == '5':
         num_actual_pos += 1
         if classification == "positive":
            num_correct_pos += 1
         elif classification == "negative":
            num_incorrect_neg += 1
   num_classified_pos = num_correct_pos + num_incorrect_pos
   num_classified_neg = num_correct_neg + num_incorrect_neg
   num_correct_total = num_correct_pos + num_correct_neg

   # Calculate per-class statistics
   # Accurate, but not robust for small data sets or really bad classifiers
   precision_pos = float(num_correct_pos) / num_classified_pos
   precision_neg = float(num_correct_neg) / num_classified_neg
   recall_pos = float(num_correct_pos) / num_actual_pos
   recall_neg = float(num_correct_neg) / num_actual_neg
   f1_pos = (2 * precision_pos * recall_pos) / (precision_pos + recall_pos)
   f1_neg = (2 * precision_neg * recall_neg) / (precision_neg + recall_neg)
   
   # Calculate net statistics using macroaveraging
   accuracy = float(num_correct_total) / num_total
   precision = (precision_pos + precision_neg) / 2
   recall = (recall_pos + recall_neg) / 2
   f1 = (f1_pos + f1_neg) / 2

   return (accuracy, precision, recall, f1)


def calcStats(classifier, data):
   names = returnNames(data)

   # Sort names of reviews into positive and negative lists
   neg_reviews = []
   pos_reviews = []
   for name in names:
      if name.split('-')[1] == '1':
         neg_reviews += [name]
      elif name.split('-')[1] == '5':
         pos_reviews += [name]

   # Apportion roughly one-tenth of the positive list and one-tenth of the
   # negative list into each bucket (discards up to ten items from end,
   # truncating after the highest included multiple of ten for simplicity)
   buckets = []
   pos_chunk_size = len(pos_reviews) / 10
   neg_chunk_size = len(neg_reviews) / 10
   start = 0
   for end in range(1, 11):
      buckets += [pos_reviews[pos_chunk_size * start:pos_chunk_size * end] +
                  neg_reviews[neg_chunk_size * start:neg_chunk_size * end]]
      start = end

   stats = [0, 0, 0, 0]
   
   # For each bucket
   for i in range(0, 10):
      print i
      # Calculate the training data and testing data for the bucket
      trainData = []
      testData = []
      for j in range(0, 10):
         if i == j:
            testData = buckets[j]
         else:
            trainData += buckets[j]
      # Train the classifier on the training data
      classifier.train(trainData)
      # Classify the test data using the classifier
      classifications = classifier.classifyAll(testData)
      # Calculate the stats for this group
      groupStats = [calcGroupStats(testData, classifications)]
      # Add the stats into a lump sum
      for j in range(0, 4):
         stats[j] += groupStats[0][j]

   # Divide the stats by ten to get the average
   for i in range(0, 4):
      stats[i] /= 10

   return stats
      
REVIEW_DIR = "movies_reviews/"
myBayes = Bayes_Classifier()
print calcStats(myBayes, REVIEW_DIR)
myBayes.train()
