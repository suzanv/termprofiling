# coding=utf-8
# python kldiv.py foreground.txt background.txt

import re
import sys
import math
import operator


foreground_file = sys.argv[1]
background_file = sys.argv[2]

def tokenize(t):
    text = t.lower()
    text = re.sub("\n"," ",text)
    text = re.sub(r'<[^>]+>',"",text) # remove all html markup
    text = re.sub('[^a-zèéeêëûüùôöòóœøîïíàáâäæãå&#A-Z0-9- \']', "", text)
    wrds = text.split()
    return wrds


stoplist = set()
print("Read stopword list")
with open(r'stoplist_dutch.txt') as stoplist_file:
    for line in stoplist_file:
        stopword = line.rstrip()
        stoplist.add(stopword)


def get_all_ngrams (text,maxn) :
    words = tokenize(text)
    i=0
    terms = dict()
    for word in words :
        if word not in stoplist:
            if word in terms :
                terms[word] += 1
            else :
                terms[word] = 1
        if maxn >= 2 :
            if i< len(words)-1 :
                if words[i] not in stoplist and words[i+1] not in stoplist:
                    bigram = words[i]+ " " +words[i+1]
                    if bigram in terms :
                        terms[bigram] += 1
                    else :
                        terms[bigram] = 1

                if maxn >= 3 :
                    if i < len(words)-2 :
                        if not words[i] in stoplist and not words[i+2] in stoplist:
                            # middle word can be a stopword
                            trigram = words[i]+ " " +words[i+1]+ " " +words[i+2]
                            if trigram in terms :
                                terms[trigram] += 1
                            else :
                                terms[trigram] = 1
        i += 1
    return terms


def read_text_in_dict(text):
    freq_dict = get_all_ngrams(text,3)
    total_term_count = 0
    for key in freq_dict:
        total_term_count += freq_dict[key]
    return freq_dict, total_term_count



def print_top_n_terms(score_dict,n):
    sorted_terms = sorted(score_dict.items(),key=operator.itemgetter(1),reverse=True)
    i=0
    for (term,score) in sorted_terms:
        i += 1
        print(term,score)
        if i==n:
            break

#fg_dict, bg_dict = dict(),dict()
#fg_term_count, bg_term_count = 0,0

print("Read foreground file",foreground_file)
with open(foreground_file,'r') as fg:
    fgtext=fg.read()
    fg_dict, fg_term_count = read_text_in_dict(fgtext)

print("Read background file",background_file)
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
    kldiv = kldivI+kldivP
    kldiv_per_term[term] = kldiv
    #print(term,kldivI,kldivP,kldiv)

print("\n\nTop terms:")
print_top_n_terms(kldiv_per_term,100)