curl -F "("Hillary Clinton" OR "Hillary" OR "Clinton") NOT ("Donald Trump" OR "Trump")"              \                                      \
 -F "language[]=en"                                                                              \
 -F "sort_by=published_at.start=NOW-60DAYS"                                                      \
 -F "sort_by=published_at.end=NOW-1DAY"                                                          \
 -F "field=sentiment.title.polarity                                                              \
 https://api.newsapi.aylien.com/api/v1/trends                                                    \