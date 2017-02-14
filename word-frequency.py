import operator
import random
import sentiment_analysis


def get_tweets(filename):
    tweets = []
    with open(filename) as f:
        tweets = f.readlines()
    return [tweet.split('\t') for tweet in tweets]

def get_texts(tweets):
    return [tweet[0] for tweet in tweets]

def remove_retweets(texts):
    return [text for text in texts if "RT" not in text]

def evaluate(texts, phrase, classifier, threshold = 0.20, number = 3):
    containing = get_containing(texts, phrase)
    count = classifier.count(containing)
    positive_count = count[0]
    neutral_count = count[1]
    negative_count = count[2]
    total_count = positive_count + negative_count
    positive_ratio = (float(positive_count) / total_count) * 100
    built_phrases = yank_phrases(number, texts, phrase, threshold)
    print("\nDuring the golden globes, people tweeted " + str(positive_count) + " positive things about " +
          "\"" + phrase + "\"" +
          " and " + str(negative_count) + " negative things, a ratio of " + str(positive_ratio) +
          " percent positive. People said a variety of things, but a lot of people made thematically" +
          " related comments like these (with a confidence threshold of " +
          str(threshold * 100) + " percent): " + "\n\n" + pretty_print(built_phrases))

def pretty_print(phrases):
    pretty = ""
    for phrase in phrases:
        pretty += (phrase + "\n\n")
    return pretty

def get_containing(texts, phrase):
    return [text for text in texts if phrase in text]

def yank_phrases(number, texts, phrase, threshold = 0.15):
    phrase_builder = get_unique_phrase_builder(texts, phrase, threshold)
    return [next(phrase_builder) for index in range(number)]

def get_unique_phrase_builder(texts, seed_phrase, threshold = 0.15):
    used_phrases = []
    while True:
        phrase_builder = get_phrase_builder(texts, seed_phrase, threshold)
        built_phrase = strip_retweet_header(next(phrase_builder))
        if built_phrase == seed_phrase:
            yield seed_phrase
        else:
            while built_phrase in used_phrases:
                phrase_builder = get_phrase_builder(texts, seed_phrase, threshold)
                built_phrase = strip_retweet_header(next(phrase_builder))
            used_phrases.append(built_phrase)
            yield built_phrase

def strip_retweet_header(phrase):
    words = get_word_list(phrase)
    clean_start_index = 0
    for index, word in enumerate(words):
        if word.strip() == 'RT':
            for i, w in enumerate(words[index:]):
                if w[-1] == ':':
                    clean_start_index = i
                    break
    clean_word_list = words[clean_start_index:]
    return " ".join(clean_word_list)

def get_phrase_builder(texts, phrase, threshold = 0.15, used_phrases = []):
    candidates = get_probability_given(texts, phrase,
                                       [len(get_word_list(phrase)) + 1])
    candidates = {candidate: candidates[candidate]
                  for candidate in candidates
                  if (candidates[candidate] > threshold and
                      strip_retweet_header(candidate) not in used_phrases and
                      strip_retweet_header(candidate) != phrase)}
    if candidates:
        yield next(get_phrase_builder(texts,
                                      choose_event(candidates),
                                      threshold, used_phrases))
    else:
        yield phrase

def choose_event(weights):
    sum = 0
    for event in weights:
        sum += weights[event]
    return choose_weighted({event: (weights[event] / sum)
                            for event in weights})

def choose_weighted(probabilities):
    # Probabilities must be normalized (i.e., sum to one)
    pointer = random.random()
    running_sum = 0
    for event in probabilities:
        running_sum += probabilities[event]
        if running_sum > pointer:
            return event


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
classifier = sentiment_analysis.Bayes_Classifier()
#classifier.train()

def tell_me_about(phrase, threshold = 0.20, number = 3):
    evaluate(ggtexts, phrase, classifier, threshold, number)
