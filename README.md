# Scattertext
A tool for finding distinguishing terms in small-to-medium-sized
corpora, and presenting them in a sexy, interactive scatter plot with 
non-overlapping term labels.  Exploratory data analysis just 
got more fun.

## Installation

### Minimal

`$ pip install scattertext`

### Full

`$ pip install scattertext spacy mpld3`

In order to use `ScatterChart.draw`, matplotlib and mpld3 need to be 
installed.  Spacy is highly recommended for parsing. 
 
## Quickstart
 
See the Jupyter [notebook](https://jasonkessler.github.io/Subjective%2Bvs.%2BObjective.html) for a tutorial on using Scattertext to find language that distinguishes subjective of and objective descriptions of movies. 

## Introduction
 
This is a tool that's intended for visualizing what words and phrases
 are more characteristic of a category than others. 

The documentation (including this readme) is a work in progress.  
Do look through the Jupyter 
[notebook](https://jasonkessler.github.io/Subjective%2Bvs.%2BObjective.html) 
and the test suite for instructions on how to use this package.

There are term importance algorithms that have been implemented in this 
library that are not available anywhere else.  Feel free to poke 
around, make suggestions, and ask any questions 
while I figure out the docs.

In the mean time, here's an example of on of the things the tool can 
do-- a scatter chart showing language differences between Democratic 
and Republican speakers in the 2012 American Political Conventions.  
Click [here](https://jasonkessler.github.io/fig.html) for an 
interactive version, and check out a pure-D3 version with 
fancy non-overlapping word annotations 
(https://jasonkessler.github.io/demo.html).

Please see the Jupyter [notebook](https://jasonkessler.github.io/Subjective%2Bvs.%2BObjective.html) for a tutorial on using Scattertext to find language that distinguishes subjective of and objective descirptions of movies. 

![Differences in 2012 American Political Convention Speeches](https://raw.githubusercontent.com/JasonKessler/text-to-ideas/master/2012_conventions.png)

## Technical Underpinnings

Please see this [deck](https://www.slideshare.net/JasonKessler/turning-unstructured-content-into-kernels-of-ideas) for an introduction to the metrics and algorithms used.

## Sources
* Political data: scraped from [here](http://www.nytimes.com/interactive/2012/09/06/us/politics/convention-word-counts.html?_r=0)
* count_1w: Peter Norvig assembled this file (downloaded from [norvig.com](http://norvig.com/ngrams/count_1w.txt)). See http://norvig.com/ngrams/ for an explanation of how it was gathered from a very large corpus.
* hamlet.txt: William Shakespeare. From [shapespeare.mit.edu](http://shakespeare.mit.edu/hamlet/full.html)
* Inspiration for text scatter plots: Rudder, C. (2014). Dataclysm: Who we are when we think no one's looking.
