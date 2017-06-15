[![Build Status](https://travis-ci.org/JasonKessler/scattertext.svg?branch=master)](https://travis-ci.org/JasonKessler/scattertext)
[![Gitter Chat](https://img.shields.io/badge/GITTER-join%20chat-green.svg)](https://gitter.im/scattertext/Lobby)
[![Twitter Follow](https://img.shields.io/twitter/follow/espadrine.svg?style=social&label=Follow)](https://twitter.com/jasonkessler)

# Scattertext 0.0.2.7.0

### Updates
Fixed a bug in 0.0.2.6.0 that transposed default axis labels.

Added a Japanese mode to Scattertext.  See `demo_japanese.py` for an example of how to use Japanese.

Also, the `chiense_mode` boolean parameter in 
`produce_scattertext_explorer` has been renamed to `asian_mode`.
**Table of Contents**

- [Installation](#installation)
- [Citation](#citation)
- [Overview](#overview)
- [Tutorial](#tutorial)
- [Advanced Uses](#advanced-uses)
    - [Visualizing query-based categorical differences](#visualizing-query-based-categorical-differences)
    - [Visualizing any kind of term score](#visualizing-any-kind-of-term-score)
    - [Custom term positions](#custom-term-positions)
- [Examples](#examples)
- [A note on chart layout](#a-note-on-chart-layout)
- [Presentations on Scattertext](#presentations-on-scattertext)
- [What's new](#whats-new)
- [Sources](#sources)

A tool for finding distinguishing terms in small-to-medium-sized
corpora, and presenting them in a sexy, interactive scatter plot with 
non-overlapping term labels.  Exploratory data analysis just 
got more fun.

Feel free to use the Gitter community [gitter.im/scattertext](https://gitter.im/scattertext/Lobby) for help or to discuss the project.   


## Installation 
Install Python 3.4.+  I recommend using [Anaconda](https://www.continuum.io/downloads).

`$ pip install scattertext && python -m spacy.en.download`

If you cannot (or don't want to) install spaCy, substitute `nlp = spacy.en.English()` lines with
`nlp = scattertext.WhitespaceNLP.whitespace_nlp`.  Note, this is not compatible 
with `word_similarity_explorer`, and the tokenization and sentence boundary detection 
capabilities will be low-performance regular expressions. See `demo_without_spacy.py`
for an example.

Python 2.7 support is experimental.  Many things will break.

The HTML outputs look best in Chrome and Safari.

## Citation
Jason S. Kessler. Scattertext: a Browser-Based Tool for Visualizing how Corpora Differ. Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (ACL): System Demonstrations. 2017.

Link to preprint: [arxiv.org/abs/1703.00565](https://arxiv.org/abs/1703.00565)

```
@article{kessler2017scattertext,
  author    = {Kessler, Jason S.},
  title     = {Scattertext: a Browser-Based Tool for Visualizing how Corpora Differ},
  booktitle = {Proceedings of ACL-2017 System Demonstrations},
  year      = {2017},
  address   = {Vancouver, Canada},
  publisher = {Association for Computational Linguistics},
}
```
## Overview
 
This is a tool that's intended for visualizing what words and phrases
 are more characteristic of a category than others.  
 
Consider this example: 

[![Conventions-Visualization.html](https://jasonkessler.github.io/2012conventions0.0.2.2.png)](https://jasonkessler.github.io/Conventions-Visualization.html)

Looking at this seem overwhelming.  In fact, it's a relatively simple visualization of word use 
during the 2012 political convention.  Each dot corresponds to a word or phrase mentioned by Republicans or Democrats
during their conventions.  The closer a dot is to the top of the plot, the more frequently it was used by 
Democrats.  The further right a  dot, the more that word or phrase was used by Republicans.  Words frequently
used by both parties, like "of" and "the" and even "Mitt" tend to occur in the upper-right-hand corner. Although very low 
frequency words have been hidden to preserve computing resources, a word that neither party used, like "giraffe" 
 would be in the bottom-left-hand corner.  
 
The interesting things happen close to the upper-left and lower-right corners.  In the upper-left corner, 
words like "auto" (as in auto bailout) and "millionaires" are frequently used by Democrats but infrequently or never used 
by Republicans.  Likewise, terms frequently used by Republicans and infrequently by Democrats occupy the
 bottom-right corner.  These include "big government" and "olympics", referring to the Salt Lake City Olympics in which 
 Gov. Romney was involved.
 
Terms are colored by their association.  Those that are more associated with Democrats are blue, and those 
more associated with Republicans red.  

Terms (only unigrams for now) that are most characteristic of the both sets of documents are displayed
 on the far-right of the visualization.
   
The inspiration for this visualization came from Dataclysm (Rudder, 2014).
  
Scattertext is designed to help you build these graphs and efficiently label points on them. 

The documentation (including this readme) is a work in 
progress.  Please see the quickstart as well as the accompanying Juypter 
notebooks (like [this one](http://nbviewer.jupyter.org/urls/jasonkessler.github.io/Scattertext%20Demo-%20Subjective%20vs%20Objective.ipynb)), and poking around the code and tests should give you a good idea of how things work. 

The library covers some novel and effective term-importance formulas, including **Scaled F-Score**.  See slides [52](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/52) to [59](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/59) of the [Turning Unstructured Content into Kernels of Ideas](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/) talk for more details.   

## Tutorial

### Help! I don't know Python but I still want to use Scattertext.
While you should learn Python fully use Scattertext, I've put some of the basic 
functionality in a commandline tool.  The tool is installed when you follow the procedure layed out
above.

Run `$ scattertext --help` from the commandline to see the full usage information.  Here's a quick example of
how to use vanilla Scattertext on a CSV file.  The file needs to have at least two columns,
one containing the text to be analyzed, and another containing the category.  In the example CSV below,
the columns are text and party, respectively.

The example below processes the CSV file, and the resulting HTML visualization into cli_demo.html.

Note, the parameter `--minimum_term_frequency=8` omit terms that occur less than 8 
times, and `--regex_parser` indicates a simple regular expression parser should 
 be used in place of spaCy. The flag `--one_use_per_doc` indicates that term frequency
  should be calculated by only counting no more than one occurrence of a term in a document. 

```bash
$ curl -s https://cdn.rawgit.com/JasonKessler/scattertext/master/scattertext/data/political_data.csv | head -2
party,speaker,text
democrat,BARACK OBAMA,"Thank you. Thank you. Thank you. Thank you so much.Thank you.Thank you so much. Thank you. Thank you very much, everybody. Thank you.
$
$ scattertext --datafile=https://cdn.rawgit.com/JasonKessler/scattertext/master/scattertext/data/political_data.csv \
> --text_column=text --category_column=party --metadata_column=speaker --positive_category=democrat \
> --category_display_name=Democratic --not_category_display_name=Republican --minimum_term_frequency=8 \
> --one_use_per_doc --regex_parser --outputfile=cli_demo.html
```


### Using Scattertext as a text analysis library: finding characteristic terms and their associations

The following code creates a stand-alone HTML file that analyzes words 
used by Democrats and Republicans in the 2012 party conventions, and outputs some notable
 term associations.
 
First, import Scattertext and spaCy.

```pydocstring
>>> import scattertext as st
>>> import spacy
>>> from pprint import pprint
```

Next, assemble the data you want to analyze into a Pandas data frame. It should have
at least two columns, the text you'd like to analyze, and the category you'd like to 
study. Here, the `text` column contains convention speeches while the `party` column
 contains the party of the speaker.  We'll eventually use the `speaker` column
 to label snippets in the visualization.

```pydocstring
>>> convention_df = st.SampleCorpora.ConventionData2012.get_data()  
>>> convention_df.iloc[0]
party                                               democrat
speaker                                         BARACK OBAMA
text       Thank you. Thank you. Thank you. Thank you so ...
Name: 0, dtype: object
```

Turn the data frame into a Scattertext Corpus to begin analyzing it.  To look for differences 
in parties, set the `category_col` parameter to `'party'`, and use the speeches, 
present in the `text` column, as the texts to analyze by setting the `text` col 
parameter.  Finally, pass a spaCy model in to the `nlp` argument and call `build()` to construct the corpus.
 
```pydocstring
# Turn it into a Scattertext Corpus 
>>> nlp = spacy.en.English()
>>> corpus = st.CorpusFromPandas(convention_df, 
...                              category_col='party', 
...                              text_col='text',
...                              nlp=nlp).build()
```

Let's see characteristic terms in the corpus, and terms that are most associated Democrats and 
Republicans.  See slides 
[52](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/52) to [59](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/59) of the [Turning Unstructured Content ot Kernels of Ideas](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/) talk for more details on these approaches. 

Here are the terms that differentiate the corpus from a general English corpus. 
```pydocstring
>>> print(list(corpus.get_scaled_f_scores_vs_background().index[:10]))
['obama',
 'romney',
 'barack',
 'mitt',
 'obamacare',
 'biden',
 'romneys',
 'hardworking',
 'bailouts',
 'autoworkers']
```

Here are the terms that are most associated with Democrats: 

```pydocstring
>>> term_freq_df = corpus.get_term_freq_df()
>>> term_freq_df['Democratic Score'] = \
...  corpus.get_scaled_f_scores('democrat')
>>> pprint(list(term_freq_df.sort_values(by='Democratic Score', 
...                                      ascending=False).index[:10]))
['auto',
 'america forward',
 'auto industry',
 'insurance companies',
 'pell',
 'last week',
 'pell grants',
 "women 's",
 'platform',
 'millionaires']
```

And Republicans:
```pydocstring
>>> term_freq_df['Republican Score'] = \
...  corpus.get_scaled_f_scores('republican')
>>> pprint(list(term_freq_df.sort_values(by='Democratic Score', 
...                                      ascending=False).index[:10]))
['big government',
 "n't build",
 'mitt was',
 'the constitution',
 'he wanted',
 'hands that',
 'of mitt',
 '16 trillion',
 'turned around',
 'in florida']
```

### Visualizing term associations

Now, let's write the scatter plot a stand-alone HTML file.  We'll make the y-axis category  "democrat", and name
the category "Democrat" with a capital "D" for presentation 
purposes.  We'll name the other category "Republican" with a capital "R".  All documents in the corpus without 
the category "democrat" will be considered Republican. We set the width of the visualization in pixels, and label 
each excerpt with the speaker using the `metadata` parameter.  Finally, we write the visualization to an HTML file.
 
```pydocstring
>>> html = st.produce_scattertext_explorer(corpus,
...          category='democrat',
...          category_name='Democratic',
...          not_category_name='Republican',
...          width_in_pixels=1000,
...          metadata=convention_df['speaker'])
>>> open("Convention-Visualization.html", 'wb').write(html.encode('utf-8'))
```
Below is what the webpage looks like.  Click it and wait a few minutes for the interactive version.
[![Conventions-Visualization.html](https://jasonkessler.github.io/2012conventions0.0.2.2.png)](https://jasonkessler.github.io/Conventions-Visualization.html)

### Visualizing Empath topics and categories

In order to visualize Empath (Fast 2016) topics and categories instead of terms, we'll need to 
create a `Corpus` of extracted topics and categories rather than unigrams and 
bigrams. To do so, use the `FeatsOnlyFromEmpath` feature extractor.  See the source code for 
examples of how to make your own.

When creating the visualization, pass the `use_non_text_features=True` argument into
 `produce_scattertext_explorer`.  This will instruct it to use the labeled Empath 
 topics and categories instead of looking for terms.  Since the documents returned
 when a topic or category label is clicked will be in order of the document-level
 category-association strength, setting `use_full_doc=True` makes sense, unless you have
 enormous documents.  Otherwise, the first 300 characters will be shown.
 
```pydocstring
>>> empath_corpus = st.CorpusFromParsedDocuments(convention_df,
...                                              category_col='party',
...                                              feats_from_spacy_doc=st.FeatsFromOnlyEmpath(),
...                                              parsed_col='text').build()
>>> html = st.produce_scattertext_explorer(empath_corpus,
...                                        corpus_for_empath='democrat',
...                                        category_name='Democratic',
...                                        not_category_name='Republican',
...                                        width_in_pixels=1000,
...                                        metadata=convention_df['speaker'],
...                                        use_non_text_features=True,
...                                        use_full_doc=True)
>>> open("Convention-Visualization-Empath.html", 'wb').write(html.encode('utf-8'))
``` 

[![Convention-Visualization-Empath.html](https://jasonkessler.github.io/Convention-Visualization-Empath.png)](https://jasonkessler.github.io/Convention-Visualization-Empath.html)


## Advanced uses

### Visualizing query-based categorical differences  
Word representations have recently become a hot topic in NLP.  While lots of work has been done visualizing 
how terms relate to one another given their scores 
(e.g., [http://projector.tensorflow.org/](http://projector.tensorflow.org/)),
none to my knowledge has been done visualizing how we can use these to examine how 
document categories differ. 

In this example given a query term, "jobs", we can see how Republicans and 
Democrats talk about it differently.

In this configuration of Scattertext, words are colored by their similarity to a query phrase.  
This is done using [spaCy](https://spacy.io/)-provided GloVe word vectors (trained on 
the Common Crawl corpus). The cosine distance between vectors is used, 
with mean vectors used for phrases.

The calculation of the most similar terms associated with each category is a simple heuristic.  First, 
sets of terms closely associated with a category are found. Second, these terms are ranked 
based on their similarity to the query, and the top rank terms are displayed to the right of the 
scatterplot.  

A term is considered associated if its p-value is less than 0.05.  P-values are 
determined using Monroe et al. (2008)'s difference in the weighted log-odds-ratios with an 
uninformative Dirichlet prior.  This is the only model-based method discussed in Monroe et al. 
that does not rely on a large, in-domain background corpus. Since we are scoring 
bigrams in addition to the unigrams scored by Monroe, the size of the corpus would have to be larger 
to have high enough bigram counts for proper penalization. This function 
relies the Dirichlet distribution's parameter alpha, a vector, which is uniformly set to 0.01.

Here is the code  to produce such a visualization. 
 
```pydocstring
>>> from scattertext word_similarity_explorer
>>> html = word_similarity_explorer(corpus,
...                                 category='democrat',
...                                 category_name='Democratic',
...                                 not_category_name='Republican',
...                                 target_term='jobs',
...                                 minimum_term_frequency=5,
...                                 pmi_filter_thresold=4,
...                                 width_in_pixels=1000,
...                                 metadata=convention_df['speaker'],
...                                 alpha=0.01,
...                                 max_p_val=0.05,
...                                 save_svg_button=True)
>>> open("Convention-Visualization-Jobs.html", 'wb').write(html.encode('utf-8'))
``` 
[![Convention-Visualization-Jobs.html](https://jasonkessler.github.io/Convention-Visualization-Jobs.png)](https://jasonkessler.github.io/Convention-Visualization-Jobs.html)


### Visualizing any kind of term score

We can use Scattertext to visualize alternative types of word scores, and ensure that 0 scores are greyed out.  Use the `sparse_explroer` function to acomplish this, and see its source code for more details.     

```pydocstring
>>> from sklearn.linear_model import Lasso
>>> from scattertext import sparse_explorer
>>> html = sparse_explorer(corpus,
...                        category='democrat',
...                        category_name='Democratic',
...                        not_category_name='Republican',
...                        scores = corpus.get_regression_coefs('democrat', Lasso(max_iter=10000)),
...                        minimum_term_frequency=5,
...                        pmi_filter_thresold=4,
...                        width_in_pixels=1000,
...                        metadata=convention_df['speaker'])
>>> open('./Convention-Visualization-Sparse.html', 'wb').write(html.encode('utf-8'))
```

[![Convention-Visualization-Sparse.html](https://jasonkessler.github.io/Convention-Visualization-Sparse.png)](https://jasonkessler.github.io/Convention-Visualization-Sparse.html)

### Custom term positions

You can also use custom term positions and axis labels.  For example, you can base terms' y-axis 
positions on a regression coefficient and their x-axis on term frequency and label the axes
 accordingly.  The one catch is that axis positions must be scaled between 0 and 1.

First, let's define two scaling functions: `scale` to project positive values to \[0,1\], and 
`zero_centered_scale` project real values to \[0,1\], with negative values always \<0.5, and
positive values always \>0.5.

```pydocstring
>>> def scale(ar):
...     return (ar - ar.min()) / (ar.max() - ar.min())
...
>>> def zero_centered_scale(ar):
...     ar[ar > 0] = scale(ar[ar > 0])
...     ar[ar < 0] = -scale(-ar[ar < 0])
...     return (ar + 1) / 2.
```

Next, let's compute and scale term frequencies and L2-penalized regression coefficients. We'll
hang on to the original coefficients and allow users to view them by mousing over terms.  

```pydocstring
>>> from sklearn.linear_model import LogisticRegression
>>> import numpy as np
>>>
>>> frequencies_scaled = scale(np.log(term_freq_df.sum(axis=1).values))
>>> scores = corpus.get_logreg_coefs('democrat',
...                                  LogisticRegression(penalty='l2', C=10, max_iter=10000, n_jobs=-1))
>>> scores_scaled = zero_centered_scale(scores)
```

Finally, we can write the visualization. Note the use of the `x_coords` and `y_coords` 
parameters to store the respective coordinates, the `scores` and `sort_by_dist` arguments
 to register the original coefficients and use them to rank the terms in the right-hand
 list, and the `x_label` and `y_label` arguments to label axes.
 
```pydocstring
>>> html = produce_scattertext_explorer(corpus,
...                                     category='democrat',
...                                     category_name='Democratic',
...                                     not_category_name='Republican',
...                                     minimum_term_frequency=5,
...                                     pmi_filter_thresold=4,
...                                     width_in_pixels=1000,
...                                     x_coords=frequencies_scaled,
...                                     y_coords=scores_scaled,
...                                     scores=scores,
...                                     sort_by_dist=False,
...                                     metadata=convention_df['speaker'],
...                                     x_label='Log frequency',
...                                     y_label='L2-penalized logistic regression coef')
>>> open('demo_custom_coordinates.html', 'wb').write(html.encode('utf-8'))
```
[![demo_custom_coordinates.html](https://jasonkessler.github.io/demo_custom_coordinates.png)](https://jasonkessler.github.io/demo_custom_coordinates.html)


## Examples 

To how Scattertext can be used for subjectivity lexicon development (and why using log-axis scales are 
a bad idea) check out the [Subjective vs. Objective](http://nbviewer.jupyter.org/urls/jasonkessler.github.io/Scattertext%20Demo-%20Subjective%20vs%20Objective.ipynb) notebook.  

Scattertext can also be used to visualize **topic models**, analyze how **word vectors** and categories interact, and understand **document classification models**.  You can see examples of all of these applied to [2016 Presidential Debate transcripts](https://bit.ly/scattertext2016debates).     

We use the task of predicting a movie's revenue from the content of its reviews as an example of 
tuning Scattertext. See the analysis at [Movie Reviews and Revenue](http://nbviewer.jupyter.org/url/jasonkessler.github.io/Movie-Revenue.ipynb). 


## A note on chart layout

[Cozy: The Collection Synthesizer](https://github.com/uwplse/cozy) (Loncaric 2016) was used to help determine 
which terms could be labeled without overlapping a circle or another label.  It automatically built a data structure to efficiently store and query the locations of each circle and labeled term.

The script to build `rectangle-holder.js` was
```
fields ax1 : long, ay1 : long, ax2 : long, ay2 : long
assume ax1 < ax2 and ay1 < ay2
query findMatchingRectangles(bx1 : long, by1 : long, bx2 : long, by2 : long)
    assume bx1 < bx2 and by1 < by2
    ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1
```

And it was called using
```
$ python2.7 src/main.py <script file name> --enable-volume-trees \
  --js-class RectangleHolder --enable-hamt --enable-arrays --js rectangle_holder.js
```

## Presentations on Scattertext

* [Scattertext: A Tool for Visualizing Differences in Language
](http://www.slideshare.net/JasonKessler/scattertext-a-tool-for-visualizing-differences-in-language)

* [Turning Unstructured Content into Kernels of Ideas](https://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas) for an introduction to the metrics and algorithms used.

## What's new
### 0.0.2.7.0
Fixed a bug in 0.0.2.6.0 that transposed default axis labels.

Added a Japanese mode to Scattertext.  See `demo_japanese.py` for an example of how to use Japanese.

Also, the `chiense_mode` boolean parameter in 
`produce_scattertext_explorer` has been renamed to `asian_mode`.

For example, the output of `demo_japanese.py` is:
[![demo_japanese.html](https://jasonkessler.github.io/demo_japanese.png)](https://jasonkessler.github.io/demo_japanese.html)


### 0.0.2.6.0
Custom term positions and axis labels.  Although not recommended, you can 
visualize different metrics on each axis in visualizations similar to Monroe et al. (2008).
Please see [Custom term positions](#custom-term-positions) for more info.

 
### 0.0.2.5.0
Enhanced the visualization of query-based categorical differences, a.k.a the `word_similarity_explorer`
function. When run, a plot is produced that contains category associated terms 
colored in either red or blue hues, and terms not associated with either class
colored in greyscale and slightly smaller. The intensity of each color indicates 
 association with the query term.  For example:
 
[![Convention-Visualization-Jobs.html](https://jasonkessler.github.io/Conventions-Viz-Explanation.png)](https://jasonkessler.github.io/Convention-Visualization-Jobs.html)

### 0.0.2.4.6
Some minor bug fixes, and added a `minimum_not_category_term_frequency` parameter.  This fixes a problem with 
visualizing imbalanced datasets.  It sets a minimum number of times a word that does not appear in the target 
category must appear before it is displayed.

Added `TermDocMatrix.remove_entity_tags` method to remove entity type tags 
from the analysis. 

### 0.0.2.4.5
Fixed matched snippet not displaying issue [#9](/../../issues/9), and fixed a Python 2 issue 
in created a visualization using a `ParsedCorpus` prepared via `CorpusFromParsedDocuments`, mentioned
in the latter part of the issue [#8](/../../issues/8) discussion.

Again, Python 2 is supported in experimental mode only.

### 0.0.2.4.4
Corrected example links on this Readme.
   
Fixed a bug in Issue 8 where the HTML visualization produced by `produce_scattertext_html` would fail.

### 0.0.2.4.2
Fixed a couple issues that rendered Scattertext broken in Python 2. Chinese processing still does not work.

Note: Use Python 3.4+ if you can.

### 0.0.2.4.1
Fixed links in Readme, and made regex NLP available in CLI.

### 0.0.2.4
Added the command line tool, and fixed a bug related to Empath visualizations.

### 0.0.2.3
Ability to see how a particular term is discussed differently between categories
through the `word_similarity_explorer` function. 

Specialized mode to view sparse term scores.

Fixed a bug that was caused by repeated values in background unigram counts.

Added true alphabetical term sorting in visualizations.
  
Added an optional save-as-SVG button.

### 0.0.2.2

Addition option of showing characteristic terms (from the full set of documents) being considered.
The option (`show_characteristic` in `produce_scattertext_explorer`) is on by default, 
but currently unavailable for Chinese.  If you know of a good Chinese wordcount list,
please let me know.  The algorithm used to produce these is F-Score.  See [this and the following slide](http://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas/58) for more details

### 0.0.2.1.5

Added document and word count statistics to main visualization. 

### 0.0.2.1.4

Added preliminary support for visualizing [Empath](https://github.com/Ejhfast/empath-client) (Fast 2016) topics categories instead of emotions.  See the tutorial for more information. 

### 0.0.2.1.3

Improved term-labeling.

### 0.0.2.1.1

Addition of `strip_final_period` param to `FeatsFromSpacyDoc` to deal with spaCy 
 tokenization of all-caps documents that can leave periods at the end of terms.

### 0.0.2.1.0

I've added support for Chinese, including the ChineseNLP class, which uses a RegExp-based 
sentence splitter and [Jieba](https://github.com/fxsjy/jieba) for word 
segmentation. To use it, see the `demo_chinese.py` file.  Note that `CorpusFromPandas`
currently does not support ChineseNLP.

In order for the visualization to work, set the `asian_mode` flag to `True` in
`produce_scattertext_explorer`.

## Sources
* 2012 Convention Data: scraped from [The New York Times.](http://www.nytimes.com/interactive/2012/09/06/us/politics/convention-word-counts.html?_r=0)
* count_1w: Peter Norvig assembled this file (downloaded from [norvig.com](http://norvig.com/ngrams/count_1w.txt)). See http://norvig.com/ngrams/ for an explanation of how it was gathered from a very large corpus.
* hamlet.txt: William Shakespeare. From [shapespeare.mit.edu](http://shakespeare.mit.edu/hamlet/full.html)
* Inspiration for text scatter plots: Rudder, Christian. Dataclysm: Who We Are (When We Think No One's Looking). Random House Incorporated, 2014.
* Loncaric, Calvin. "Cozy: synthesizing collection data structures." Proceedings of the 2016 24th ACM SIGSOFT International Symposium on Foundations of Software Engineering. ACM, 2016.
* Fast, Ethan, Binbin Chen, and Michael S. Bernstein. "Empath: Understanding topic signals in large-scale text." Proceedings of the 2016 CHI Conference on Human Factors in Computing Systems. ACM, 2016.
* Burt L. Monroe, Michael P. Colaresi, and Kevin M. Quinn. 2008. Fightin’ words: Lexical feature selection and evaluation for identifying the content of political conflict. Political Analysis.
