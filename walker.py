import pickle
import pylast
from manager import login
from random import random, choice
from itertools import accumulate
from bisect import bisect
import os
import time
from glob import glob
import curses
import pyprind

class Walker(object):
    def __init__(self):
        self.network = login()
        self.walk_data = None
        self.walk_filename = None

    def __repr__(self):
        return 'Walk data:\n\t' + '; '.join(str(artist) for artist in self.walk_data)

    def __iter__(self):
        return iter(self.walk_data)

    def new_name(self, base):
        strtime = time.strftime('%y-%m-%d--%H-%M-%S')
        return 'data/' + base + strtime + '.p'

    def load_walk(self, filename=None, duplicate=False):
        if filename is None:
            old_walks = glob('data/' + self.__class__.__name__.lower() + '*.p')
            if len(old_walks) == 0:
                filename = self.new_name(self.__class__.__name__.lower())
            else:
                filename = sorted(old_walks)[-1]    # get newest walk
        def new_walk():
            while True:
                try:
                    ans = input('Do you wish to create a new walk ([y]/n)? ')
                    if ans == 'y' or ans == '':
                        self.walk_data = [self.seed]
                        self.walk_filename = filename
                        with open(filename, 'wb') as f:
                            pickle.dump(self.walk_data, f)
                        break
                    elif ans == 'n':
                        break
                except KeyboardInterrupt:
                    break
        try:
            with open(filename, 'rb') as f:
                self.walk_data = pickle.load(f)
                if duplicate:
                    path, ext = os.path.splitext(filename)
                    new_filename = self.new_name(self.__class__.__name__.lower())
                    with open(new_filename, 'wb') as f:
                        pickle.dump(self.walk_data, f)
                        self.walk_filename = new_filename
                else:
                    self.walk_filename = filename
        except EOFError:
            print('The walk data appears to be empty or damaged.')
            new_walk()
        except IOError:
            raise
            print("Could not find '{}'.".format(filename))
            new_walk()

    def walk_forever(self, autosave=True):
        # todo: curses
        if self.walk_data is None:
            print('Please first load/create walk data to walk forever.')
        else:
            try:
                while True:
                    self.walk_data.append(self.step())
                    if autosave:
                        with open(self.walk_filename, 'wb') as f:
                            pickle.dump(self.walk_data, f)
            except KeyboardInterrupt:
                print('\nNumber of steps in walk: {}'.format(len(self.walk_data)))
            except:
                print('\nNumber of steps in walk: {}'.format(len(self.walk_data)))
                raise

    def gather_tags(self, filename=None, outfile=None, autosave=True, show=False):
        if filename is None:
            filename = self.walk_filename
            if self.walk_data is None:
                print('No walk data found')
                return
        if outfile is None:
            old_tags = glob('data/tag_data*.p')
            if len(old_tags) == 0:
                outfile = 'data/tag_data' + self.walk_filename[-20:-2] + '.p'
                tag_data = []
                print('New file created: {}'.format(outfile))
            else:
                outfile = sorted(old_tags)[-1]    # get newest tag data
                with open(outfile, 'rb') as f:
                    tag_data = pickle.load(f)
                print('Tag data loaded: {}'.format(self.walk_filename[-20:-2]))
                if show:
                    artist, tags = tag_data[-1]
                    print('Last gathered: {} {}'.format(artist, [str(t.item) for t in tags[:3]]))
        pbar = pyprind.ProgPercent(len(self.walk_data) - len(tag_data))
        print('{} artists left.'.format(len(self.walk_data) - len(tag_data)))
        try:
            if autosave:
                print('Autosave feature is active...')
            for artist in self.walk_data[len(tag_data):]:
                tags = artist.get_top_tags(limit=100)
                tag_data.append((artist, tags))
                if autosave:
                    with open(outfile, 'wb') as f:
                        pickle.dump(tag_data, f)
                pbar.update()
        except:
            with open(outfile, 'wb') as f:
                pickle.dump(tag_data, f)
            print('\nJust finished with {} {}'.format(artist, [str(t.item) for t in tag_data[-1][1][:3]]))

class MDWalker(Walker):
    def __init__(self, seed=None):
        super().__init__()
        self.max_degree = 100
        if seed is None:
            self.seed = self.network.search_for_artist('john coltrane').get_next_page()[0]
        else:
            self.seed = seed

    def step(self, index=-1, back_prob=0.1):
        if random() < back_prob:
            last = choice(self.walk_data)
        else:
            last = self.walk_data[index]
        print(last)
        similar = [ti.item for ti in last.get_similar(limit=self.max_degree)]     # max degree is 250 by Last.fm construction
        if len(similar) == self.max_degree:
            return choice(similar)
        elif len(similar) == 0:
            return self.step(index=-2)
        else:
            weights = [1/len(similar) for _ in range(len(similar))]
            similar.append(last)
            weights.append(1 - len(similar)/self.max_degree)
            cumdist = list(accumulate(weights))
            return similar[bisect(cumdist, random()*cumdist[-1])]

if __name__ == '__main__':
    md = MDWalker()
    md.load_walk(duplicate=False)
    md.walk_forever(autosave=True)
    # md.gather_tags(show=True)


