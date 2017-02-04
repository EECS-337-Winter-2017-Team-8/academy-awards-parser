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

def test_phrase_builder():
    phrase_builder = get_phrase_builder(ggtexts, "Best", threshold = 0.15)
    i = 0
    for phrase in phrase_builder:
        print(phrase)
        i += 1
        if i > 1000:
            break

used_phrases = []

def get_phrase_builder(texts, phrase, threshold = 0.15):
    global used_phrases
    candidates = get_probability_given(texts, phrase,
                                       [len(get_word_list(phrase)) + 1])
    best = sort_dict(candidates)
    best.reverse()
    for candidate in best:
        if candidate[1] > threshold:
            phrase_builder = get_phrase_builder(texts, candidate[0], threshold)
            for bigger_phrase in phrase_builder:
                yield bigger_phrase
    actual_content = phrase.split(':')[-1]
    if actual_content not in used_phrases:
        used_phrases.append(actual_content)
        print used_phrases
        yield actual_content


def get_probability_given(texts, phrase, phrase_lengths):
    intersect_counts = get_intersect_counts(texts, phrase, phrase_lengths)
    phrase_count = get_phrase_count(texts, phrase)
    return {phrase_2:
            (float(dict_try(intersect_counts, phrase_2, 0)) / phrase_count)
            for phrase_2 in intersect_counts}

def get_phrase_count(texts, phrase):
    phrase_count = 0
    for text in texts:
        if phrase in text:
            phrase_count += 1
    return phrase_count

def get_intersect_counts(texts, phrase, allowed_phrase_lengths):
    phrase_texts = [text for text in texts if phrase in text]
    occurrences_in_common = get_phrase_counts(phrase_texts,
                                              allowed_phrase_lengths)
    return occurrences_in_common

def get_phrase_counts(texts, allowed_phrase_lengths):
    phrase_counts = {}
    for phrase_length in allowed_phrase_lengths:
        for text in texts:
            for phrase in get_phrases(text, phrase_length):
                dict_increment(phrase_counts, phrase, 1)
    return phrase_counts

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

def dict_try(d, k, otherwise):
    if d.has_key(k):
        return d[k]
    else:
        return otherwise

def dict_increment(d, k, n):
    if d.has_key(k):
        temp = {k: d.pop(k) + n}
        d.update(temp)
    else:
        temp = {k: n}
        d.update(temp)

def sort_dict(freq_dict):
    sorted_freqs = sorted(freq_dict.items(), key=operator.itemgetter(1))
    return sorted_freqs


ggtexts = get_texts(get_tweets("goldenglobes.tab"))
