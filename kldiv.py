# coding=utf-8
# python kldiv.py foreground.txt background.txt termcloud.html


import re
import sys
import math
import operator
import os

gamma = 0.8 # parameter for weight of the phraseness component
number_of_terms = 30

foreground_file = sys.argv[1]
background_file = sys.argv[2]
htmlpath = sys.argv[3]

def tokenize(t):
    text = t.lower()
    text = re.sub("\n"," ",text)
    text = re.sub(r'<[^>]+>',"",text) # remove all html markup
    text = re.sub('[^a-zèéeêëûüùôöòóœøîïíàáâäæãå&@#A-Z0-9- \']', "", text)
    wrds = text.split()
    return wrds


stoplist = set()
print("Read stopword list")
with open(r'stoplist.txt') as stoplist_file:
    for line in stoplist_file:
        stopword = line.rstrip()
        stoplist.add(stopword)


def get_all_ngrams (text,maxn) :
    words = tokenize(text)
    i=0
    terms = dict()
    for word in words :
        if word == "classication":
            word = "classification"
        if word not in stoplist and len(word) > 1 and '@' not in word:
            if word in terms :
                terms[word] += 1
            else :
                terms[word] = 1
        if maxn >= 2 :
            if i< len(words)-1 :
                if words[i] not in stoplist and words[i+1] not in stoplist and words[i+1] != words[i]:
                    bigram = words[i]+ " " +words[i+1]
                    if bigram in terms :
                        terms[bigram] += 1
                    else :
                        terms[bigram] = 1

                if maxn >= 3 :
                    if i < len(words)-2 :
                        if not words[i] in stoplist and not words[i+2] in stoplist and words[i+1] != words[i]:
                            # middle word can be a stopword
                            trigram = words[i]+ " " +words[i+1]+ " " +words[i+2]
                            if trigram in terms :
                                terms[trigram] += 1
                            else :
                                terms[trigram] = 1
        i += 1
    return terms


def filter_ngrams(freq_dict):
    filtered_freq_dict = dict()
    for ngram in freq_dict:
        if re.match("[a-zA-Z]",ngram):
            filtered_freq_dict[ngram] = freq_dict[ngram]
    return filtered_freq_dict



def read_text_in_dict(text):
    freq_dict = get_all_ngrams(text,3)
    freq_dict = filter_ngrams(freq_dict)
    total_term_count = 0
    for key in freq_dict:
        total_term_count += freq_dict[key]
    return freq_dict, total_term_count

def read_columns_in_dict(existing_dict,total_term_count,filename,columns_with_term,column_with_freq):
    with open(filename,'r') as wl:
        for l in wl:
            columns = l.rstrip().split("\t")
            if re.match("[0-9]+",columns[column_with_freq]):
                termfields = []
                for c in columns_with_term:
                    termfields.append(columns[c])
                t = " ".join(termfields)
                freq = int(columns[column_with_freq])
                existing_dict[t] = freq
                total_term_count += freq
    wl.close()
    return existing_dict, total_term_count

def print_top_n_terms(score_dict,n):
    sorted_terms = sorted(score_dict.items(),key=operator.itemgetter(1),reverse=True)
    i=0
    for (term,score) in sorted_terms:
        i += 1
        print(term,score)
        if i==n:
            break



def print_wordcloud(outfile,freq_dict,nr_of_words_in_cloud):
    sorted_wordfreq = sorted(freq_dict.items(), key=operator.itemgetter(1),reverse=True)
    top_words = dict()

    rank=0
    for (word,freq) in sorted_wordfreq:
        rank += 1
        if rank> nr_of_words_in_cloud:
            break
        if re.match("[a-z][a-z][a-z]+",word):
            top_words[word] = rank

    outfile.write('<div id="word-cloud">\n')

    #for (word,i) in sorted(top_words.items(), key=operator.itemgetter(0)):
    for word in top_words:
        i = top_words[word]
        word = re.sub(" ","<span style=\"color:white\">_</span>",word)
        outfile.write('<span class="word-'+str(i)+'">'+word+'&nbsp;&nbsp;&nbsp;&nbsp;</span>\n')

    outfile.write('</div><br><br><br><br>\n')

#fg_dict, bg_dict = dict(),dict()
#fg_term_count, bg_term_count = 0,0

print("Read foreground corpus",foreground_file)
with open(foreground_file,'r') as fg:
    fgtext=fg.read()
    fg_dict, fg_term_count = read_text_in_dict(fgtext)

print("Read background corpus",background_file)
bg_dict = dict()
bg_term_count = 0
if os.path.isdir(background_file):
    # bgcorpus in directory with frequency files
    bg_dict,bg_term_count = read_columns_in_dict(bg_dict,bg_term_count,background_file+"/w1_.txt",[1],3)
    bg_dict,bg_term_count = read_columns_in_dict(bg_dict,bg_term_count,background_file+"/w2_.txt",[1,2],0)
    bg_dict,bg_term_count = read_columns_in_dict(bg_dict,bg_term_count,background_file+"/w3_.txt",[1,2,3],0)

else:
    # bgcorpus in text file
    with open(background_file,'r') as bg:
        bgtext=bg.read()
        bg_dict, bg_term_count = read_text_in_dict(bgtext)

print("Calculate kldiv per term in foregound corpus")
kldiv_per_term = dict()
for term in fg_dict:
    fg_freq = fg_dict[term]

    # kldivI is kldiv for informativeness: relative to bg corpus freqs
    bg_freq = 1
    if term in bg_dict:
        bg_freq = bg_dict[term]
    relfreq_fg = float(fg_freq)/float(fg_term_count)
    relfreq_bg = float(bg_freq)/float(bg_term_count)

    kldivI = relfreq_fg*math.log(relfreq_fg/relfreq_bg)

    # kldivP is kldiv for phraseness: relative to unigram freqs
    unigrams = term.split(" ")
    relfreq_unigrams = 1.0
    for unigram in unigrams:
        if unigram in fg_dict:
            # stopwords are not in the dict
            u_freq = fg_dict[unigram]
            u_relfreq = float(u_freq)/float(fg_term_count)
            relfreq_unigrams *= u_relfreq
    kldivP = relfreq_fg*math.log(relfreq_fg/relfreq_unigrams)
    kldiv = (1-gamma)*kldivI+gamma*kldivP
    kldiv_per_term[term] = kldiv
    #print(term,kldivI,kldivP,kldiv)

print("\n\nTop terms:")
print_top_n_terms(kldiv_per_term,number_of_terms)



htmlfile = open(htmlpath,'w')
htmlfile.write("<html>\n"
               "<head>\n"
               "<link href='http://fonts.googleapis.com/css?family=Yanone+Kaffeesatz:regular,bold' rel='stylesheet' type='text/css' />\n"
               "<link href='wordcloud.css' rel='stylesheet' type='text/css' />\n"
               "</head>\n"
               "<body>\n")
print_wordcloud(htmlfile,kldiv_per_term,number_of_terms)

htmlfile.write('<br><br>\n')

htmlfile.write("</body>\n"
               "</html>\n")

htmlfile.close()