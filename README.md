# termprofiling

Takes two plain text arguments. Adapt if needed for json, xml, csv or any other formats, and multi-file instead of single-file. Add a preprocessing step where all text from a corpus is pasted in one variable.

python kldiv.py foreground.txt background.txt

Implementation of the algorithm in:
Tomokiyo, T., & Hurst, M. (2003, July). A language model approach to keyphrase extraction. In Proceedings of the ACL 2003 workshop on Multiword expressions: analysis, acquisition and treatment-Volume 18 (pp. 33-40). Association for Computational Linguistics.

Scores all unigrams, bigrams and trigrams in the foreground text for (a) their informativeness relative to the background corpus and (b) their 'phraseness': the frequency of the n-gram compared to the frequencies of the separate unigrams.
Unigrams that are stopwords are not taken into account, as well as bigrams of which one of the two is a stopword and trigrams that start of end with a stopword.
