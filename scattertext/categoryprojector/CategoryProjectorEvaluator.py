import scipy

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from scattertext.Scalers import stretch_0_to_1
from scattertext.categoryprojector.CategoryProjection import CategoryProjection


class CategoryProjectionEvaluator(object):
    def evaluate(self, category_projection):
        raise NotImplementedError()


class RipleyKCategoryProjectorEvaluator(CategoryProjectionEvaluator):
    def __init__(self, max_distance=np.sqrt(2)):
        self.max_distance = max_distance

    def evaluate(self, category_projection):
        assert type(category_projection) == CategoryProjection
        try:
            from astropy.stats import RipleysKEstimator
        except:
            raise Exception("Please install astropy")

        ripley_estimator = RipleysKEstimator(area=1., x_max=1., y_max=1., x_min=0., y_min=0.)
        proj = category_projection.projection[:, [category_projection.x_dim, category_projection.y_dim]]
        scaled_proj = np.array([stretch_0_to_1(proj.T[0]), stretch_0_to_1(proj.T[1])]).T
        radii = np.linspace(0, self.max_distance, 1000)
        deviances = np.abs(ripley_estimator(scaled_proj, radii, mode='ripley') - ripley_estimator.poisson(radii))
        return np.trapz(deviances, x=radii)


class EmbeddingsProjectorEvaluator(CategoryProjectionEvaluator):
    def __init__(self, get_vector):
        self.get_vector = get_vector
        #import spacy
        #assert issubclass(type(nlp), spacy.language.Language)
        #self.nlp = nlp
        #self.vector_func = lambda: nlp(x)[0].vector

    def evaluate(self, category_projection):
        assert type(category_projection) == CategoryProjection
        topics = category_projection.get_nearest_terms()
        total_similarity = 0
        for topic in topics.values():
            topic_vectors = np.array([self.get_vector(term) for term in topic])
            import pdb; pdb.set_trace()
            sim_matrix = cosine_similarity(topic_vectors)
            tril_sim_matrix = np.tril(sim_matrix)
            mean_similarity = tril_sim_matrix.sum()/(tril_sim_matrix.shape[0] ** 2 - tril_sim_matrix.shape[0]) / 2
            total_similarity += mean_similarity
        return total_similarity/len(topics)