"""
define artists as documents 
    although we could use songs, they have less tags on average. in fact it would be interesting to draw out the distributions on uniform random samples of each.
perhaps change all tags to lowercase, and remove punctuation?
    a closer inspection should be made to what tweaks should be made on the tags, by looking at a large variety of them and noticing patterns by hand
remove tags that only appear once in the whole corpus of documents
    what's the equivalent of a stop list?

"""

import pickle
import numpy as np
from math import log2       # lookup difference between from importing vs. not, efficiency
from scipy.linalg import svd
import matplotlib.pyplot as plt; plt.style.use('ggplot')
from sklearn.decomposition import TruncatedSVD

with open('walker_data/tag_data15-02-08--16-34-35.p', 'rb') as f:
    tag_data = pickle.load(f)

class LSA(object):
    def __init__(self, tag_data):
        self.tag_data = tag_data[::100]

    def term_doc(self):
        """ this creates a term-document matrix
        for now, this function only creates tf-idf weights """
        # convert tag_data to artist, dictionary pair for O(1) lookup
        # divide by 100 per weight, to make it normalized in [0, 1]
        def safe_weight(tag):
            try:
                return int(t.weight)/100
            except:
                return 1.0
        tag_sets = [(str(artist), {str(t.item): safe_weight(t) \
            for t in tags[:8]}) for artist, tags in self.tag_data]
        # print(tag_sets)
        # get list of unique tags for row listing; convert to list for ordering
        # possibly use OrderedSet here for lack of variety, in listing
        uniq_tags = list(set.union(*(set(tags.keys()) for _, tags in tag_sets)))
        self.term_labels = uniq_tags
        self.doc_labels = [artist for artist, _ in tag_sets]
        # print(self.term_labels)
        # print(self.doc_labels)
        # possibly used labeled array, or sparse in the future
        nterms, ndocs = len(uniq_tags), len(tag_sets)
        # print('number of unique terms: {}'.format(nterms))
        term_doc = np.zeros((nterms, ndocs))
        for i, t in enumerate(uniq_tags):
            for j, (_, tags) in enumerate(tag_sets):
                term_doc[i, j] = tags.get(t, 0)     # get the normalized Last.fm weights, i.e. document norm tf
        # apply the idf weights
        # print(term_doc)
        for (i, j), _ in np.ndenumerate(term_doc):
            term_doc[i, j] *= log2(ndocs/(1 + term_doc[i, j]))
        self.term_doc = term_doc
        print(term_doc.shape)
        return term_doc

    def scatter2d(self):
        u, s, v = svd(self.term_doc)
        x, y = zip(*-u[:, 0:2])    # skip first dimension
        areas = 3.14*20*np.array(list(map(np.linalg.norm, zip(x, y))))
        print(areas)
        plt.scatter(x, y, s=areas)
        for label, xx, yy in zip(self.term_labels, x, y):
            if np.linalg.norm([xx, yy]) > 0.12:
                plt.annotate(
                    label, 
                    xy = (xx, yy), xytext = (-12, 12),
                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                    bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        plt.show()

    def reduce_dim(self, k):
        svd = TruncatedSVD(n_components=k)
        reduced = svd.fit_transform(self.term_doc)
        print(reduced)
        distances = np.dot(reduced, np.transpose(reduced))
        pairs = [((self.term_labels[i], self.term_labels[j]), distances[i, j]) for i, j in zip(*np.triu_indices(len(distances), 1))]
        top = sorted(pairs, key=lambda x: x[1])
        for pair, weight in top[-20:]:
            print(pair, weight)

    def test(self, k=3):
        # print(self.term_doc)
        x = np.array([[1,0,1,0,0,0],[0,1,0,0,0,0],[1,1,0,0,0,0],
            [1,0,0,1,1,0],[0,0,0,1,0,1]])
        u, s, v = svd(x, full_matrices=False)
        print(u)
        s[2:] = 0
        print(np.diag(s))
        print(v)
        a = np.dot(u, np.dot(np.diag(s), v))
        print(a)

if __name__ == '__main__':
    l = LSA(tag_data)
    l.term_doc()
    # l.test()
    x = l.reduce_dim(20)
    # print(x)
    # l.scatter2d()



