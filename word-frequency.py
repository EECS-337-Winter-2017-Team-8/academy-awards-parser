import operator
import enchant
import nltk

# def associate_words(words, word_co_occurrence_dict):
#     words.sort()
#     for word in words:
#         if word_co_occurrence_dict.has_key(word):
#             word_co_occurrence_counts = word_co_occurrence_dict[word]
#         else:
#             word_co_occurrence_counts = {}
#         for co_occurring_word in words:
#             dictIncrement(word_co_occurrence_counts, co_occurring_word)
#         word_co_occurrence_dict[word] = word_co_occurrence_counts
#     return word_co_occurrence_dict

# def get_frequencies(filename):
#     parsed_tweets = tweets(filename)
#     words_lists = get_words(parsed_tweets)
#     wcod = {}
#     for words in words_lists:
#         wcod = associate_words(words, wcod)
#     return wcod

# def dictIncrement(d, k):
#    """ Increments the value stored for a key. """
#    if d.has_key(k):
#       temp = {k: d.pop(k) + 1}
#       d.update(temp)
#    else:
#       temp = {k: 1}
#       d.update(temp)

# def sort_dict(freq_dict):
#     sorted_freqs = sorted(freq_dict.items(), key=operator.itemgetter(1))
#     return sorted_freqs

# def get_single_word_associations(query_string, search_texts):
#     single_word_associations = {}
#     query_words = query_string.split(' ')
#     for text in search_texts:
#         if query_string in text:
#             for word in text.split(' '):
#                 if word not in query_words:
#                     dictIncrement(single_word_associations, word)
#     return single_word_associations

# def query(frequency_dict, query_string, search_texts):
#     if frequency_dict.has_key(query_string):
#         return frequency_dict[query_string]
#     temp = {query_string: get_single_word_associations(query_string, search_texts)}
#     frequency_dict.update(temp)
#     return frequency_dict

##########

def get_tweets(filename):
    tweets = []
    with open(filename) as f:
        tweets = f.readlines()
    return [tweet.split('\t') for tweet in tweets]

def get_texts(tweets):
    return [tweet[0] for tweet in tweets]

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
