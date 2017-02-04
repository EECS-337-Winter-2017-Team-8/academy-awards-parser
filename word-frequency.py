import operator
import enchant
import nltk

def get_tweets(filename):
    tweets = []
    with open(filename) as f:
        tweets = f.readlines()
    return [tweet.split('\t') for tweet in tweets]

def get_texts(tweets):
    return [tweet[0] for tweet in tweets]

## bad function - no use without fix
def get_phrase_correllation(texts, phrase, phrase_scores, phrase_lengths):
    phrase_texts = [text for text in texts if phrase in text]
    phrase_scores_given_phrase = get_multi_phrase_scores(phrase_texts,
                                                         phrase_lengths)
    return {other_phrase:
            (float(dict_get(phrase_scores_given_phrase, other_phrase)) /
             dict_get(phrase_scores, other_phrase))
            for other_phrase in phrase_scores}

def get_phrase_occurances_in_common(texts, phrase_1, phrase_2):


def get_multi_phrase_scores(texts, phrase_lengths):
    phrase_scores = {}
    for phrase_length in phrase_lengths:
        phrase_scores.update(get_phrase_scores(texts, phrase_length))
    return phrase_scores

def get_phrase_scores(texts, phrase_length):
    phrase_scores = {}
    for text in texts:
        for phrase in get_phrases(text, phrase_length):
            dict_add(phrase_scores, phrase, phrase_length)
    return phrase_scores

def get_multi_phrase_counts(texts, phrase_lengths):
    phrase_counts = {}
    for phrase_length in phrase_lengths:
        phrase_counts.update(get_phrase_counts(texts, phrase_length))
    return phrase_counts

def get_phrase_counts(texts, phrase_length):
    phrase_counts = {}
    for text in texts:
        for phrase in get_phrases(text, phrase_length):
            dict_increment(phrase_counts, phrase)
    return phrase_counts

def get_phrase_associations(query_string, search_texts, phrase_length):
    phrase_associations = {}
    for search_text in search_texts:
        if query_string in search_text:
            for phrase in get_phrases(search_text, phrase_length):
                dict_increment(phrase_associations, phrase)
    return phrase_associations

def get_word_list(text):
    return text.split(' ')

def get_phrases(text, phrase_length):
    word_list = get_word_list(text)
    end_index = len(word_list) - phrase_length
    return [' '.join(word_list[index : index + phrase_length])
            for index in range(end_index)]

def dict_get(d, k):
    if d.has_key(k):
        return d[k]
    else:
        return 1

def dict_add(d, k, n):
    if d.has_key(k):
        temp = {k: d.pop(k) + n}
        d.update(temp)
    else:
        temp = {k: n}
        d.update(temp)

def dict_increment(d, k):
   if d.has_key(k):
      temp = {k: d.pop(k) + 1}
      d.update(temp)
   else:
      temp = {k: 1}
      d.update(temp)

def sort_dict(freq_dict):
    sorted_freqs = sorted(freq_dict.items(), key=operator.itemgetter(1))
    return sorted_freqs


ggtexts = get_texts(get_tweets("goldenglobes.tab"))
