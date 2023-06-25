import sys
import gzip
import json
from http import cookiejar
import os
import requests
from timeit import default_timer as timer
from dotenv import dotenv_values

env = dotenv_values(".env")

def get_revs():
    cj = cookiejar.MozillaCookieJar('data/cookies.txt')
    cj.load()
    start, end = env['REV_START'], env['REV_END']
    assert(start != None and end != None)
    start, end = int(start), int(end)
    for i in range(start, end+1):
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

        if not os.path.exists(f'data/raws/{env["GID"]}'):
            os.makedirs(f'data/raws/{env["GID"]}')
        with open(f'data/raws/{env["GID"]}/{i}.html.gz', 'wb') as f:
            f.write(gzip.compress(r.content))

def get_timestamp_chunks():
    cj = cookiejar.MozillaCookieJar('data/cookies.txt')
    cj.load()
    max_rev = 39067
    while max_rev > 1:
        start = timer()
        print(f'Revisions before {max_rev}')
        tile_url = f'https://docs.google.com/spreadsheets/d/{env["SHEET_ID"]}/revisions/tiles?end={max_rev}&revisionBatchSize=1500&showDetailedRevisions=true&token={env["TOKEN"]}'
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
        with open(f'data/timestamp-chunks/{min_rev}-to-{max_rev}.json', 'w') as f:
            f.write(json.dumps(info, indent=2))
        max_rev = min_rev - 1

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc > 0:
        funcname = sys.argv[1]
        print(funcname)
        if funcname in locals():
            locals()[funcname](*sys.argv[2:])
