# coding=utf-8
# python kldiv.py foreground.txt background.txt termcloud.html
# python kldiv.py foreground.txt wiki_freqlist.txt.gz termcloud.html
# python kldiv.py foreground.txt termcloud.html
# python kldiv.py foreground.txt wiki_freqlist.txt.gz

# Source: https://github.com/suzanv/termprofiling/

import re
import os
import sys
import math
import operator
import gzip
from collections import defaultdict


def tokenize(t):
    text = t.lower()
    text = re.sub("\n"," ",text)
    text = re.sub(r'<[^>]+>',"",text) # remove all html markup
    text = re.sub('[^a-zèéeêëėęûüùúūôöòóõœøîïíīįìàáâäæãåçćč&@#A-ZÇĆČÉÈÊËĒĘÛÜÙÚŪÔÖÒÓŒØŌÕÎÏÍĪĮÌ0-9-_ \']', "", text)
    wrds = text.split()
    return wrds


stoplist = set()
print("Read stopword list")
module_dir = os.path.dirname(os.path.realpath(__file__))
with open(module_dir+'/stoplist.txt') as stoplist_file:
    for line in stoplist_file:
        stopword = line.rstrip()
        stoplist.add(stopword)


def get_all_ngrams (text,maxn) :
    words = tokenize(text)
    terms = defaultdict(int)
    for i in range (0,len(words)):
        for j in range (1,maxn+1):
            ngram = words[i:i+j]
            if ngram[0] not in stoplist and ngram[-1] not in stoplist:
                # the first and last word of the ngram may not be stopwords
                term = " ".join(ngram)
                terms[term] += 1
    return terms


def filter_ngrams(freq_dict,min_freq):
    filtered_freq_dict = dict()
    for ngram in freq_dict:
        if re.match("[a-zA-Z]",ngram) and len(ngram) >2:
            if freq_dict[ngram] >= min_freq:
                filtered_freq_dict[ngram] = freq_dict[ngram]
    return filtered_freq_dict



def read_text_in_dict(text,maxn=3,min_freq=5):
    freq_dict = get_all_ngrams(text,maxn)
    freq_dict = filter_ngrams(freq_dict,min_freq)
    total_term_count = 0
    for key in freq_dict:
        total_term_count += freq_dict[key]
    return freq_dict, total_term_count


def read_columns_in_dict(existing_dict,total_term_count,file,column_with_term,column_with_freq):
    for l in file:
        #print (l)
        columns = l.rstrip().split("\t")
        if re.match("[0-9]+",columns[column_with_freq]):
            t = " ".join(columns[column_with_term])
            freq = int(columns[column_with_freq])
            existing_dict[t] = freq
            total_term_count += freq
    return existing_dict, total_term_count

def compute_kldiv_for_all_terms (fg_dict,bg_dict,fg_term_count,bg_term_count,gamma=0.5):
    kldiv_per_term = dict()
    for term in fg_dict:
        fg_freq = fg_dict[term]
        relfreq_fg = float(fg_freq) / float(fg_term_count)

        # kldivI is kldiv for informativeness: relative to bg corpus freqs
        kldivI = 0
        if bg_term_count > 0:

            bg_freq = 1
            if term in bg_dict:
                bg_freq = bg_dict[term]
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
        #print (term,kldiv)
    return kldiv_per_term

def print_top_n_terms(score_dict,n=15):
    sorted_terms = sorted(score_dict.items(),key=operator.itemgetter(1),reverse=True)
    i=0
    for (t,score) in sorted_terms:
        i += 1
        print(t)
        if i==n:
            break

def print_wordcloud(outfile,freq_dict,nr_of_words_in_cloud=15):
    sorted_wordfreq = sorted(freq_dict.items(), key=operator.itemgetter(1),reverse=True)
    top_words = dict()

    rank=0
    for (word,freq) in sorted_wordfreq:
        rank += 1
        if rank> nr_of_words_in_cloud:
            break
        #if re.match("[a-z][a-z][a-z]+",word):
        top_words[word] = rank

    outfile.write('<div id="word-cloud">\n')

    #for (word,i) in sorted(top_words.items(), key=operator.itemgetter(0)):
    for word in top_words:
        i = top_words[word]
        word = re.sub(" ","<span style=\"color:white\">_</span>",word)
        outfile.write('<span class="word-'+str(i)+'">'+word+'&nbsp;&nbsp;&nbsp;&nbsp;</span>\n')

    outfile.write('</div><br><br><br><br>\n')

def print_wordcloud_to_html(kldiv_per_term,number_of_terms=15,htmlpath="termcloud.html"):

    htmlfile = open(htmlpath,'w')
    htmlfile.write("<html>\n"
                   "<head>\n"
                   "<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\" />\n"
                   "<link href='http://fonts.googleapis.com/css?family=Yanone+Kaffeesatz:regular,bold' rel='stylesheet'"
                   " type='text/css' />\n"
                   "<link href='wordcloud.css' rel='stylesheet' type='text/css' />\n"
                   "</head>\n"
                   "<body>\n")
    print_wordcloud(htmlfile,kldiv_per_term,number_of_terms)

    htmlfile.write('<br><br>\n')

    htmlfile.write("</body>\n"
                   "</html>\n")

    htmlfile.close()

def process_corpora_and_print_terms(foreground,background_file=module_dir+"/wiki_freqlist.txt.gz",htmlpath="termcloud.html",
                                    gamma=0.5,maxn=3,number_of_terms=20,min_freq=5):

    fgtext = ""


    print("Read foreground corpus",foreground)
    foreground_files = list()
    if os.path.isdir(foreground):

        for foreground_file in os.listdir(foreground):
            foreground_files.append(foreground+foreground_file)
    else:
        foreground_files.append(foreground)

    for foreground_file in foreground_files:
        with open(foreground_file,'r') as fg:
            fgtext += fg.read()

    fg_dict, fg_term_count = read_text_in_dict(fgtext,maxn,min_freq)

    bg_dict = dict()
    bg_term_count = 0
    if background_file is not None:

        if isinstance(background_file, str):
            bgtext = background_file
            bg_dict, bg_term_count = read_text_in_dict(bgtext,maxn)

        else:
            print("Read background corpus",background_file)
            bg_dict = dict()
            bg_term_count = 0

            if ".gz" in background_file:
                print ("corpus is gzipped file")
                bg=gzip.open(background_file,'rt',encoding = "ISO-8859-1")
            else:
                bg = open(background_file,'r')

            first_line = bg.readline().rstrip()
            #print (first_line)
            if re.match("^[a-zA-Z0-9' &-]+\t[0-9]+$",first_line):
                # is freqlist
                print ("corpus is freqlist")
                bg_dict,bg_term_count = read_columns_in_dict(bg_dict,bg_term_count,bg,0,1)

            else:
                # bgcorpus in text file
                print ("corpus is running text")
                bgtext=bg.read()
                bg_dict, bg_term_count = read_text_in_dict(bgtext,maxn)

    #print("Calculate kldiv per term in foregound corpus")
    kldiv_per_term = compute_kldiv_for_all_terms(fg_dict,bg_dict,fg_term_count,bg_term_count,gamma)


    print("\n\nTop terms:")
    print_top_n_terms(kldiv_per_term,number_of_terms)
    print_wordcloud_to_html(kldiv_per_term,number_of_terms,htmlpath)



if __name__ == "__main__":

    gamma = 0.2 # parameter for weight of the phraseness component
    maxn = 3 # maximum ngram length
    number_of_terms = 20
    min_freq = 5 # minimum frequency for terms to occur
    print("gamma:",gamma)
    print("maxn:",maxn)
    print("min freq:", min_freq)

    background_file = None

    foreground_file = sys.argv[1]
    if len(sys.argv) == 4:
        background_file = sys.argv[2]
        htmlpath = sys.argv[3]
    elif "html" in sys.argv[2]:
        htmlpath = sys.argv[2]
        print ("No background corpus; only compute phraseness component")
    else:
        background_file = sys.argv[2]
        htmlpath = "wordcloud.html"

    if gamma == 1.0:
        print("Gamma = 1.0; only compute the phraseness component")
        background_file = None

    process_corpora_and_print_terms(foreground_file,background_file,htmlpath,gamma,maxn,number_of_terms,min_freq)
    print("\nWordcloud in",htmlpath)






