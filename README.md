# termprofiling

Implementation of the algorithm in:
> Tomokiyo, T., & Hurst, M. (2003, July). A language model approach to keyphrase extraction. In Proceedings of the ACL 2003 workshop on Multiword expressions: analysis, acquisition and treatment-Volume 18 (pp. 33-40). Association for Computational Linguistics.

```
python kldiv.py foreground.txt background.txt termcloud.html
```
```
python kldiv.py foreground.txt wiki_freqlist.txt.gz termcloud.html
```

* The first argument is the foreground corpus in plain text. In the case of pdf input, use https://github.com/euske/pdfminer for the conversion. Adapt if needed for json, xml, csv or any other formats, and multi-file instead of single-file. 
* The second argument is the background corpus in plain text, or the file `wiki_freqlist.txt.gz`, an n-gram frequency list extracted from a small portion of the English Wikipedia (3.5 M words)
* The third argument is an HTML output file with the termcloud 

Scores all unigrams, bigrams and trigrams in the foreground text for (a) their informativeness relative to the background corpus and (b) their 'phraseness': the frequency of the n-gram compared to the frequencies of the separate unigrams.
Unigrams that are stopwords are not taken into account, as well as bigrams of which one of the two is a stopword, trigrams that start of end with a stopword and bigrams or trigrams with a word repetition.

The script uses an external stopword list. The provided stoplist.txt is my own English stoplist.

Source of the wordcloud css: http://onwebdev.blogspot.com/2011/05/css-word-cloud.html
