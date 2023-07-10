from data import *

'''
Purpose of this is to do the basic conversion of csv to player pb progression.
Will try and rename this to something better when I can think of it lmao.
'''

def get_distinct_sheet_headers(name):
    # for given gid, get unique files
    # for each unique revision, check headers, see when new one is added
    leaderboards = get_leaderboards()
    board = leaderboards[name]
    i = 0
    for interval in board:
        sheet_id = interval['gid']
        start, end = interval['start'], interval['end']
        unique_revs = get_unique_revs(sheet_id)
        dirty_revs = get_dirty_revs(sheet_id)
        last_headers = []
        for rev in unique_revs:
            if rev < start:
                continue
            if rev > end:
                break
            if rev in dirty_revs:
                continue
            headers = get_rev_csv(sheet_id, rev)[0]
            if headers != last_headers:
                print(f'{i}: {sheet_id}-{rev} changes to\n{headers}')
                last_headers = headers
            i += 1

if __name__ == '__main__':
    get_distinct_sheet_headers('NTSC 0-19 Score')
