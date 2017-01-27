import nltk

def keywords(filepath):
	keywords = []
	wordfile = open(filepath, "r")
	for line in wordfile:
		keywords.append(line)
	return keywords

def useful_filter(search_array, data, or_flag=True):
	matchingLines = []
	while(search_array):
		search_elt = search_array.pop()
		elt_matchingLines = filter (lambda (line):
			(search_elt.lower() in line.lower()), data)
		if(or_flag):
			matchingLines = list(set(elt_matchingLines+matchingLines))
		else:
			matchingLines = list(set(elt_matchingLines) & set(matchingLines))
	return matchingLines
		

GG_tweet_id = "18667907"

keywords = keywords("keywords.txt")

tweets = list(open("goldenglobes.tab","r"))

GG_tweets = useful_filter([GG_tweet_id], tweets)

awards = useful_filter(["congratulations"], GG_tweets)

host_GG_tweets = useful_filter(["host"], GG_tweets)
presenter_GG_tweets = useful_filter(["present"], GG_tweets)

for tweet in awards:
	word_list = nltk.word_tokenize(tweet)
	for i in range(0, word_list):
		if word_list[i] == "Congratulations":
			if (word_list[i+1]=="to" || word_list[i+1] in string.punctuation.replace("@","")):
				winner_start_index = word_list[i] + 2

	
