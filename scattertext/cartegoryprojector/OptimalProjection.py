import numpy as np
from sklearn.decomposition import PCA

from scattertext.Scalers import stretch_0_to_1
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.cartegoryprojector.CategoryProjector import CategoryProjector
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor


def get_optimal_category_projection(
        corpus,
        n_dims=3,
        n_steps=10,
        projector=lambda n_terms, n_dims: CategoryProjector(AssociationCompactor(n_terms, scorer=RankDifference),
                                                            projector=PCA(n_dims)),
        verbose=False
    ):
    try:
        from astropy.stats import RipleysKEstimator
    except:
        raise Exception("Please install astropy")

    ripley = RipleysKEstimator(area=1., x_max=1., y_max=1., x_min=0., y_min=0.)
    min_dev = None
    best_k = None
    best_x = None
    best_y = None
    best_projector = None
    for k in np.power(2, np.linspace(np.log(corpus.get_num_categories()) / np.log(2),
                                     np.log(corpus.get_num_terms()) / np.log(2), n_steps)).astype(int):
        r = np.linspace(0, np.sqrt(2), 100)
        category_projector = projector(k, n_dims)
        category_projection = category_projector.project(corpus)
        for dim_1 in range(0, n_dims):
            for dim_2 in range(dim_1 + 1, n_dims):
                proj = category_projection.projection[:, [dim_1, dim_2]]
                scaled_proj = np.array([stretch_0_to_1(proj.T[0]), stretch_0_to_1(proj.T[1])]).T
                dev = np.sum(np.abs(ripley(scaled_proj, r, mode='ripley') - ripley.poisson(r)))
                if min_dev is None or dev < min_dev:
                    min_dev = dev
                    best_k = k
                    best_projector = category_projector
                    best_x, best_y = (dim_1, dim_2)
                if verbose:
                    print(k, dim_1, dim_2, dev, best_k, best_x, best_y, min_dev)
    if verbose:
        print(best_k, best_x, best_y)
    return best_projector.project(corpus, best_x, best_y)
