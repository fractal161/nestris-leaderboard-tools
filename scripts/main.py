from data import *
from diff import diffSheets

'''
Purpose of this is to do the basic conversion of csv to player pb progression.
Will try and rename this to something better when I can think of it lmao.
'''

def print_distinct_sheet_headers(name):
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
            headers = get_rev_as_list(sheet_id, rev)[0]
            if headers != last_headers:
                print(f'{i}: {sheet_id}-{rev} changes to\n{headers}')
                last_headers = headers
            i += 1

def print_unusual_revs(id, hide_explained=True):
    revs = get_clean_revs(id)
    i = 0
    for rev1, rev2 in zip(revs[:-1], revs[1:]):
        if hide_explained:
            continue
        if not is_diff_normal(id, rev1, rev2):
            print(f'{i}:', rev1, rev2)
            i += 1

# checks if diff is manually overriden or satisfies heuristics
def is_diff_normal(id: str, rev1: int, rev2: int):
    overrides = get_diff_overrides(id)
    for override in overrides:
        if override['start'] == rev1 and override['end'] == rev2:
            return True
    sheet1 = get_rev_as_list(id, rev1)
    sheet2 = get_rev_as_list(id, rev2)
    diff = diffSheets(sheet1, sheet2)
    if len(diff['added']) > 0 and len(diff['removed']) > 0:
        return False
    return True

def get_diff_from_override(override):
    return dict(
        added=override['added'],
        removed=override['removed'],
        moved=override['moved'],
        modified=override['modified']
    )


# from the diff object, return list of pairs, where each pair contains the
# corresponding indices. None on either side implies an add or remove
def get_row_map(len1, len2, diff):
    row_map = []
    old_moved, new_moved = (), ()
    if len(diff['moved']) > 0:
        old_moved, new_moved = zip(*diff['moved'])
    old_mod, new_mod = (), ()
    if len(diff['modified']) > 0:
        old_mod, new_mod = zip(*diff['modified'])
    old_map = old_moved + old_mod
    new_map = new_moved + new_mod
    added = diff['added']
    removed = diff['removed']
    index1, index2 = 0, 0
    while index1 < len1 or index2 < len2:
        if index1 in removed:
            while index1 in removed:
                row_map.append((index1, None))
                index1 += 1
        elif index2 in added:
            while index2 in added:
                row_map.append((None, index2))
                index2 += 1
        elif index1 in old_map:
            pos = old_map.index(index1)
            row_map.append((index1, new_map[pos]))
            index1 += 1
        else:
            while index2 in new_map:
                index2 += 1
            if index2 < len2:
                row_map.append((index1, index2))
                index1 += 1
                index2 += 1
    assert index1 == len1 and index2 == len2
    return row_map

def print_distinct_names(id):
    revs = get_clean_revs(id)
    special = get_clean_unusual_revs(id)
    players = set()
    for rev in revs:
        if rev in special:
            continue
        df = get_rev_as_df(id, rev)
        for player in df['name'].dropna():
            if player not in players:
                print(f'{rev}: {player}')
                players.add(player)
    print(len(players), 'total names')

if __name__ == '__main__':
    # print_distinct_sheet_headers("NTSC 0-19 Score")
    # df = get_rev_as_df("1078039113", 3799)
    #print_unusual_revs("1516944123", hide_explained=False)
    #print_unusual_revs("1078039113", hide_explained=False)
    sheet1 = get_rev_as_list('1078039113', 31271)
    sheet2 = get_rev_as_list('1078039113', 31273)
    overrides = get_diff_overrides('1078039113')
    #diff = diffSheets(sheet1, sheet2)
    diff = get_diff_from_override(overrides[1])
    print(diff)
    print(get_row_map(len(sheet1), len(sheet2), diff))
