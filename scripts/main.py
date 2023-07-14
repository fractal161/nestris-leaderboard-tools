from collections import defaultdict

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

def print_unusual_revs(id, hide_explained=False):
    revs = get_clean_revs(id)
    i = 0
    for rev1, rev2 in zip(revs[:-1], revs[1:]):
        # TODO this is clearly wrong?
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
def get_row_map(id, rev1, rev2):
    sheet1 = get_rev_as_list(id, rev1)
    sheet2 = get_rev_as_list(id, rev2)
    len1, len2 = len(sheet1), len(sheet2)
    overrides = get_diff_overrides(id)
    is_override = False
    diff = {}
    for override in overrides:
        if override['start'] == rev1 and override['end'] == rev2:
            diff = get_diff_from_override(override)
            is_override = True
    if not is_override:
        diff = diffSheets(sheet1, sheet2)
    # MAIN IDEA: any index not explicitly mentioned in the diff is moved,
    # and the order in which these come is the order in which they're mapped
    old_moved, new_moved = (), ()
    if len(diff['moved']) > 0:
        old_moved, new_moved = zip(*diff['moved'])
    old_mod, new_mod = (), ()
    if len(diff['modified']) > 0:
        old_mod, new_mod = zip(*diff['modified'])
    index1, index2 = 0, 0
    moved = [(i, j) for i, j in diff['moved']]
    while index1 < len1 or index2 < len2:
        while index1 < len1 and (
            index1 in old_moved or
            index1 in old_mod or
            index1 in diff['removed']
        ):
            index1 += 1
        while index2 < len2 and (
            index2 in new_moved or
            index2 in new_mod or
            index2 in diff['added']
        ):
            index2 += 1
        if index1 == len1 or index2 == len2:
            assert index1 == len1 and index2 == len2
        else:
            moved.append((index1, index2))
            index1 += 1
            index2 += 1
    return dict(
        added=diff['added'],
        removed=diff['removed'],
        moved=moved,
        modified=diff['modified'],
    )

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

# the Most Important Function
def compute_all_player_histories(id: str):
    revs = get_clean_revs(id)
    # maintain row history for individual rows somehow
    # each row object has an id (player_id)
    # each row object has a current index, representing its presence in the
    # current revision. use separate array for this

    first_rev = get_rev_as_df(id, revs[0])
    first_rev.insert(0, 'Rev', revs[0])
    next_player_id = 0
    all_updates = pd.DataFrame()
    last_player_rows = []
    # the ith pandas row is the (i+1)st row in the sheet array, so we use
    # None as a dummy element. The exception is if there are no headers detected,
    active_player_ids: list[int|None] = [None]
    #if len(first_revs
    #
    def add_row(player_id, row, is_deletion=False):
        nonlocal all_updates
        nonlocal last_player_rows
        row_with_id = pd.concat([
            pd.Series({'player_id': player_id}),
            row
        ])
        row_df = pd.DataFrame(row_with_id).transpose()
        all_updates = pd.concat([all_updates, row_df], ignore_index=True)
        # prefer row_df's version of columns
        if not is_deletion:
            all_updates = all_updates[row_df.columns]
        # update most recent index map
        assert player_id <= len(last_player_rows)
        if player_id == len(last_player_rows):
            last_player_rows.append(len(all_updates)-1)
        else:
            last_player_rows[player_id] = len(all_updates)-1

    # initialize with data in first rev, where each row is new
    for _, row in first_rev.iterrows():
        # remember that df indices are one less than actual
        # because header isn't counted!
        new_row = row
        if 'Rank' in new_row:
            new_row = row.drop(['Rank'])
        add_row(next_player_id, new_row)
        active_player_ids.append(next_player_id)
        next_player_id += 1
    # use transitions between rows
    for rev1, rev2 in zip(revs[:-1], revs[1:]):
        print('Parsing rev', rev2)
        # get row map from diff
        row_map = get_row_map(id, rev1, rev2)
        # first row is always header, since we made sure of that
        new_sheet_df = get_rev_as_df(id, rev2)

        new_active_ids: list[int|None] = [
            None for _ in range(len(get_rev_as_list(id, rev2)))
        ]
        # removed rows are given special entries
        for index in row_map['removed']:
            player_id = active_player_ids[index]
            assert player_id != None
            new_row = pd.Series({'Rev': rev2, 'Name': 'ROW DELETED'})
            add_row(player_id, new_row, is_deletion=True)
        # when looping through moved rows, only update the player_index location
        for index1, index2 in row_map['moved']:
            if index2 == None or index2 == 0:
                continue
            new_active_ids[index2] = active_player_ids[index1]
        # when looping through modified rows, do the full update
        for index1, index2 in row_map['modified']:
            # signifies that the player_id is done.
            # this will not be copied over to the next iteration
            if index2 == None or index2 == 0:
                continue
            player_id = active_player_ids[index1]
            if player_id == None:
                raise ValueError('This shouldn\'t happen')
            #print(index1, index2, player_id)
            # check if row should be updated, then update the player map
            player_index = last_player_rows[player_id]
            last_player_row = all_updates.iloc[player_index, 2:]
            # ignore first two entries, since they are always id, rev
            new_row = new_sheet_df.iloc[index2-1]
            # ignore rank, since this changes a lot
            #if 'rank' in new_row:
            #    new_row.drop(['rank'])
            if not last_player_row.equals(new_row):
            #if not np.array_equal(last_player_row, new_row, equal_nan=True):
                # add rev, then add row
                new_row = pd.concat([pd.Series({'Rev': rev2}), new_row])
                add_row(player_id, new_row)
            # update active_player_ids
            new_active_ids[index2] = player_id

        for index in row_map['added']:
            # basically repeat the process for adding a new thing
            new_row = new_sheet_df.iloc[index-1]
            # ignore rank, since this changes a lot
            if 'rank' in new_row:
                new_row.drop(['rank'])
            new_row = pd.concat([pd.Series({'Rev': rev2}), new_row])
            add_row(next_player_id, new_row)
            active_player_ids.append(next_player_id)
            new_active_ids[index] = next_player_id
            next_player_id += 1

        assert all(i != None for i in new_active_ids[1:])
        active_player_ids = new_active_ids
    # remove player_ids that only have rows that are full NaNs
    all_updates = all_updates[all_updates
        .drop(columns=['Rev', 'player_id'])
        .apply(lambda x: not pd.isna(x).all(), axis=1)
    ]
    all_player_ids = all_updates.player_id.unique()
    player_folder = f'findings/sheets/{id}/players'
    if not os.path.exists(player_folder):
        os.makedirs(f'findings/sheets/{id}/players')
    # clean up files
    for filename in os.listdir(player_folder):
        path = os.path.join(player_folder, filename)
        if os.path.isfile(path):
            os.unlink(path)
    # write each row history to file
    for player_id in all_player_ids:
        #print(player_id)
        player_history = all_updates[all_updates.player_id == player_id]
        player_history = player_history.drop(columns=['player_id'])
        if 'Rank' in player_history.columns:
            player_history = player_history.drop(columns=['Rank'])
        # if only two rows and second is 'ROW DELETED', then
        # probably a useless row, and shouldn't be written
        if len(player_history) < 3 and player_history.iloc[-1]['Name'] == 'ROW DELETED':
            continue
        print('Writing', get_most_recent_name(player_history))
        player_history.to_csv(f'findings/sheets/{id}/players/{player_id}.csv', index=False)

def get_most_recent_name(history):
    for i in range(len(history)-1, -1, -1):
        test_name = str(history.iloc[i]['Name'])
        if test_name != 'nan' and test_name != 'ROW DELETED':
            return test_name
    return 'nan'

def write_player_names(id: str):
    player_ids = []
    for filename in os.listdir(f'findings/sheets/{id}/players'):
        # attempt to extract number
        if filename.endswith('.csv'):
            player_ids.append(int(filename[:-4]))
    player_ids.sort()
    player_name_counts = defaultdict(int)
    player_names = {}
    for player_id in player_ids:
        history = pd.read_csv(f'findings/sheets/{id}/players/{player_id}.csv')
        name = get_most_recent_name(history)
        player_name_counts[name] += 1
        if player_name_counts[name] > 1:
            player_names[name + f' ({player_name_counts[name]})'] = player_id
        else:
            player_names[name] = player_id
    with open(f'findings/sheets/{id}/players/names.json', 'w') as f:
        json.dump(player_names, f, indent=2)

if __name__ == '__main__':
    # Use to filter out versions with bad headers
    #print_distinct_sheet_headers("NTSC 0-19 Score")

    # Check that all unusual revs are accounted for
    #print_unusual_revs("1516944123", hide_explained=False)
    #print_unusual_revs("1078039113", hide_explained=False)

    # Write player histories to their own files
    compute_all_player_histories('1078039113')

    # After player histories are found, write the most recent names
    # used for each one
    write_player_names('1078039113')
