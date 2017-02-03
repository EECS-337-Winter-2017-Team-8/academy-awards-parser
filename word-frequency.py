import operator

def tweets(filename):
    tweets = []
    with open(filename) as f:
        tweets = f.readlines()
    return [tweet.split('\t') for tweet in tweets]

def get_text(tweets):
    return [tweet[0] for tweet in tweets]

def get_words(tweets):
    return [text.split(' ') for text in get_text(tweets)]

def associate_words(words, word_co_occurrence_dict):
    words.sort()
    for word in words:
        if word_co_occurrence_dict.has_key(word):
            word_co_occurrence_counts = word_co_occurrence_dict[word]
        else:
            word_co_occurrence_counts = {}
        for co_occurring_word in words:
            dictIncrement(word_co_occurrence_counts, co_occurring_word)
        word_co_occurrence_dict[word] = word_co_occurrence_counts
    return word_co_occurrence_dict

def get_frequencies(filename):
    parsed_tweets = tweets(filename)
    words_lists = get_words(parsed_tweets)
    wcod = {}
    for words in words_lists:
        wcod = associate_words(words, wcod)
    return wcod

def dictIncrement(d, k):
   """ Increments the value stored for a key. """
   if d.has_key(k):
      temp = {k: d.pop(k) + 1}
      d.update(temp)
   else:
      temp = {k: 2}
      d.update(temp)

def sort_dict(freq_dict):
    sorted_freqs = sorted(freq_dict.items(), key=operator.itemgetter(1))
    return sorted_freqs

def query(dict, string, texts):
    for text in texts:
        if text in text:
