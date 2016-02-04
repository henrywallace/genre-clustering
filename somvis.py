from tagslda2 import TagsLDA
from scipy.stats import entropy as divergence
from som import SOM
import matplotlib.pyplot as plt
import numpy as np

def main():
	# FIT THE LDA
	lda = TagsLDA(skip=10)
	theta, beta = lda.train(ntopics=30, niter=300, seed=42)

	# TRAIN THE SOM
	dist_func = lambda p, q: divergence(p, q)
	som = SOM(grid_shape=(20, 20), ndims=lda.nterms, dist_func=dist_func)		# len(dictionary) = len(dictionary.token2id)
	som.train(lda.beta, nepochs=10)
	
	# PLOT
	labels = [lda.topic_representatives(i, topn=3, show_scores=False) for i in range(lda.ntopics)]
	areas = np.array([30*2*np.pi*score**2 for score in lda.topic_significances()])
	areas_top, top_indices = zip(*sorted([(a, i) for i, a in enumerate(areas)], reverse=True)[:10])
	locations = som.get_locations(vecs=lda.beta[top_indices, :], labels=labels)

	# print(locations)
	labels, data = zip(*locations.items())
	x, y = zip(*data)
	plt.scatter(x, y, s=areas_top, alpha=0.5)
	for l, x, y in zip(labels, x, y):
		plt.annotate(l, xy=(x, y), textcoords='offset points', xytext=(0, 20), horizontalalignment='center')
	plt.show()		


if __name__ == '__main__':
	main()