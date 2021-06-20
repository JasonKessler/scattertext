import numpy as np
import pandas as pd
"""
seed_mat = np.matrix([model.wv[word] for word in pos_seeds + neg_seeds])
term_mat = np.matrix([model.wv[word] for word in model.wv.vocab])
seed_norm = np.matrix(np.linalg.norm(seed_mat, axis=1))
term_norm = np.matrix(np.linalg.norm(term_mat, axis=1))
cosine_mat = (((seed_mat * term_mat.T).T/seed_norm)/term_norm.T)
polarity_mat = np.matrix([1/len(pos_seeds)] * len(pos_seeds) + [-1/len(neg_seeds)] * len(neg_seeds))
term_scale = (cosine_mat * polarity_mat.T).A1
"""

def latent_semantic_scale_from_word2vec(model,
                                        pos_seed_words=None,
                                        neg_seed_words=None,
                                        seed_words=None,
                                        seed_values=None,):
    terms = [word for word in model.wv.key_to_index.keys()]
    embeddings = np.matrix([model.wv[word] for word in model.wv.key_to_index.keys()])
    return lss_terms(embeddings, terms, pos_seed_words, neg_seed_words, seed_words, seed_values)


def lss_terms(embeddings,
              terms,
              pos_seed_words=None,
              neg_seed_words=None,
              seed_words=None,
              seed_values=None):
    neg_seed_words = [] if neg_seed_words is None else neg_seed_words
    pos_seed_words = [] if pos_seed_words is None else pos_seed_words
    seed_words = [] if seed_words is None else seed_words
    seed_values = [] if seed_values is None else seed_values
    for word, value in zip((pos_seed_words + neg_seed_words), [1] * len(pos_seed_words) + [-1] * len(neg_seed_words)):
        seed_words.append(word)
        seed_values.append(value)

    assert seed_values
    assert embeddings.shape[0] == len(terms)
    assert len(seed_words) == len(seed_values)
    assert len(set(seed_words) & set(terms)) == len(seed_words)

    term2i = {term:i for i, term in enumerate(terms)}
    seed_mat = embeddings[[term2i[term] for term in seed_words],:]

    seed_norm = np.matrix(np.linalg.norm(seed_mat, axis=1))
    term_norm = np.matrix(np.linalg.norm(embeddings, axis=1))

    cosine_mat = (((seed_mat * embeddings.T).T/seed_norm)/term_norm.T)

    return pd.Series((cosine_mat * np.matrix(seed_values).T).A1, index=terms)

