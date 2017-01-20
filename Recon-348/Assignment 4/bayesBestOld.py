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
    
   def classify(self, sText):
      """Given a target string sText, this function returns the most likely document
      class to which the target string belongs (i.e., positive, negative or neutral).
      """

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

##   def testTokenizer(self, number):
##      """ Tests the output of a tokenizer on the reviews. """
##      names = returnNames(REVIEW_DIR)
##      i = 0
##      for name in names:
##         i += 1
##         if i > number:
##            break
##         words = self.tokenize(self.loadFile(REVIEW_DIR + name))
##         print words

##   def stripTokens(self, tokens, removeList):
##      newList = []
##      for token in tokens:
##         if token not in removeList:
##            newList += [token]
##      return newList
         
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

##def stripTokens(tokens, pos):
##   """Given a list of pos-tagged tokens from nltk, strips the ones which match
##      any of the parts of speech passed in as a second list."""
##   result = []
##   for token in tokens:
##      if token[1] not in pos:
##         result += [token]
##   return result
         

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
