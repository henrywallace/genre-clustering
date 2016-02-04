import numpy as np
import matplotlib.pyplot as plt
from random import choice
from pyprind import ProgPercent

def find_factorization(x):
    def loss(x, n, m):
        return 1*abs(x - n*m) + 2*abs(n - m)
    def solve(x):
        (n_min, m_min), loss_min = (None, None), float('inf')
        for n in range(1, x + 1):
            for m in range(n, x + 1):
                fval = loss(x, n, m)
                if fval < loss_min and x <= n*m:
                    (n_min, m_min), loss_min = (n, m), fval
        return (n_min, m_min)
    return solve(x)

class SOM(object):
    def __init__(self, grid_shape=(10, 10), ndims=3, dist_func=None):
        self.grid_shape = grid_shape       
        self.ndims = ndims
        self.grid = self.rand_grid()
        self.t = 0
        self.history = [self.grid.copy()]
        self.nepochs = None
        if dist_func is None:
            self.dist_func = lambda x, y: np.linalg.norm(np.subtract(x, y))
        else:
            self.dist_func = dist_func

    def rand_node(self):
        vec = np.random.rand(self.ndims)       # so that neurons are very small
        return vec/vec.sum()

    def rand_grid(self):
        grid_width, grid_height = self.grid_shape
        nodes = np.zeros((grid_width, grid_height, self.ndims))
        for i, j in np.ndindex(self.grid_shape):
            nodes[i, j] = self.rand_node()
        return nodes

    def plot_history(self):
        nrows, ncols = find_factorization(len(self.history))
        fig, axes = plt.subplots(nrows, ncols)
        for i, ax in enumerate(np.reshape(axes, -1)):
            if i < len(self.history):
                ax.imshow(self.history[i], interpolation='nearest')       
                # ax.set_title('iteration {}'.format(i))        
            ax.axis('off') 
        plt.show()

    def learn_weight(self):
        lrn0 = 0.005
        return lrn0**(self.t/self.nepochs)

    def neighbor_weight(self, ind_winner, ind_other):
        sig0, tau0 = max(self.grid_shape)/5, 10
        sigma = sig0 * np.exp(-self.t/tau0)
        dist = np.linalg.norm(np.subtract(ind_winner, ind_other))
        return self.learn_weight() * np.exp(-dist**2 / (2 * sigma**2))

    def update_grid(self, input_vec):
        ind_min, dist_min = (0, 0), float('inf')
        for ind in np.ndindex(self.grid_shape):
            dist = self.dist_func(self.grid[ind], input_vec)
            if dist < dist_min:
                ind_min, dist_min = ind, dist
        for ind in np.ndindex(self.grid_shape):
            neuron = self.grid[ind]
            dist = np.subtract(input_vec, neuron)
            delta = self.neighbor_weight(ind_min, ind) * dist
            self.grid[ind] += delta

    def train(self, train_vecs, nepochs=10, save_history=False):
        print('starting training...')
        pbar = ProgPercent(nepochs*len(train_vecs))
        self.nepochs = nepochs
        for _ in range(nepochs):
            for vec in train_vecs:
                self.update_grid(vec)
                pbar.update()
            self.t += 1
            if save_history:
                self.history.append(self.grid.copy())
        print('done')

    def get_locations(self, vecs, labels=None):
        print('getting locations...')
        pbar = ProgPercent(len(vecs)*np.prod(self.grid_shape))
        locations = {}
        for i, v in enumerate(vecs):
            ind_min, dist_min = (0, 0), float('inf')
            for ind in np.ndindex(self.grid_shape):
                dist = self.dist_func(self.grid[ind], v)
                if dist < dist_min:
                    ind_min, dist_min = ind, dist
                pbar.update()
            if labels is None:
                locations[i] = ind_min
            else:
                locations[labels[i]] = ind_min
        print('done')
        return locations


if __name__ == '__main__':
    # som = SOM(ndims=3, grid_shape=(20, 20))
    # train_vecs = np.random.rand(8, som.ndims)
    # plt.figure(1)
    # plt.imshow(train_vecs.reshape(1, 8, som.ndims), interpolation='nearest')
    # som.train(train_vecs, nepochs=10)
    # som.plot_history()    
    pass






