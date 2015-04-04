import plistlib
import pickle
from time import strftime, localtime
import os
from fuzzywuzzy import process
from digger import LastFMDigger
from datetime import datetime


class cd(object):
    def __init__(self, new_path):
        self.saved_path = os.getcwd()
        self.new_path = os.path.expanduser(new_path)
    def __enter__(self):
        os.chdir(self.new_path)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

class iTunesLibrary(object):
    def __init__(self, refresh=False):
        if refresh:
            self.reload_lib()
        else:
            try:
                save_time, saved_lib = pickle.load(open('saved_lib.pkl', 'rb'))
                print('Loaded iTunes library from ', save_time)
                self.lib = saved_lib
            except IOError:
                print('No pickled iTunes library file found.')
                self.reload_lib()

    def reload_lib(self):
        print("Parsing iTunes library...")
        with cd('~/Music/iTunes'):
            with open('iTunes Music Library.xml', 'rb') as f:
                save_time = strftime("%a, %d %b %y %I:%M:%S %p", localtime())
                self.lib = plistlib.load(f)
        pickle.dump((save_time, self.lib), open('saved_lib.pkl', 'wb'))
        print('done!')

    def query_playlists(self, query=None, limit=4, interactive=False):
        if query is None:
            query = input("playlist query: ")
        playlists = [p['Name'] for p in self.lib['Playlists']]
        matches = [m[0] for m in process.extract(query, playlists, limit=limit)]
        results, indices = zip(*((m, playlists.index(m)) for m in matches))
        if interactive:
            for i, r in enumerate(results):
                print("[{}]\t{}".format(i, r))
            pick_index = int(input("select index: "))
        else:
            pick_index = 0
        return self.lib['Playlists'][indices[pick_index]]

    def print_playlist(self, playlist, interactive=False):
        plist_result = self.query_playlists(playlist, interactive)
        print(plist_result['Name'])
        for artist, track in self.playlist_items(plist_result):
            print(artist, track)

    def playlist_items(self, playlist):
        track_ids = [e['Track ID'] for e in playlist['Playlist Items']]
        tracks = [self.lib['Tracks'][str(tid)] for tid in track_ids]
        return ((t['Artist'], t['Name']) for t in tracks)

    # def scrobble_playlist(self, playlist, interactive=False):
    #     digger = LastFMDigger()
    #     for artist, track in self.playlist_items(self.query_playlists(playlist, interactive=interactive)):
    #         print('scrobbling {} - {}'.format(artist, track))
    #         timestamp = datetime.now().strftime('%s')
    #         digger.network.scrobble(artist, track, timestamp)


if __name__ == '__main__':
    lib = iTunesLibrary(refresh=False)
    # lib.scrobble_playlist('beetz')
    lib.print_playlist('beetz')

