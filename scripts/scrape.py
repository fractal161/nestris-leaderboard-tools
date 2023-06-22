import gzip
import json
from http import cookiejar
import requests
from timeit import default_timer as timer
from dotenv import dotenv_values

env = dotenv_values(".env")

sheet_id = '1ZBxkZEsfwDsUpyire4Xb16er36Covk7nhR8BN_LPodI'

# is the old gid 1516944123?


def get_revs():
    cj = cookiejar.MozillaCookieJar('data/cookies.txt')
    cj.load()
    for i in range(1, 39067):
        start = timer()
        print(f'Fetching revision {i}')
        rev_url = f'https://docs.google.com/spreadsheets/u/0/d/{env["SHEET_ID"]}/revisions/show?rev={i}&gid={env["GID"]}'
        timeout = 30
        while True:
            try:
                r = requests.get(rev_url, cookies=cj, timeout=timeout)
                break
            except:
                print('Timed out, retrying connection')
                timeout += 5

        end = timer()
        print(f'Took {end - start:.2f} seconds')

        with open(f'data/rev-{i}.html.gz', 'wb') as f:
            f.write(gzip.compress(r.content))

def get_tiles():
    cj = cookiejar.MozillaCookieJar('data/cookies.txt')
    cj.load()
    max_rev = 39067
    while max_rev > 1:
        start = timer()
        print(f'Revisions before {max_rev}')
        tile_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/revisions/tiles?end={max_rev}&revisionBatchSize=1500&showDetailedRevisions=true&token={env["TOKEN"]}'
        timeout = 30
        while True:
            try:
                r = requests.get(tile_url, cookies=cj, timeout=timeout)
                break
            except:
                print('Timed out, retrying connection')
                timeout += 5
        end = timer()
        print(f'Took {end - start:.2f} seconds')
        # get full interval
        info = json.loads(r.text.split('\n')[1])
        min_rev = info['firstRev']
        with open(f'data/timestamps/{min_rev}-to-{max_rev}.json', 'w') as f:
            f.write(json.dumps(info, indent=2))
        max_rev = min_rev - 1

get_tiles()
