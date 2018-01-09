from lightning.classification import CDClassifier
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.manifold import TSNE
from sklearn.metrics import f1_score
import scattertext as st
from scattertext import SampleCorpora
TfidfTransformer
convention_df = SampleCorpora.ConventionData2012.get_data()


tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)


file_name = "demo_tsne.html"
open(file_name, 'wb').write(html.encode('utf-8'))
print("open " + file_name)
