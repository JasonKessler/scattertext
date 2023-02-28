import abc

import numpy as np

from scattertext.TermDocMatrix import TermDocMatrix


class CategoryEmbedderABC:
    @abc.abstractmethod
    def embed_categories(self, corpus: TermDocMatrix) -> np.array:
        pass
