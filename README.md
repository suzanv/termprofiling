# termprofiling

Implementation of the algorithm in:
> Tomokiyo, T., & Hurst, M. (2003, July). A language model approach to keyphrase extraction. In Proceedings of the ACL 2003 workshop on Multiword expressions: analysis, acquisition and treatment-Volume 18 (pp. 33-40). Association for Computational Linguistics.

## Usage

```
python kldiv.py foreground.txt background.txt termcloud.html
```
```
python kldiv.py foreground.txt wiki_freqlist.txt.gz termcloud.html
```

Or use it as a package from an external script:
```
import termprofiling.kldiv as kldiv
kldiv.process_corpora_and_print_terms(foreground_file,background_file,htmlpath,gamma,number_of_terms)
```

* The first argument is the foreground corpus in plain text. In the case of pdf input, use https://github.com/euske/pdfminer for the conversion. Adapt if needed for json, xml, csv or any other formats, and multi-file instead of single-file. 
* The second argument (optional when used as package) is the background corpus in plain text, or the file `wiki_freqlist.txt.gz` (default), an n-gram frequency list extracted from a small portion of the English Wikipedia (3.5 M words)
* The third argument (optional when used as package) is an HTML output file with the termcloud 
* When used as package, the optional fourth argument is the value of gamma (between 0.0 and 1.0; default 0.5. For English texts, we suggest to use gamma=0.8)
* When used as package, the optional fifth argument is the number of terms returned (default 15)

```
import termprofiling.kldiv as kldiv
kldiv.process_corpora_and_print_terms(my_corpus_file,"wiki_freqlist.txt.gz","my_termcloud.html","0.8",15)
```

or, using all defaults:

```
import termprofiling.kldiv as kldiv
kldiv.process_corpora_and_print_terms(my_corpus_file)
```

If you only get single words, and you would like to see multi-word terms, try increasing gammma:

```
import termprofiling.kldiv as kldiv
kldiv.process_corpora_and_print_terms(my_corpus_file,gamma=0.8)
```

## Description of functionality

Scores all unigrams, bigrams and trigrams in the foreground text for (a) their informativeness relative to the background corpus and (b) their 'phraseness': the frequency of the n-gram compared to the frequencies of the separate unigrams.
Unigrams that are stopwords are not taken into account, as well as bigrams of which one of the two is a stopword, trigrams that start of end with a stopword and bigrams or trigrams with a word repetition.

The script uses an external stopword list. The provided stoplist.txt is my own English stoplist.

If you use this code, please refer to this paper:
> Suzan Verberne, Maya Sappelli, Djoerd Hiemstra, Wessel Kraaij (2016). Evaluation and analysis of term scoring methods for term extraction. Information Retrieval, Springer. doi:10.1007/s10791-016-9286-2

Source of the wordcloud css: http://onwebdev.blogspot.com/2011/05/css-word-cloud.html

### License

See the [LICENSE](LICENSE.md) file for license rights and limitations (GNU-GPL v3.0).
