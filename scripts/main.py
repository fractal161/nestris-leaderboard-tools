from data import *
from diff import diffSheets

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
    id = "1516944123"
    revs = get_clean_revs(id)
    special = get_clean_unusual_revs(id)
    i = 0
    for rev1, rev2 in zip(revs[:-1], revs[1:]):
        if rev1 in special and rev2 in special:
            continue
        sheet1 = get_rev_csv(id, rev1)
        sheet2 = get_rev_csv(id, rev2)
        diff = diffSheets(sheet1, sheet2)
        if len(diff['added']) > 1 or len(diff['removed']) > 1:
            print(f'{i}:', rev1, rev2)
            i += 1
