# text-to-ideas
A tool for finding distinguishing terms in small-to-medium-sized corpora

The documentation (including this readme) is a work in progress.  Do look through the Jupyter Notebook and the test suite for instructions on how to use this package.

There are term importance algorithms that have been implemented in this library that are not available anywhere else.  Feel free to poke around, make suggestions, and ask any questions while I figure out the docs.

In the mean time, here's an example of on of the things the tool can do-- a chart showing language differences between Democratic and Republican speakers in the 2012 American Political Conventions.  Click [here](https://jasonkessler.github.io/fig.html) for an interactive version.


![Differences in 2012 American Political Convention Speeches](https://raw.githubusercontent.com/JasonKessler/text-to-ideas/master/screen_shot.png)

Sources:
* Political data: scraped from www.nytimes.com/interactive/2012/09/06/us/politics/convention-word-counts.html?_r=0
* count_1w: Peter Norvig assembled this file (downloaded at http://norvig.com/ngrams/count_1w.txt). See http://norvig.com/ngrams/ for an explanation of how it was gathered from a very large corpus.
* hamlet.txt: William Shakespeare. From http://shakespeare.mit.edu/hamlet/full.html
