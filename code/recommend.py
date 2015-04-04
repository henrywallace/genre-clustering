import argparse
import csv
import pylast
from datetime import datetime
from random import sample
import webbrowser

""" NOTES
...
"""

parser = argparse.ArgumentParser(description='Command-line tool for song recommendations')
parser.add_argument('-i', '--interactive', dest='interactive', action='store_true', help='interactive')
parser.add_argument('-t', '--tracks', dest='tracks', nargs='+', help='recommendations for track')
parser.add_argument('-f', '--friends', dest='friends', action='store_true', help='get friend recommendations')
parser.add_argument('-s', '--show', dest='show', type=int, default=3)
parser.add_argument('-l', '--limit', dest='limit', type=int, default=20)
parser.add_argument('-w', '--website', dest='website', action='store_true', help='open user page in browser')

args = parser.parse_args()

# read login details from login.txt
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
        '\tAPI_SECRET:\t<your api_secret>\n')
    exit()

# login into Last.fm, to scrobble
network = pylast.LastFMNetwork(username=login['USERNAME'],
    password_hash=pylast.md5(login['PASSWORD']),
    api_key=login['API_KEY'], api_secret=login['API_SECRET'])
timestamp = datetime.now().strftime('%s')


if args.tracks is not None:
    track_choices = []
    for t in args.tracks:
        results = network.search_for_track('', t).get_next_page()
        if args.interactive:
            print("Results for '{}'".format(t))
            for i, r in enumerate(results[:min(4, len(results))]):
                print('[{}]\t{}'.format(i, r))
            pick_index = int(input('select index: '))
        else:
            pick_index = 0
        track_choices.append(results[pick_index])
    # gather tag data
    # similar = set(track_choices)
    similar = []
    print(args.limit)
    print(args.show)
    for t in track_choices:
        print('Gathering similar tracks for {}...'.format(t.get_name()))
        similar.append([s.item for s in t.get_similar(limit=args.limit)])
    share = list(set.intersection(*map(set, similar)))
    print('SHARED SIMILAR TRACKS:')
    recommendations = sample(share, min(args.show, len(share)))
    for t in recommendations:
        print('  •', t)

if args.website:
    for t in recommendations:
        webbrowser.open(t.get_url())

if args.friends:
    friends = sample(network.get_user(login['USERNAME']).get_friends(), 4)
    loved = []
    for f in friends:
        loved += [x.track for x in f.get_loved_tracks()]
    choices = sample(loved, args.limit)
    for t in choices:
        print('  •', t)



