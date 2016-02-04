import argparse
import pylast
from itunes import iTunesLibrary
from datetime import datetime
import csv
import webbrowser

""" NOTES
Clean-up args.interactive for each section. Make it possible to scrobble
multiple tracks by including quotes or some other division syntax per track
entry. Clean-up Last.fm login to include an authentication login scheme and
make this part of itunes.py. 
"""

parser = argparse.ArgumentParser(description='Command-line tool for manual scrobbling.')
parser.add_argument('-i', '--interactive', dest='interactive', action='store_false', help='turn interactive off')
parser.add_argument('-w', '--website', dest='website', action='store_true', help='open user page in browser.')
parser.add_argument('-d', '--display', dest='display', type=int, default=7, help='number of displayed results.')

parser.add_argument('-p', '--playlist', dest='playlist', nargs='+', help='iTunes playlist query.')
parser.add_argument('-t', '--track', dest='track', nargs='+', help='track query')
parser.add_argument('-a', '--albums', dest='album', nargs='+', help='album query')


args = parser.parse_args()

# read login details from lastfm-login.csv
login = {}
try:
    with open('lastfm-login.csv', newline='') as f:
        reader = csv.reader(f, delimiter=':', quoting=csv.QUOTE_NONE, skipinitialspace=True)
        for key, val in reader:
            login[key.upper()] = val
except IOError:
    print('Please save you login details to a txt file in the following csv format:\n'
        '\tUSERNAME:\t<your username>\n'
        '\tPASSWORD:\t<your password>\n'
        '\tAPI_KEY:\t<your api_key>\n'
        '\tAPI_SECRET:\t<your api_secret\n')
    exit()

# login into Last.fm, to scrobble
network = pylast.LastFMNetwork(username=login['USERNAME'],
    password_hash=pylast.md5(login['PASSWORD']),
    api_key=login['API_KEY'], api_secret=login['API_SECRET'])
timestamp = datetime.now().strftime('%s')

if args.playlist is not None:
    lib = iTunesLibrary()
    p = ' '.join(args.playlist) 
    if args.interactive: print("Results for '{}':".format(p))
    choice = lib.query_playlists(p, interactive=args.interactive, limit=args.display)
    for artist, track in lib.playlist_items(choice):
        if args.interactive: print('scrobbling {} - {}'.format(artist, track))
        network.scrobble(artist, track, timestamp)

if args.track is not None:
    for t in args.track:
        results = network.search_for_track('', t).get_next_page()
        if args.interactive is not None:
            print('Results for {}:'.format(t))
            for i, r in enumerate(results[:min(args.display, len(results))]):
                print('[{}]\t{}'.format(i, r))
            pick_index = int(input("select index: "))
        else:
            pick_index = 0
        artist = str(results[pick_index].get_artist())
        track = str(results[pick_index].get_name())
        print('scrobbling {} - {}'.format(artist, track))
        network.scrobble(artist, track, timestamp)

if args.album is not None:
    for a in args.album:
        results = network.search_for_album(a).get_next_page()
        if args.interactive:
            print('Results for {}:'.format(a))
            for i, r in enumerate(results[:min(args.display, len(results))]):
                print('[{}]\t{}'.format(i, r))
            pick_index = int(input("select index: "))
        else:
            pick_index = 0
        album = results[pick_index]
        for t in album.get_tracks():
            artist = str(t.get_artist())
            track = str(t.get_name())
            print('scrobbling {} - {}'.format(artist, track))
            network.scrobble(artist, track, timestamp)

if args.website:
    webbrowser.open('http://www.last.fm/user/{}/tracks'.format(login['USERNAME']))