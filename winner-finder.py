# ~~~~~~~~~~~~~~~~~~~~~~~~~~~IDE Set up ~~~~~~~~~~~~~~~~~~~~~~~~~~~
import nltk, string, os

def clear():
	print "\n"*62

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~Functions Set up ~~~~~~~~~~~~~~~~~~~~~~~~~~~

def keywords(filepath):
	# Function to load keywords in useful format
	keywords = []
	wordfile = open(filepath, "r")
	for line in wordfile:
		keywords.append(line)
	return keywords

def useful_filter(search_array, data, or_flag=True):
	# Function to filter over Data Corpus, selecting entries which
	# match verbatim with either/all elements of the search_array
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
		
def isQuotn(elt):
	return ((elt == "``") | (elt == "''") | (elt == "`") | (elt == "'") | (elt == "\""))

def correctParanthesis(token):
	#NLTK is a bit weird here
	if(token == "``"):
		return '"'
	elif(token == "''"):
		return '"'
	else:
		return token

def handle_name(tweet_segment, offset):
	#Call when you have found out where a name should begin:
	#i.e. after "Congratulations to "
	#Returns the name for formats: (1) Name; (2) Twitter Handle; (3) Name(@Twitter); (4) "Name": add'l info
	#TO BE PRINTED, MUST INCREMENT 1 TO END
	next_word = tweet_segment[0]
	start, end = None, None

	if (isQuotn (next_word)):
		start, end = 0, [tweet_segment.index(token) for token in tweet_segment[1:] if isQuotn(token)][0]
		#end is set to index of closing quot'n marks

	elif (next_word == "@"):
		start, end = 0,1

	elif (next_word[0].isupper()):
		start, end = 0,0
		while(tweet_segment[end+1][0].isupper() & (tweet_segment[end+1].lower()!="for")):
			end+=1
	if(end!=None):
		if tweet_segment[end+1]=="(":
			end = end+1+tweet_segment[end+1:].index(")")
		elif tweet_segment[end+1]==":":
			end = end+1+tweet_segment[end+2:].index("-") #Hard-coded.......
	# print "internal answer is", tweet_segment[start:end+1] 
	try:
		return start+offset, end+offset
	except:
		return None, None

def printResults(inp_word_list, tweet, st, end):
	tweet_start = tweet.index(inp_word_list[st])
	tweet_end = tweet_start + 1+ tweet[tweet_start+1:].index(inp_word_list[end]) +len(inp_word_list[end])
	result = tweet[tweet_start:tweet_end]
	return result

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Code ~~~~~~~~~~~~~~~~~~~~~~~~~~~		

GG_tweet_id = "18667907"

keywords = keywords("keywords.txt")
congrats_words = ["Congratulations", "congratulations", "congrats"]
win_words = ["wins", "won", "winning", "winner"]

tweets = list(open("goldenglobes.tab","r"))

GG_tweets = useful_filter([GG_tweet_id], tweets)

awards = useful_filter(["congratulations"], GG_tweets)

host_GG_tweets = useful_filter(["host"], GG_tweets)
presenter_GG_tweets = useful_filter(["present"], GG_tweets)

def tweet_comprehension(tweet):
	word_list = nltk.word_tokenize(tweet)
	lower_word_list = map(str.lower, word_list)
	congrats_index, win_index, win_word = None, None, None
	w_st, w_end = 0,0

	for i in range(0, len(congrats_words)):
		if congrats_words[i] in word_list:
			congrats_index = word_list.index(congrats_words[i])

	for i in range(0, len(win_words)):
		if win_words[i] in lower_word_list:
			win_index = lower_word_list.index(win_words[i])
			win_word = win_words[i]

	if((win_index!=None) and (congrats_index!=None)):
		if(win_index < congrats_index):
			if(win_word == "winner"):
				increment = 1
				while((lower_word_list[win_index+increment] == "is") | (lower_word_list[win_index+increment] == "...")):
					increment+=1
				w_st, w_end = handle_name(word_list[win_index+increment:], win_index+increment)
				return printResults( map(correctParanthesis, word_list), tweet, w_st, w_end)

		elif(congrats_index < win_index):
			if(lower_word_list[congrats_index+1] == "to"):
				# print "calling from to"
				w_st, w_end = handle_name(word_list[congrats_index+2:], congrats_index+2)
				return printResults( map(correctParanthesis, word_list), tweet, w_st, w_end)
			elif(word_list[congrats_index+1] == ","):	
				w_st, w_end = handle_name(word_list[congrats_index+2:], congrats_index+2)
				return printResults( map(correctParanthesis, word_list), tweet, w_st, w_end)
			else:
				print "Neither to nor comma"

	elif(congrats_index!=None):
		if(lower_word_list[congrats_index+1] == "to"):
			# print "calling from to"
			w_st, w_end = handle_name(word_list[congrats_index+2:], congrats_index+2)
			return printResults( map(correctParanthesis, word_list), tweet, w_st, w_end)
		elif(word_list[congrats_index+1] == ","):	
			w_st, w_end = handle_name(word_list[congrats_index+2:], congrats_index+2)
			return printResults( map(correctParanthesis, word_list), tweet, w_st, w_end)
		else:
			print "Neither to nor comma"
	elif (win_index!=None):
			print "tbd"

def runTests():
	for i in awards:
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		print i
		a = tweet_comprehension(i)		
		print "winner is: ", a
		



















