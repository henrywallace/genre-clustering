import pylast
import time
import pickle

def get_doc_term(artists, filename, attempts=50):
    docs = []
    ntags_dist = []
    for i, a in enumerate(artists):
        print(i, a, end=' ')
        for _ in range(attempts):
            try:
                tags = {t.item: t.weight for t in a.get_top_tags()}
                docs.append((a, tags))
                ntags_dist.append(len(tags))
                print(len(tags))
            except Exception as e:
                print(e)
                print('Waiting 5 seconds...')
                time.sleep(5)
                continue
            break
    with open(filename, 'wb') as f:
        pickle.dump((docs, ntags_dist), f)
    return docs, ntags_dist

with open('walk_additions.pkl', 'rb') as f:
    artists, _ = pickle.load(f)
    get_doc_term(artists, 'document_additions.pkl')