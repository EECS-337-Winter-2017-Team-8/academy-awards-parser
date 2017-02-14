# ~~~~~~~~~~~~~~~~~~~~~~~~~~~IDE Set up ~~~~~~~~~~~~~~~~~~~~~~~~~~~
import nltk, string, os

#OmarIDESetUpStuff: Ignore please
# execfile('../Desktop/Code/nlp-eecs337/winner-finder.py')
# os.chdir('../Desktop/Code/nlp-eecs337')

def clear():
	print "\n"*62

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~		

GG_tweet_id = "18667907"  					#@goldenglobes
TheAcademy_tweet_id = "200163448"			#@theacademy
Oscars_Live_id = "1088416026" 				#@oscars_live

congrats_words = ["congratulations", "congrats"]
win_words = ["wins", "won", "winning", "winner"]
nom_words = ["nominee", "nominated"]
pres_words = ["presenter", "presented", "presenting"]
venue_words = ["red", "carpet"]
award_show_names = ["golden", "globes", "goldenglobes", "#goldenglobes", "oscars", "#oscars", "academy", "#theacademy", "#academyawards", "academyawards", "awards"]

adjectives = ["adapted", "animated", "best", "feature", "lead", "leading", "made", "motion", "original",  "short", "starring", "supporting", "visual"]
genres = ["action", "adventure", "comedy", "drama", "foreign", "independent", "musical", "suspense", "thriller"]
grammar = [",", "(", ")", "a", "and", "by", "for", "in", "or", "&", "with", ":"] #added with
media = ["play", "series", "show", "television", "tv"]
subjects = ["actor", "achievement", "actress", "cinematography", "costume", "design", "directing", "director", "documentary", "editing", "effects", "film",  "hair", 
			"hairstyling", "hair-styling", "makeup", "miniseries", "mini", "mixing", "movie", "music", "performance", "picture", "production", "role","screenplay", 
			"score", "script", "series","song", "sound", "writing"]
extra = ["language", "subject"]
iswasare = ["is", "was", "are"]
whowhichthat = ["who", "which", "that"]
pronouns = ["i", "he", "she", "me", "them", "it", "who", "whom", "they", "and"]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Misc Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~

def number_filter(search_array, data, or_flag=True):
	#takes strings
	matchingLines = []
	if(or_flag):
		for line in data:
			for elt in search_array:
				if (elt.isdigit()):
					if elt in line:
						# print linep
						matchingLines.append(line)
					else:
						continue
				else:
					continue
	else:
		for line in data:
			matchFlag = True
			for elt in search_array:
				if (elt.isdigit()):
					if not(elt in line):
						matchFlag = False
						break
			if(matchFlag == True):
				matchingLines.append(line)
	return matchingLines

def word_filter(search_array, data, or_flag=True):
	# Function to filter over Data Corpus, selecting entries which
	# match verbatim with either/all elements of the search_array
	#		Using nltk.word_tokenize(line) slows performance so much.
	#What if we use split
	search_array = map(str.lower, search_array)
	matchingLines = []
	if(or_flag):
		matchingLines = filter (lambda (line):
			(set(search_array).intersection(line.lower().split(" "))), data)
	else:
		matchingLines = filter (lambda (line):
			(len(set(search_array).intersection(line.lower().split(" "))) == len(search_array)), data)
	return matchingLines
		
def consecutive_words_filter (search_array, data):
	#Returns all the lines who match the search_array in consecutive order.
	search_array = map(str.lower, search_array)
	matchingLines = []
	for line in data:
		append = True
		line_words = line.lower().split(' ')
		if search_array[0] in line_words:
			initial_index = line_words.index(search_array[0])
			for i in range(len(search_array) - 1):
				if (line_words[initial_index+1+i]!=search_array[i+1]):
					append = False
					break
		else: 
			append = False
		if(append):
			matchingLines.append(line)
	return matchingLines

def multiple_consecutive_words_filter(search_arrays, data):
	#Returns all the lines that match any of the search_arrays in consecutive order.
	matchingLines = []
	for search_array in search_arrays:
		matchingLines+=consecutive_words_filter(search_array, data)
	return list(set(matchingLines))

def user_filter(search_users, data):
	ret = []
	for i in data:
		try:
			user in search_users
			if i.split('\t')[1]==user:
				ret.append(i)
		except:
			continue
	return ret

def cutRT(tweet_word_list):
	if (tweet_word_list[0:2]==["RT", "@"]):
		return tweet_word_list[4:]
	return tweet_word_list

def isQuotn(elt):
	return ((elt == "``") | (elt == "''") | (elt == "`") | (elt == "'") | (elt == "\""))

def complete_remove(token, arr):
	return [elt for elt in arr if(elt!=token)]

def correctParanthesis(token):
	#NLTK is a bit weird here
	if(token == "``"):
		return '"'
	elif(token == "''"):
		return '"'
	else:
		return token

def correctAmpersands(tweet):
	if "&amp;" in tweet:
		return tweet.replace("&amp;","&")
	return tweet

def match_nominee_award(nominees, tweet):
	word_list = nltk.word_tokenize(tweet)
	lower_word_list = map(str.lower, word_list)

	for i in range(0, len(nominees)):
		if(tweet.find(nominees[i])!=-1):
			return nominees[i]

	return None

def notEveryWordIsCaps(inp_word_list):
	for word in inp_word_list:
		if(word[0].isalpha() and not(word[0].isupper())):
			return True
	return False

def isLowerAnd(word):
	return word == "and" or word == "&"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Handle Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~

def handle_name_fwd(tweet_segment, offset, tweetIsNotAllCaps=False):
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

	elif (next_word[0].isupper() and tweetIsNotAllCaps):
		start, end = 0,0
		while( ( len(tweet_segment) > (end+1)) and (tweet_segment[end+1][0].isupper()) and(tweet_segment[end+1].lower()!="for")):
			# print "this is:", tweet_segment[end+1]
			end+=1
	if((end!=None) and (end!=(len(tweet_segment)-1))):
		if (tweet_segment[end+1]=="("):
			try:
				end = end+1+tweet_segment[end+1:].index(")")
			except:
				pass
		elif (tweet_segment[end+1]==":"):
			try:
				end = end+1+tweet_segment[end+2:].index("-")
			except:
				pass
	# print "internal answer is", tweet_segment[start:end+1] 
	try:
		return start+offset, end+offset
	except:
		return None, None

def handle_name_bwd(tweet_segment, offset, tweetIsNotAllCaps=False):
	#ex: ['Dev', 'Patel', 'and', 'Sunny', 'Pawar', 'introduce', '@', 'LionMovie']
	#end must refer to the LAST INDEX that holds an important val, such that tweet_segment_rv[end] is the last part we need.
	tweet_segment_rv = tweet_segment[::-1]
	next_word = tweet_segment_rv[0]
	bwd_start, bwd_end = None, None

	if (isQuotn (next_word)):
		if(next_word == "'"):
			for i in range(len(tweet_segment_rv[1:])):
				if(isQuotn(tweet_segment_rv[i][0])):
					bwd_end = i+1
					bwd_start = 0
					break
		else:
			bwd_start, bwd_end = 0, [tweet_segment_rv.index(token) for token in tweet_segment_rv[1:] if isQuotn(token)][0]
	elif (next_word == ")"):
		bwd_start, bwd_end = 0, [tweet_segment_rv.index(token) for token in tweet_segment_rv[1:] if (token=="(")][0]
		if(tweetIsNotAllCaps):
			while( (len(tweet_segment_rv)>(bwd_end+2)) and (tweet_segment_rv[bwd_end+1][0].isupper())):
				bwd_end+=1
	elif ((len(tweet_segment_rv)>=2) and (tweet_segment_rv[1] == "@")):
		bwd_start, bwd_end = 0, 1
	elif (next_word[0].isupper() and tweetIsNotAllCaps): #and notEveryWordIsCaps(tweet_segment)):
		bwd_start, bwd_end = 0,0
		while( (len(tweet_segment_rv)>(bwd_end+1)) and(tweet_segment_rv[bwd_end+1][0].isupper())):
			bwd_end+=1

	if((bwd_start==None) or (bwd_end==None)):
		return None, None
	else:
		if( (bwd_end<(len(tweet_segment_rv)-1) ) and (tweet_segment_rv[bwd_end+1]=="#")):
			bwd_end+=1
		start = offset-bwd_end
		end = offset
		return start, end
	return None, None

def handle_subject(tweet_segment, offset):	
	end, length = 0, len(tweet_segment)

	next_word, after_next_word = None, None
	if(length>=3):
		next_word, after_next_word = tweet_segment[1], tweet_segment[2] #The 2 words AFTER subject
	elif(length>=2):
		next_word = tweet_segment[1]
	
	if(next_word in subjects):
		#SUBJECT+SUBJECT
		w_st, w_end = handle_genre(tweet_segment[2:],offset+2)
		return offset, w_end

	elif(next_word in grammar):
		if ((isLowerAnd(next_word)) & (after_next_word in subjects)):
			#SUBJECT + AND + SUBJECT
			w_st, w_end = handle_genre(tweet_segment[3:],offset+3)
			return offset, w_end
		elif ((next_word == "in") and (after_next_word == "a") and (length>=5)):
			next_word, after_next_word = tweet_segment[3], tweet_segment[4]
			if((next_word in adjectives)&(after_next_word in subjects)):
				#SUBJECT + IN + A + ADJECTIVE + SUBJECT
				w_st, w_end = handle_genre(tweet_segment[5:], 5)
				return offset, w_end+offset
			elif((next_word in media)&(after_next_word in subjects)):
				if(length>=7):
					next_word, after_next_word = tweet_segment[5], tweet_segment[6]
					if((next_word == "or") & (after_next_word in subjects)):
						#SUBJECT + IN + A + MEDIA + SUBJECT + OR + SUBJECT
						return offset, 7+offset
					else:
						w_st, w_end = handle_genre(tweet_segment[5:], 5)
						return offset, w_end+offset
				else:
					start_g, end_g = handle_genre(tweet_segment[5:], 5)
				return offset, end_g+offset
			elif((next_word in genres)):
				if(after_next_word in subjects):
					return offset, offset+5
				else:
					return offset, offset+4
			else:
				return offset, offset+5
		elif ((next_word == "or") & (after_next_word in adjectives) & (length>=5)):
			next_word, after_next_word = tweet_segment[3], tweet_segment[4]
			if((next_word in subjects) & (after_next_word in adjectives) & (length>=7)):
				next_word, after_next_word = tweet_segment[5], tweet_segment[6]
				if((next_word =="for") & (after_next_word in media)):
					w_st, w_end = handle_genre(tweet_segment[7:],offset+7)
					return offset, w_end
		elif ((next_word == "by") & ((after_next_word == "a")|(after_next_word == "an")) & (length>=5)):
			next_word, after_next_word = tweet_segment[3], tweet_segment[4]
			if(next_word in subjects):
				if((after_next_word == "in") & (length>=7)):
					next_word, after_next_word = tweet_segment[5], tweet_segment[6]
					if((next_word =="a")|(next_word=="an")):
						if(after_next_word in subjects):
							w_st, w_end = handle_genre(tweet_segment[7:],offset+7)
							return offset, w_end
						elif(((after_next_word in adjectives) | (after_next_word in media))&(length>=8)):
							next_word = tweet_segment[7]
							if(next_word in subjects):
								w_st, w_end = handle_genre(tweet_segment[8:],offset+8)
								return offset, w_end
						else: return offset, offset
					elif((next_word in subjects)|(next_word in media)):
						if((after_next_word == ",") | (after_next_word == "or") & (length>=8)):
							iterator = 7
							while( (tweet_segment[iterator]==",")|(tweet_segment[iterator]=="or")|(tweet_segment[iterator] in media)|(tweet_segment[iterator] in subjects)):
								iterator+=1
							w_st, w_end = handle_genre(tweet_segment[iterator:],offset+iterator)
							return offset, w_end
						w_st, w_end = handle_genre(tweet_segment[6:],offset+6)
						return 
					elif(next_word in genres):
						if(after_next_word in subjects):
							return offset, offset+7
						else:
							return offset, offset+6
				else: return offset, offset					
			else: return offset, offset
		elif ((next_word == "(")):
			if(after_next_word in adjectives):
				if(length>=5):
					next_word, after_next_word = tweet_segment[3], tweet_segment[4]
					if( ((next_word in subjects) | (next_word in extra)) & (after_next_word == ")")):
						w_st, w_end = handle_genre(tweet_segment[5:],offset+5)
						return offset, w_end
						# return start + offset, end + offset + 5
					if(next_word == ")"):
						w_st, w_end = handle_genre(tweet_segment[4:],offset+4)
						return offset, w_end
						# return start + offset, end + offset + 4
				elif(length>=4):
					next_word = tweet_segment[3]
					if (next_word == ")"):
						w_st, w_end = handle_genre(tweet_segment[4:],offset+4)
						return offset, w_end
						# return start + offset, end + offset + 4
			else:
				iterator=3
				while(tweet_segment[iterator]!=")"):
					iterator+=1
				w_st, w_end = handle_genre(tweet_segment[iterator+1:],offset+iterator+1)
				return offset, w_end

		else:
			w_st, w_end = handle_genre(tweet_segment[1:],offset+1)
			return offset, w_end	
	elif ((next_word == "-") & (length>=5)):
		if(after_next_word in genres):
			w_st, w_end = handle_genre(tweet_segment[1:],offset+1)	
			return offset, w_end
		elif(after_next_word in subjects):
			next_word, after_next_word = tweet_segment[3], tweet_segment[4]
			if(next_word == "or"):
				if (after_next_word in media):
					next_word = tweet_segment[5]
					if(next_word in subjects):
						w_st, w_end = handle_genre(tweet_segment[6:],offset+6)
						return offset, w_end
					else:
						return offset, offset+6
				elif (after_next_word in subjects):
					w_st, w_end = handle_genre(tweet_segment[5:],offset+5)
					return offset, w_end
		else:
			return offset, offset+1
	else:
		w_st, w_end = handle_genre(tweet_segment[1:],offset+1)
		return offset, w_end

def handle_genre(tweet_segment, offset):
	length = len(tweet_segment)
	next_word = tweet_segment[0]
	if(next_word == "-"):
		if(length>=4):
			second_word, third_word, fourth_word = tweet_segment[1], tweet_segment[2], tweet_segment[3]
			if(second_word in genres):
				if((third_word == "or")|(third_word == "language")):
					if(fourth_word in genres):
						return offset, 4+offset
				return offset, 2+offset
			else:
				return offset, offset
		elif(length>=2):
			second_word = tweet_segment[1]
			if(second_word in genres):
				return offset, 2+offset
	elif((next_word in genres) & (length>=2)):
		next_word = tweet_segment[1]
		if(next_word in adjectives):
			w_st, w_end = handle_genre(tweet_segment[3:],offset+3)
			return offset, w_end
			# return offset, offset+3
		elif((next_word == "language") & (length>=3)):
			next_word = tweet_segment[2]
			if(next_word in subjects):
				w_st, w_end = handle_genre(tweet_segment[3:],offset+3)
				return offset, w_end
				# return offset, offset+3
		elif(next_word in subjects):
			w_st, w_end = handle_genre(tweet_segment[2:],offset+2)
			return offset, w_end
		elif((next_word in grammar) & (length>=4)):
			if(next_word == "or"):
				after_next_word = tweet_segment[2]
				if(after_next_word in genres):
					return offset, 3+offset 
				else:
					return offset, 1+offset
			else:
				return offset, offset+1
		else:
			return None, None
	elif((length>=3) & (next_word == "language") & (tweet_segment[2] in subjects)):
		if((length>=5) & (tweet_segment[3] == "-" ) & (tweet_segment[4] in genres)):
			w_st, w_end = handle_genre(tweet_segment[3:], 4)
			return offset, w_end+offset
		else:
			return offset, 3+offset
	else:
		return offset, offset

def handle_adjective(tweet_segment, offset):
	length = len(tweet_segment)
	if(length>=2):
		if(tweet_segment[1] in subjects): #If we have Adjective + Subject ->
			if(length>=4):
				if(tweet_segment[2] == "-"):
					if (tweet_segment[3] in adjectives):
						return offset, + 5+offset
					else:
						g_st, g_end = handle_genre(tweet_segment[2:], 2)
						return 0, g_end+offset
				elif((tweet_segment[2] == "in") & (tweet_segment[3] == "a")):
					if (length>=6):
						if((tweet_segment[4] in media) & (tweet_segment[5] in subjects)):
							if(length>=8):
								if((tweet_segment[6] == ",")&(tweet_segment[7] in subjects)&(length>=10)):
									if((tweet_segment[8] == "or")&(tweet_segment[9] in subjects)):
										return offset, offset + 10
									elif((length>=11) & (tweet_segment[8] == ",")& (tweet_segment[9] in "or") & (tweet_segment[10] in subjects)):
										return offset, offset + 11
									else:
										return offset, offset + 8
								else:
									return offset, offset+ 6
							else:
								return offset, offset+ 6
						elif((tweet_segment[4] in adjectives) & (tweet_segment[5] in subjects)):
							return offset, offset+ 6
						else:
							return offset, offset+ 5
					else:
						return offset, offset+5
				elif(tweet_segment[2] in genres):
					w_st, w_end = handle_genre(tweet_segment[2:], offset+2)
					return offset, w_end
				else:
					return offset, 2+offset
			else:
				#Adjective + Subject
				return offset, 2+offset
		
		elif((length>=3)&(tweet_segment[1] in adjectives) & (tweet_segment[2] in subjects)):
			w_st, w_end = handle_genre(tweet_segment[3:], offset+3)
			return offset, w_end
		# next_word, after_next_word = tweet_segment[1], tweet_segment[2] #The 2 words AFTER subject
	else:
		g_st, g_end = handle_genre(tweet_segment[2:], 2)
		return offset, g_end+offset

def handle_media(tweet_segment, offset):
	length = len(tweet_segment)
	if((length>=2) & (tweet_segment[1] in subjects)):
		if(length>=4):
			if (tweet_segment[2] in subjects):
				w_st, w_end = handle_genre(tweet_segment[3:], 3+offset)
				return 0, w_end
			elif (tweet_segment[2] == "-"):
				w_st, w_end = handle_genre(tweet_segment[2:], 2+offset)
				return 0, w_end
			elif (tweet_segment[2] in grammar):
				if(tweet_segment[2] == "or"):
					if(tweet_segment[3] in subjects):
						w_st, w_end = handle_genre(tweet_segment[4:], 4+offset)
						return 0, w_end
	return 0,0

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Print ~~~~~~~~~~~~~~~~~~~~~~~~~~~

def printResults(inp_word_list, tweet, st, end):
	if((st == None) or (end == None)):
		return None
	if(st==end):
		return inp_word_list[st]
	start_word = inp_word_list[st]
	if(tweet.count(start_word)>1):
		number_of_preceding_copies = inp_word_list[:st].count(start_word)
		new_tweet = tweet
		if(number_of_preceding_copies != 0):
			for i in range(number_of_preceding_copies):
				new_tweet = new_tweet[new_tweet.index(start_word) + len(start_word):]
		tweet_start = new_tweet.index(inp_word_list[st])
		tweet_end = tweet_start + 1+ new_tweet[tweet_start+1:].index(inp_word_list[end]) +len(inp_word_list[end])
		result = new_tweet[tweet_start:tweet_end]
	else:
		tweet_start = tweet.index(inp_word_list[st])
		tweet_end = tweet_start + 1+ tweet[tweet_start+1:].index(inp_word_list[end]) +len(inp_word_list[end])
		result = tweet[tweet_start:tweet_end]
	return result

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Code ~~~~~~~~~~~~~~~~~~~~~~~~~~~		

def get_award(tweet):
	tweet_body = correctAmpersands(tweet).split("\t")[0]

	word_list = nltk.word_tokenize(tweet_body)
	concise_word_list = cutRT(word_list)
	lower_word_list = map(str.lower, concise_word_list)

	best_index = None
	if("best" in lower_word_list):
		best_indices = [i for i, x in enumerate(lower_word_list) if x == "best"]
		for best_index in best_indices:
			next_word = lower_word_list[best_index+1]
			if(next_word in subjects):
				w_st, w_end = handle_subject(lower_word_list[best_index+1:],best_index+1) #Input is tweet cut AFTER best  
			elif(next_word in adjectives):
				w_st, w_end = handle_adjective(lower_word_list[best_index+1:],best_index+1)
			elif(next_word in media):
				w_st, w_end = handle_media(lower_word_list[best_index+1:],best_index+1)
			elif(next_word in genres):
				w_st, w_end = handle_genre(lower_word_list[best_index+1:],best_index+1)
			else:
				w_st, w_end = None, None

			if(w_end):
				return printResults(map(correctParanthesis, concise_word_list), tweet_body, best_index, w_end-1)
			else:
				continue
	return None

def get_winner(tweet):
	tweet_body = correctAmpersands(tweet).split("\t")[0]
	word_list = nltk.word_tokenize(tweet_body)
	concise_word_list = cutRT(word_list)
	isNotAllCaps = notEveryWordIsCaps(concise_word_list)

	lower_word_list = map(str.lower, concise_word_list)
	congrats_index, win_index, win_word = None, None, None
	w_st, w_end = 0,0

	for i in range(0, len(congrats_words)):
		if congrats_words[i] in lower_word_list:
			congrats_index = lower_word_list.index(congrats_words[i])

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
				w_st, w_end = handle_name_fwd(concise_word_list[win_index+increment:], win_index+increment, isNotAllCaps)
				return printResults( map(correctParanthesis, concise_word_list), tweet_body, w_st, w_end)

		elif(congrats_index < win_index):
			if(lower_word_list[congrats_index+1] == "to"):
				# print "calling from to"
				w_st, w_end = handle_name_fwd(concise_word_list[congrats_index+2:], congrats_index+2, isNotAllCaps)
				# print "w_st: ", w_st, "; w_end: ", w_end
				# print "word_list[w_st:w_end] = ", word_list[w_st:w_end]
				return printResults( map(correctParanthesis, concise_word_list), tweet_body, w_st, w_end)
			elif(concise_word_list[congrats_index+1] == ","):	
				w_st, w_end = handle_name_fwd(concise_word_list[congrats_index+2:], congrats_index+2, isNotAllCaps)
				return printResults( map(correctParanthesis, concise_word_list), tweet_body, w_st, w_end)
			else:
				print "Neither to nor comma"

	elif(congrats_index!=None):
		if(lower_word_list[congrats_index+1] == "to"):
			# print "calling from to"
			w_st, w_end = handle_name_fwd(concise_word_list[congrats_index+2:], congrats_index+2, isNotAllCaps)
			# print "w_st: ", w_st, "; w_end: ", w_end
			# print "word_list[w_st:w_end] = ", word_list[w_st:w_end]
			return printResults( map(correctParanthesis, concise_word_list), tweet_body, w_st, w_end)
		elif(concise_word_list[congrats_index+1] == ","):	
			w_st, w_end = handle_name_fwd(concise_word_list[congrats_index+2:], congrats_index+2, isNotAllCaps)
			return printResults( map(correctParanthesis, concise_word_list), tweet_body, w_st, w_end)
		else:
			print "Neither to nor comma"
	
	elif (win_index!=None):
		if(win_word == "winner"):
			increment = 1
			while((lower_word_list[win_index+increment] == "is") | (lower_word_list[win_index+increment] == "...")):
				increment+=1
			w_st, w_end = handle_name_fwd(concise_word_list[win_index+increment:], win_index+increment, isNotAllCaps)
			return printResults( map(correctParanthesis, concise_word_list), tweet_body, w_st, w_end)

def get_nominee(tweet):
	tweet_body = correctAmpersands(tweet).split("\t")[0]

	word_list = nltk.word_tokenize(tweet_body)
	concise_word_list = cutRT(word_list)
	lower_word_list = map(str.lower, concise_word_list)

	if(tweet[0:4]=="RT @"):
		concise_tweet_body = tweet[tweet.index(":")+1:]
	else:
		concise_tweet_body = tweet_body.replace("&amp;", "&")
	# if(concise_word_list[0]=="@" and tweet[0:4]=="RT @"):
	# 	concise_tweet_body = tweet_body[tweet_body[4:].index(correctParanthesis(concise_word_list[0]))+4:]
	# else:
	# 	concise_tweet_body = tweet_body[tweet_body.index(correctParanthesis(concise_word_list[0])):]

	isNotAllCaps = notEveryWordIsCaps(concise_word_list)

	nom_index, nom_word = None, None
	n_st, n_end = 0,0

	for i in range(0, len(nom_words)):
		if nom_words[i] in lower_word_list:
			nom_index = lower_word_list.index(nom_words[i])
			nom_word = nom_words[i]

	if(nom_index!=None):
		if(nom_word == "nominee"):
			increment = 1
			if(len(lower_word_list) > (nom_index+increment)):
				if((lower_word_list[nom_index+increment] == ",") | (lower_word_list[nom_index+increment] == ":")):
					increment += 1
					n_st, n_end = handle_name_fwd(concise_word_list[nom_index+increment:], nom_index+increment, isNotAllCaps)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, n_st, n_end)
				elif( (lower_word_list[nom_index+increment] not in grammar) & (lower_word_list[nom_index+increment]!="#") & (lower_word_list[nom_index+increment]!="is")) :
					n_st, n_end = handle_name_fwd(concise_word_list[nom_index+increment:], nom_index+increment, isNotAllCaps)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, n_st, n_end)
			return None
		elif(nom_word == "nominated"):
			if(nom_index >= 1):
				if(lower_word_list[nom_index-1] in iswasare):
					if(nom_index>=2):
						if(lower_word_list[nom_index-2] in whowhichthat):
							if((nom_index>=3)&(lower_word_list[nom_index-3] == ",")):		#Name begins.. call handle_name_bwd with lower_word_list[:nom_index-3] so it has everything until that index
								n_st, n_end = handle_name_bwd(concise_word_list[:nom_index-3], nom_index-4, isNotAllCaps)
								return printResults(map(correctParanthesis, concise_word_list), concise_tweet_body, n_st, n_end)
							else:
								return None
						elif((lower_word_list[nom_index-2] not in pronouns)&(lower_word_list[nom_index-2] != ",")): 		#Name begins.. call handle_name_bwd with lower_word_list[:nom_index-2] so it has everything until that index
							n_st, n_end = handle_name_bwd(concise_word_list[:nom_index-1], nom_index-2, isNotAllCaps)
							if(n_st!=None and n_end!=None):
								if(lower_word_list[n_st-1]=="from"):
									n2_st, n2_end = handle_name_bwd(concise_word_list[:n_st-1], n_st-2, isNotAllCaps)
									return printResults(map(correctParanthesis, concise_word_list), concise_tweet_body, n2_st, n_end)	
								return printResults(map(correctParanthesis, concise_word_list), concise_tweet_body, n_st, n_end)
							else: return None
						else:
							return None
				elif(lower_word_list[nom_index-1]== ","):
					n_st, n_end = handle_name_bwd(concise_word_list[:nom_index-1], nom_index-2, isNotAllCaps)
					return printResults(map(correctParanthesis, concise_word_list), concise_tweet_body, n_st, n_end)	
	return None

def get_presenter(tweet):
	tweet_body = correctAmpersands(tweet).split("\t")[0]
	word_list = nltk.word_tokenize(tweet_body)
	concise_word_list = cutRT(word_list)
	lower_word_list = map(str.lower, concise_word_list)
	
	if(tweet[0:4]=="RT @"):
		concise_tweet_body = tweet_body.replace("&amp;","&")[tweet.index(":")+1:]
	else:
		concise_tweet_body = tweet_body.replace("&amp;","&")
		
	isNotAllCaps = notEveryWordIsCaps(concise_word_list)

	pres_index, pres_word = None, None
	p_st, p_end = 0,0

	for i in range(0, len(pres_words)):
		if pres_words[i] in lower_word_list:
			pres_index = lower_word_list.index(pres_words[i])
			pres_word = pres_words[i]

	if(pres_index!=None):
		if(pres_word == "presenter"):
			if(pres_index!=0 and (lower_word_list[pres_index-1] == "best") and ( len(lower_word_list)>(pres_index+2) )):
					if( (lower_word_list[pres_index+1] in iswasare) or (lower_word_list[pres_index+1] == "for") or (lower_word_list[pres_index+1] == "=")):
						p_st, p_end = handle_name_fwd(concise_word_list[pres_index+2:], pres_index+2, isNotAllCaps)
						if((p_st!=None) and (p_end != None)):
							if(len(concise_word_list)>p_end+1):
								if (isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
									p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
									if(p_st_2!=None and p_end_2!=None):
										return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
							return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
					elif( len(lower_word_list)>(pres_index+3) and (lower_word_list[pres_index+1] == "goes") and (lower_word_list[pres_index+2] == "to")):
						p_st, p_end = handle_name_fwd(concise_word_list[pres_index+3:], pres_index+3, isNotAllCaps)
						if((p_st!=None) and (p_end != None)):
							if(len(concise_word_list)>p_end+1):
								if ( isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
									p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
									if(p_st_2!=None and p_end_2!=None):
										return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
							return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
						else:
							return None
					elif( len(lower_word_list)>(pres_index+4) and (lower_word_list[pres_index+1] == "award")):
						if (((lower_word_list[pres_index+2] == "goes") and (lower_word_list[pres_index+3] == "to")) or ((lower_word_list[pres_index+2] == "is") and (lower_word_list[pres_index+3] == "for"))):
							p_st, p_end = handle_name_fwd(concise_word_list[pres_index+4:], pres_index+4, isNotAllCaps)
							if((p_st!=None) and (p_end != None)):
								if(len(concise_word_list)>p_end+1):
									if (isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
										p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
										if(p_st_2!=None and p_end_2!=None):
											return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
							else:
								return None
						elif (lower_word_list[pres_index+2] == "="):
							p_st, p_end = handle_name_fwd(concise_word_list[pres_index+3:], pres_index+3, isNotAllCaps)
							if((p_st!=None) and (p_end != None)):
								if(len(concise_word_list)>p_end+1):
									if (isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
										p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
										if(p_st_2!=None and p_end_2!=None):
											return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
							else:
								return None
					else:
						return None
			elif((not (lower_word_list[pres_index+1] in grammar)) and (concise_word_list[pres_index+1][0].isupper() or (concise_word_list[pres_index+1][0]=="@"))):
				p_st, p_end = handle_name_fwd(concise_word_list[pres_index+1:], pres_index+1, isNotAllCaps)
				if((p_st!=None) and (p_end != None)):
					if(len(concise_word_list)>p_end+1):
						if (isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
							p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
							if(p_st_2!=None and p_end_2!=None):
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
				else:
					return None
			return None
		elif(pres_word == "presented"):
			if( (len(lower_word_list) > pres_index+2) and (lower_word_list[pres_index+1]=="by")):
				p_st, p_end = handle_name_fwd(concise_word_list[pres_index+2:], pres_index+2, isNotAllCaps)
				if((p_st!=None) and (p_end != None)):
					if(len(lower_word_list)>(p_end+1)):
						if (isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
							p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
							if(p_st_2!=None and p_end_2!=None):
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif( (len(lower_word_list) > pres_index+4) and (lower_word_list[pres_index+1]=="to")):
				if((lower_word_list[pres_index+2] in pronouns) and (lower_word_list[pres_index+3]=="by")):
					p_st, p_end = handle_name_fwd(concise_word_list[pres_index+4:], pres_index+4, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(len(lower_word_list)>(p_end+1)):
							if (isLowerAnd(lower_word_list[p_end+1]) or (lower_word_list[p_end+1] == "with") or (lower_word_list[p_end+1] == "alongside")):
								p_st_2, p_end_2 = handle_name_fwd(concise_word_list[p_end+2:], p_end+2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end_2)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
				elif( (pres_index>=1) and (concise_word_list[pres_index-1][0].isupper()) and (not (lower_word_list[pres_index-1] in pronouns))):
					p_st, p_end = handle_name_bwd(concise_word_list[:pres_index], pres_index-1, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(pres_index>(p_end+1)):
							if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
								p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif( (pres_index>=2) and (lower_word_list[pres_index-1] == "just")):
				if(lower_word_list[pres_index-2] in pronouns):
					return None
				else:
					p_st, p_end = handle_name_bwd(concise_word_list[:pres_index-1], pres_index-2, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(pres_index>(p_end+1)):
							if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
								p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif((pres_index>=1) and (concise_word_list[pres_index-1][0].isupper())):
				if(lower_word_list[pres_index-1] in pronouns):
					return None
				else:
					p_st, p_end = handle_name_bwd(concise_word_list[:pres_index], pres_index-1, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(pres_index>(p_end+1)):
							if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
								p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif(pres_index>=12 and (lower_word_list[pres_index-2]=="@")):
				p_st, p_end = handle_name_bwd(concise_word_list[:pres_index], pres_index-1, isNotAllCaps)
				if((p_st!=None) and (p_end != None)):
					if(pres_index>(p_end+1)):
						if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
							p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
							if(p_st_2!=None and p_end_2!=None):
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			return None
		elif(pres_word == "presenting"):
			if ((pres_index>=1) and (concise_word_list[pres_index-1][0].isupper()) and (not (lower_word_list[pres_index-1] in grammar)) and (not (lower_word_list[pres_index-1] in pronouns))):
				p_st, p_end = handle_name_bwd(concise_word_list[:pres_index], pres_index-1, isNotAllCaps)
				if((p_st!=None) and (p_end != None)):
					if(p_st>=1):
						if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
							p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
							if(p_st_2!=None and p_end_2!=None):
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif ((pres_index>=2) and (lower_word_list[pres_index-2]=="@")):
				p_st, p_end = handle_name_bwd(concise_word_list[:pres_index], pres_index-1, isNotAllCaps)
				if((p_st!=None) and (p_end != None)):
					if(p_st>=1):
						if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
							p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
							if(p_st_2!=None and p_end_2!=None):
								return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
					return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif (pres_index>=2) and (lower_word_list[pres_index-1] in iswasare):
				if (not (lower_word_list[pres_index-2] in pronouns)):
					p_st, p_end = handle_name_bwd(concise_word_list[:pres_index-1], pres_index-2, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(p_st>=1):
							if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
								p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
				elif (lower_word_list[pres_index-2] in whowhichthat):
					p_st, p_end = handle_name_bwd(concise_word_list[:pres_index-2], pres_index-3, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(p_st>=1):
							if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
								p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
			elif ((pres_index>=2) and (((lower_word_list[pres_index-1] == "now") and (lower_word_list[pres_index-2] == "is")) or ((lower_word_list[pres_index-1] == "be") and (lower_word_list[pres_index-2] == "will")))):
				if(pres_index>=3) and (not (lower_word_list[pres_index-3] in pronouns)):
					p_st, p_end = handle_name_bwd(concise_word_list[:pres_index-2], pres_index-3, isNotAllCaps)
					if((p_st!=None) and (p_end != None)):
						if(p_st>=1):
							if (isLowerAnd(lower_word_list[p_st-1]) or (lower_word_list[p_st-1] == "with") or (lower_word_list[p_st-1] == "alongside")):
								p_st_2, p_end_2 = handle_name_bwd(concise_word_list[:p_st-1], p_st-2, isNotAllCaps)
								if(p_st_2!=None and p_end_2!=None):
									return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st_2, p_end)
						return printResults( map(correctParanthesis, concise_word_list), concise_tweet_body, p_st, p_end)
				return None
			return None
	return None

def get_venue(tweet):
	tweet_body = correctAmpersands(tweet).split("\t")[0]
	word_list = nltk.word_tokenize(tweet_body)
	concise_word_list = cutRT(word_list)
	lower_word_list = map(str.lower, concise_word_list)
	
	if(tweet[0:4]=="RT @"):
		concise_tweet_body = tweet_body.replace("&amp;","&")[tweet.index(":")+1:]
	else:
		concise_tweet_body = tweet_body.replace("&amp;","&")
		
	isNotAllCaps = notEveryWordIsCaps(concise_word_list)

	red_index, ceremony_index = None, None
	v_st, v_end, increment = 0, 0, 0

	for i in lower_word_list:
		if(i == "red"):
			red_index = lower_word_list.index(i)
			increment = 1
		elif(i in award_show_names):
			ceremony_index = lower_word_list.index(i)
			increment = 1
	
	if((red_index == None) and (ceremony_index == None)):
		return None

	listLen = len(lower_word_list)

	if((red_index!=None) and (red_index+increment < listLen)):
		if(lower_word_list[red_index+increment]=="carpet"):
			carpet_index = red_index+increment
			increment += 1
			if(red_index+increment < listLen):
				if((lower_word_list[red_index+increment] == "@") or (lower_word_list[red_index+increment] == "at")):
					at_index, at_token = red_index+increment, lower_word_list[red_index+increment]
					increment += 1
					at_tweet_index = tweet_body.find(at_token)
					if(tweet_body[at_tweet_index+1]!=" "):
						return None
					elif(lower_word_list[red_index+increment] in award_show_names):
						return None
					elif(lower_word_list[red_index+increment] == "the"):
						the_index = red_index+increment
						increment += 1
						if(lower_word_list[red_index+increment] in award_show_names):
							return None
						elif((lower_word_list[red_index+increment] == "@") or (lower_word_list[red_index+increment] == "#")):
							increment += 1
							if(lower_word_list[red_index+increment] in award_show_names):
								return None
							else:
								v_st, v_end = handle_name_fwd(concise_word_list[red_index+increment:], red_index+increment, isNotAllCaps)
								return printResults( map(correctParanthesis, concise_word_list), tweet_body, v_st, v_end)
						else:
							v_st, v_end = handle_name_fwd(concise_word_list[red_index+increment:], red_index+increment, isNotAllCaps)
							return printResults( map(correctParanthesis, concise_word_list), tweet_body, v_st, v_end)
					elif(lower_word_list[red_index+increment] == "@" or "#"):
						if(lower_word_list[red_index+increment] in award_show_names):
							return None
						else:				
							v_st, v_end = handle_name_fwd(concise_word_list[red_index+increment:], red_index+increment, isNotAllCaps)
							return printResults( map(correctParanthesis, concise_word_list), tweet_body, v_st, v_end)
	elif((ceremony_index!=None)) and (ceremony_index+increment < listLen):
		if((lower_word_list[ceremony_index+increment] == "@") or (lower_word_list[ceremony_index+increment] == "at")):
			at_index, at_token = ceremony_index+increment, lower_word_list[ceremony_index+increment]
			increment += 1
			at_tweet_index = tweet_body.find(at_token)
			if(tweet_body[at_tweet_index+1]!=" "):
				return None
			elif(lower_word_list[ceremony_index+increment] in award_show_names):
				return None
			elif(lower_word_list[ceremony_index+increment] == "the"):
				the_index = ceremony_index+increment
				increment += 1
				if(lower_word_list[ceremony_index+increment] in award_show_names):
					return None
				elif((lower_word_list[ceremony_index+increment] == "@") or (lower_word_list[ceremony_index+increment] == "#")):
					increment += 1
					if(lower_word_list[ceremony_index+increment] in award_show_names):
						return None
					else:
						v_st, v_end = handle_name_fwd(concise_word_list[ceremony_index+increment:], ceremony_index+increment, isNotAllCaps)
						return printResults( map(correctParanthesis, concise_word_list), tweet_body, v_st, v_end)
				else:
					v_st, v_end = handle_name_fwd(concise_word_list[ceremony_index+increment:], ceremony_index+increment, isNotAllCaps)
					return printResults( map(correctParanthesis, concise_word_list), tweet_body, v_st, v_end)
			elif(lower_word_list[ceremony_index+increment] == "@" or "#"):
				if(lower_word_list[ceremony_index+increment] in award_show_names):
					return None
				else:				
					v_st, v_end = handle_name_fwd(concise_word_list[ceremony_index+increment:], ceremony_index+increment, isNotAllCaps)
					return printResults( map(correctParanthesis, concise_word_list), tweet_body, v_st, v_end)
	return None


def get_host():
	word_file = open("wordsEn.txt", "r")
	en_words = set([word.strip().lower() for word in word_file])
	host = []
	host_tweets = word_filter(["host", "hosts", "hosting", "hosted"], inp_tweets)
	host_tweets = " ".join(host_tweets)
	host_tweets_words = [word.lower() for word in nltk.regexp_tokenize(host_tweets, pattern="\w[a-z]+")]

	word_list = []
	stop_words = nltk.corpus.stopwords.words("english")
	stop_words.extend(["globe", "golden", "goldenglobe", "goldenglobes", "oscar", "oscars", "http", "https", "rt"])

	for word in host_tweets_words:
		if word not in stop_words and word not in en_words:
			word_list.append(word)

	fdist = nltk.FreqDist(word_list)
	# for word in fdist.most_common(50):
	# 	print word

	for word in fdist.most_common(2):
		host.append(word[0])

	if host[0] in host[1]:
		host = [host[1]]
	elif host[1] in host[0]:
		host = [host[0]]

	word_file.close()

	return host

#~~~~~~~~~~~~~~~~~~~~~~~~~~~ User Interface ~~~~~~~~~~~~~~~~~~~~~~~~~~~

tweets = list(open("goldenglobes.tab","r"))

def extract_Awards_Info(event_name, inp_tweets):
	lower_event_name = event_name.lower()
	if("golden globe" in lower_event_name):
		GG_tweets = number_filter([GG_tweet_id], inp_tweets)
		awards_tweets = word_filter(congrats_words, GG_tweets)
		pairings = []
		for i in awards_tweets:
			award = get_award(i)
			# print "award won is: ", award
			# print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			pairings.append(award)
		return pairings
	elif (("academy awards" in lower_event_name) | ("oscars" in lower_event_name)):
		Combined_tweets = number_filter([TheAcademy_tweet_id, Oscars_Live_id], inp_tweets)
		awards_tweets = word_filter(congrats_words, GG_tweets)
		pairings = []
		for i in awards_tweets:
			award = get_award(i)
			# print "award won is: ", award
			# print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			pairings.append(award)
		return pairings
	else:
		return "Unable; check event_name and inp_tweets"

def extract_Winners_Info(event_name, inp_tweets):
	lower_event_name = event_name.lower()
	if("golden globe" in lower_event_name):
		GG_tweets = number_filter([GG_tweet_id], inp_tweets)
		awards_tweets = word_filter(congrats_words, GG_tweets)
		# nom_tweets = word_filter(nom_words, inp_tweets)
		nom_tweets = word_filter(["nominee"], inp_tweets)
		venue_tweets = word_filter(venue_words, inp_tweets)
		pairings = []
		# for i in awards_tweets:
		# 	winner, award = get_winner(i), get_award(i)
		# 	print "winner is: ", winner
		# 	print "award won is: ", award
		# 	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		# 	pairings.append((winner, award))
		nominees = []
		for i in nom_tweets:
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			print "i is : ", i
			nominee, award = get_nominee(i), get_award(i)
			if(nominee!=None):
				nominees.append(str.lower(nominee))
				print "nominee is: ", nominee
			elif((nominee==None) and (award!=None)):
				nominee = match_nominee_award(nominees,i)
			if((nominee!=None) and (award!=None)):
				print nominee, " is nominated for ", award
				pairings.append( (nominee, award) )
		return pairings
	elif (("academy awards" in lower_event_name) | ("oscars" in lower_event_name)):
		Combined_tweets = number_filter([TheAcademy_tweet_id, Oscars_Live_id], inp_tweets)
		awards_tweets = word_filter(congrats_words, GG_tweets)
		pairings = []
		for i in awards_tweets:
			winner, award = get_winner(i), get_award(i)
			# print "winner is: ", winner
			# print "award won is: ", award
			# print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			pairings.append( (winner, award) )
		return pairings

def extract_Nominees_Info(event_name, inp_tweets):
	lower_event_name = event_name.lower()
	if("golden globe" in lower_event_name):
		n_tweets = word_filter(nom_words, inp_tweets)
		pairings = []
		for i in n_tweets:
			nominee = get_nominee(i)
			if(nominee!=None):
				try:
					award = get_award(i)
				except:
					award = None
				# print "nominee is: ", nominee
				# print "award won is: ", award
				# print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
				pairings.append( (nominee, award))
		return pairings
	elif (("academy awards" in lower_event_name) | ("oscars" in lower_event_name)):
		n_tweets =  word_filter(nom_words, inp_tweets)
		pairings = []
		for i in n_tweets:
			nominee = get_nominee(i)
			if(nominee!=None):
				try:
					award = get_award(i)
				except:
					award = None
				# print "nominee is: ", nominee
				# print "award won is: ", award
				# print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
				pairings.append( (nominee, award))
		return pairings

def extract_Host_Info(event_name, inp_tweets):
	hosts = get_host(inp_tweets)
	# if len(hosts) == 1:
	# 	print "Host is " + hosts[0] + "."
	# else:
	# 	print "Hosts are " + hosts[0] + " and " + hosts[1] + "."
	return hosts

def extract_Venue_Info(event_name, inp_tweets):
	lower_event_name = event_name.lower()
	venue_tweets = word_filter(venue_words, inp_tweets)
	pairings = []
	for i in venue_tweets:
		venue = get_venue
		if(venue!=None):
			pairings.append(venue)
			# print "The venue is: ", venue
			# print i
			# print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	return pairings

def extract_Info_With_Venue(event_name, inp_tweets):
	lower_event_name = event_name.lower()
	if("golden globe" in lower_event_name):
		GG_tweets = number_filter([GG_tweet_id], inp_tweets)
		awards_tweets = word_filter(congrats_words, GG_tweets)
		# nom_tweets = word_filter(nom_words, inp_tweets)
		# nom_tweets = word_filter(["nominee"], inp_tweets)
		venue_tweets = word_filter(venue_words, inp_tweets)
		venue_tweets += word_filter(award_show_names, inp_tweets)
		pairings = []
		# for i in awards_tweets:
		# 	winner, award = get_winner(i), get_award(i)
		# 	print "winner is: ", winner
		# 	print "award won is: ", award
		# 	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		# 	pairings.append((winner, award))
		# nominees = []
		# for i in nom_tweets:
		# 	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		# 	print "i is : ", i
		# 	nominee, award = get_nominee(i), get_award(i)
		# 	if(nominee!=None):
		# 		nominees.append(str.lower(nominee))
		# 		print "nominee is: ", nominee
		# 	elif((nominee==None) and (award!=None)):
		# 		nominee = match_nominee_award(nominees,i)
		# 	if((nominee!=None) and (award!=None)):
		# 		print nominee, " is nominated for ", award
		# 		pairings.append( (nominee, award) )
		venueList = []
		for i in venue_tweets:
			venue = get_venue(i)
			if(venue!=None):
				print i
				print "The venue is: ", venue
				print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
				venueList.append(venue)

		venueListCount = {}
		for i in venueList:
			if(i not in venueListCount):
				venueListCount[i] = 1
			elif(i in venueListCount):
				venueListCount[i] += 1

		mostCommonVenueCount = 0
		mostCommonVenue = None
		for i in venueListCount.keys():
			if(venueListCount[i] > mostCommonVenueCount):
				mostCommonVenueCount = venueListCount[i]
				mostCommonVenue = i

		print "The list of possible venues is: ", venueList
		print "The most common venue is: ", mostCommonVenue
		return mostCommonVenue
	elif (("academy awards" in lower_event_name) | ("oscars" in lower_event_name)):
		Combined_tweets = number_filter([TheAcademy_tweet_id, Oscars_Live_id], inp_tweets)
		awards_tweets = word_filter(congrats_words, GG_tweets)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Demo ~~~~~~~~~~~~~~~~~~~~~~~~~~~

def run_Names_Tests():
	GG_tweets = number_filter([GG_tweet_id], tweets)
	awards_tweets = word_filter(congrats_words, GG_tweets)
	for i in extensive_awards_tweets:
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		print i
		a = get_winner(i)		
		print "winner is: ", a
		
def run_Awards_Tests():
	GG_tweets = number_filter([GG_tweet_id], tweets)
	awards_tweets = word_filter(congrats_words, GG_tweets)
	for i in extensive_awards_tweets:
		try:
			a = get_award(i)
			print a
		except:
			print "FAILED:", i
			continue

def run_Nom_Tests():
	n_tweets = word_filter(nom_words, tweets)
	for tweet in n_tweets[:50]:
		try:
			nominee = get_nominee(tweet)
			print "tweet is: ", tweet
			print "nominee is: ", nominee
		except:
			print "FAILED:", tweet
			print "~~~~~~~~~~~~~~~~~~~~~~~~"
			continue

def run_Pres_Tests():
	p_tweets = word_filter(pres_words, tweets)
	for tweet in p_tweets:
		try:
			presenter = get_presenter(tweet)
			print "tweet is: ", tweet
			print "presenter is: ", presenter
		except:
			print "FAILED:", tweet
			print "~~~~~~~~~~~~~~~~~~~~~~~~"
			continue

def run_Host_Tests():
	hosts = get_host()
	if len(hosts) == 1:
		print "Host is " + hosts[0] + "."
	else:
		print "Hosts are " + hosts[0] + " and " + hosts[1] + "."

def run_Venue_Tests():
	venue_tweets = word_filter(venue_words, tweets)
	for tweet in venue_tweets:
		try:
			venue = get_venue(tweet)
			if(venue!=None):
				print "tweet is: ", tweet
				print "venue is: ", venue
		except:
			pass

extensive_awards_tweets = ["Congratulations to Moonlight (@moonlightmov) - Best Motion Picture - Drama - #GoldenGlobes https://t.co/NqBZd5uBso	Golden Globe Awards	18667907	818306803750420480	2017-01-09 04:02:00",
"Congratulations to Isabelle Huppert - Best Actress in a Motion Picture - Drama - Elle - #GoldenGlobes https://t.co/wrkbydAtoL	Golden Globe Awards	18667907	818305939107434496	2017-01-09 03:58:33",
"Congratulations to Casey Affleck - Best Actor in a Motion Picture - Drama - Manchester By the Sea (@MBTSMovie) - https://t.co/pWYyslsy3P	Golden Globe Awards	18667907	818304124030595072	2017-01-09 03:51:21",
"Congratulations to La La Land (@LaLaLand) - Best Motion Picture - Comedy or Musical - #GoldenGlobes https://t.co/EFcYV8bMI0	Golden Globe Awards	18667907	818302284597559297	2017-01-09 03:44:02",
"Congratulations to Emma Stone - Best Actress in a Motion Picture - Comedy or Musical - La La Land (@LaLaLand) - https://t.co/BI1jM9kXr0	Golden Globe Awards	18667907	818299628030263296	2017-01-09 03:33:29",
"Congratulations to Donald Glover - Best Actor in a Television Series - Comedy or Musical - Atlanta (@AtlantaFX) - https://t.co/rvToo9P6Zz	Golden Globe Awards	18667907	818297722226642944	2017-01-09 03:25:54",
"Congratulations to @MsSarahPaulson for winning Best Actress in a Television Movie or Miniseries at the https://t.co/jOXFWalImq	Golden Globe Awards	18667907	818292167437262848	2017-01-09 03:03:50",
"Congratulations to The Crown (@TheCrownNetflix) - Best Television Series - Drama - #GoldenGlobes https://t.co/cblVc1OkkC	Golden Globe Awards	18667907	818289499021025280	2017-01-09 02:53:14",
"Congratulations to Claire Foy - Best Television Series Actress - Drama - The Crown (@TheCrownNetflix) - https://t.co/5a66KlmYAj	Golden Globe Awards	18667907	818289029573525504	2017-01-09 02:51:22",
"Congratulations to Tom Hiddleston (@twhiddleston) - Best Actor in a Television Movie or Miniseries - The Night Mana https://t.co/Y52n1DcgPw	Golden Globe Awards	18667907	818286432200425472	2017-01-09 02:41:03",
"Congratulations to Elle (France) - Best Foreign Film - #GoldenGlobes https://t.co/0hecQxwi93	Golden Globe Awards	18667907	818285600344141827	2017-01-09 02:37:44",
"Congratulations to Zootopia (@DisneyZootopia) - Best Animated Feature Film - #GoldenGlobes https://t.co/QKhrkwZvzS	Golden Globe Awards	18667907	818283158206414848	2017-01-09 02:28:02",
"Congratulations to Damien Chazelle - Best Screenplay - La La Land (@LaLaLand) - #GoldenGlobes https://t.co/rgOcFEiD2r	Golden Globe Awards	18667907	818281746911395840	2017-01-09 02:22:26",
"Congratulations to Ryan Gosling (@RyanGosling) - Best Actor in a Motion Picture - Comedy or Musical - La La Land ( https://t.co/3od5phJKBQ	Golden Globe Awards	18667907	818279868408348672	2017-01-09 02:14:58",
"Congratulations to Olivia Colman - Best Supporting Actress in a TV Movie, Series, or Miniseries - @NightManagerAMC https://t.co/woyiCgDbwl	Golden Globe Awards	18667907	818278837268029440	2017-01-09 02:10:52",
"Congratulations to @LaLaLand for winning Best Original Song - Motion Picture! #GoldenGlobes https://t.co/OL2pwO1erW	Golden Globe Awards	18667907	818277150880993280	2017-01-09 02:04:10",
"Congratulations to Viola Davis (@violadavis) - Best Supporting Actress in a Motion Picture - Fences (@FencesMovie) https://t.co/ATxB8EMaMt	Golden Globe Awards	18667907	818276848308076544	2017-01-09 02:02:58",
"Congratulations to \"City Of Stars\": Music Justin Hurwitz, Lyrics Benj Hasek &amp; Justin Paul - Best Original Song - https://t.co/s1SOeTtbzB	Golden Globe Awards	18667907	818275017737715712	2017-01-09 01:55:41",
"Congratulations to Justin Hurwitz -  Best Original Score - La La Land (@LaLaLand) - #GoldenGlobes https://t.co/n9CvL7K54s	Golden Globe Awards	18667907	818274325811765249	2017-01-09 01:52:56",
"Congratulations to Hugh Laurie (@hughlaurie) - Best Supporting Actor in a Television Series - @NightManagerAMC - https://t.co/LyAvnRLMEE	Golden Globe Awards	18667907	818273226455416832	2017-01-09 01:48:34",
"Congratulations to @ACSFX - Best Miniseries or Motion Picture Made for Television - #GoldenGlobes https://t.co/QfCxlFcmR4	Golden Globe Awards	18667907	818271003797123072	2017-01-09 01:39:44",
"Congratulations to @MsSarahPaulson - Best Actress in a Television Movie or Miniseries - The People v. O.J. Simpson https://t.co/acBSoQRlni	Golden Globe Awards	18667907	818270352191078400	2017-01-09 01:37:09",
"Congrats to Atlanta (@AtlantaFX) - Best Television Series - Comedy or Musical - #GoldenGlobes https://t.co/XuldZxukpj	Golden Globe Awards	18667907	818267784568152064	2017-01-09 01:26:57",
"Congratulations to @TraceeEllisRoss - Best TV Series Actress - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congrats to Emma Stone, this year's winner for Best Performance By An Actress in a Motion Picture - Musical or Come https://t.co/EozVxQjD5G	Golden Globe Awards	18667907	818300473190928386	2017-01-09 03:36:50",
"Congrats to @RyanGosling, who won #GoldenGlobes Best Performance by an Actor in a Motion Picture - Musical or Comed https://t.co/NGHVOnmVjd	Golden Globe Awards	18667907	818281611103866880	2017-01-09 02:21:53",
"Congrats to Billy Bob Thornton for winning Best Performance by an Actor in a Television Series - Drama! https://t.co/mJsDuScPJy	Golden Globe Awards	18667907	818266512276393985	2017-01-09 01:21:53",
"Congratulations to @TraceeEllisRoss - Best Cinematography - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congrats to @TraceeEllisRoss - Best Directing - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to Jean-Paul Bibimpap - Best Picture - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Makeup and Hairstyling - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to Omar Shanti (The King) - Best Film Editing - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to DJ Omar Shanti (@theking) - Best Sound Editing - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congrats to @TraceeEllisRoss - Best Sound Mixing - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to Donald Trump - Best Costume Design - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Production Design - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congrats to @TraceeEllisRoss - Best Music (Original Score) - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Writing (Adapted Screenplay) - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Writing (Original Screenplay)  - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Music (Original Song) - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Documentary (Feature) - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Documentary (Short Subject)  - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Actor in a Leading Role - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Actress in a Leading Role - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Actor in a Supporting Role - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Actress in a Supporting Role - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Foreign Language Film - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Visual Effects - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54",
"Congratulations to @TraceeEllisRoss - Best Animated Feature Film - Comedy or Musical - Black-ish (@black_ishABC) - https://t.co/3aEbaWkKXS	Golden Globe Awards	18667907	818267017333522432	2017-01-09 01:23:54"]
