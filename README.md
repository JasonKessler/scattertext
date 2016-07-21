# text-to-ideas
A tool for finding distinguishing terms in small-to-medium-sized corpora

### Unusual Algorithms:
#### Rudder algorithm.
Adapted from Dataclysm. Rudder C (2014) Dataclysm: Who We Are (When We Think No One’s Looking) (Crown, New York).
```math #
\sqrt(Percentile(P(word|category)) + 1 - Percentile(P(word|~category)))
```
#### Kessler algorithm.
 Original.

#### Other: to do.




Sources:
* Political data: scraped from www.nytimes.com/interactive/2012/09/06/us/politics/convention-word-counts.html?_r=0
* count_1w: Peter Norvig assembled this file (downloaded at http://norvig.com/ngrams/count_1w.txt). See http://norvig.com/ngrams/ for an explanation of how it was gathered from a very large corpus.
* hamlet.txt: William Shakespeare. From http://shakespeare.mit.edu/hamlet/full.html