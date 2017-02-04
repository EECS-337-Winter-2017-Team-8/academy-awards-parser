import operator
from random import randint

def get_tweets(filename):
    tweets = []
    with open(filename) as f:
        tweets = f.readlines()
    return [tweet.split('\t') for tweet in tweets]

def get_texts(tweets):
    return [tweet[0] for tweet in tweets]

def remove_retweets(texts):
    return [text for text in texts if "RT" not in text]

# # messy no work good function - please fix thanks
# def get_most_important_associations(texts, phrase_lengths):
#     scores = get_multi_phrase_scores(texts, phrase_lengths)
#     top_word_scores = sort_dict(scores)[-20:]
#     matches = {word_score[0]:
#                sort_dict(get_phrase_occurrences_in_common(texts, word_score[0], phrase_lengths))[-5:]
#                for word_score in top_word_scores}
#     return matches

def get_correlations(texts, phrase_lengths):
    phrase_occurances = get_multi_phrase_counts(texts, phrase_lengths)
    return {phrase[0]: sort_dict(
        remove_overlap(phrase[0],
                       get_conditional_probability(texts, phrase[0],
                                                   phrase_lengths)))[-2:]
            for phrase in sort_dict(phrase_occurances)[-20:]}


def build_phrases(texts, phrase, threshold = 0.2):
    build_phrase(texts, phrase, threshold)
    

def build_phrase(texts, phrase, threshold = 0.2):
    candidates = get_conditional_probability(texts, phrase,
                                             [len(get_word_list(phrase)) + 1])
    best = sort_dict(candidates)[randint(-3, -2)]
    if best[1] > threshold:
        return build_phrase(texts, best[0], threshold)
    else:
        return phrase

def get_conditional_probability(texts, phrase, phrase_lengths):
    candidate_counts = get_phrases_intersect_count(texts, phrase, phrase_lengths)
    phrase_count = 0
    for text in texts:
        if phrase in text:
            phrase_count += 1
    return {phrase_2: (float(dict_get(candidate_counts, phrase_2, 0)) /
                       phrase_count)
            for phrase_2 in candidate_counts}

def get_phrases_intersect_count(texts, phrase, phrase_lengths):
    phrase_texts = [text for text in texts if phrase in text]
    occurrences_in_common = get_multi_phrase_counts(phrase_texts,
                                                    phrase_lengths)
    return occurrences_in_common

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

def remove_overlap(phrase, phrase_scores):
    for key in phrase_scores:
        for word in get_word_list(phrase):
            if word in get_word_list(key):
                phrase_scores.update({key: 0})
    return phrase_scores

def dict_get(d, k, otherwise):
    if d.has_key(k):
        return d[k]
    else:
        return otherwise

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
