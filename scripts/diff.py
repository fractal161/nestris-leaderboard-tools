from difflib import SequenceMatcher
from typing import OrderedDict

'''
basically copy the strategy from the ts version
first just hash the rows
then check to see if there are any movements
then check to see if only one delete/add
'''
# TODO: weird behavior with modifying duplicate rows?
def diffSheets(sheet1: list[list[str]], sheet2: list[list[str]]):
    # imsheet is "immutable sheet", for passing in to difflib
    imsheet1 = [tuple(r[1:]) for r in sheet1]
    imsheet2 = [tuple(r[1:]) for r in sheet2]
    diff = SequenceMatcher(None, imsheet1, imsheet2)
    # since order might matter later on
    changed_rows1 = OrderedDict()
    changed_rows2 = OrderedDict()
    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        if tag == 'replace':
            # imsheet1[i1:i2] present in sheet1 but not sheet2
            # imsheet2[j1:j2] present in sheet2 but not sheet1
            for i in range(i1, i2):
                changed_rows1[imsheet1[i]] = i
            for j in range(j1, j2):
                changed_rows2[imsheet2[j]] = j
        elif tag == 'delete':
            # imsheet1[i1:i2] is present in sheet1 but not sheet2
            for i in range(i1, i2):
                changed_rows1[imsheet1[i]] = i
        elif tag == 'insert':
            # imsheet2[j1:j2] present in sheet2 but not sheet1
            for j in range(j1, j2):
                changed_rows2[imsheet2[j]] = j
    moved = []
    added = []
    removed = []
    modified = []
    for row, i1 in changed_rows1.items():
        if row in changed_rows2:
            i2 = changed_rows2[row]
            moved.append((i1, i2))
        else:
            removed.append(i1)
    for row, i in changed_rows2.items():
        if row not in changed_rows1:
            added.append(i)
    added.sort()
    removed.sort()
    # heuristic: in this case, assume that order is preserved
    if len(removed) == len(added):
        is_valid = True
        for old_idx, new_idx in zip(removed, added):
            # heuristic for these is at most two changes
            row_diff = SequenceMatcher(None, sheet1[old_idx], sheet2[new_idx])
            add_count = 0
            rem_count = 0
            for tag, i1, i2, j1, j2 in row_diff.get_opcodes():
                if tag == 'replace':
                    add_count += j2-j1
                    rem_count += i2-i1
                elif tag == 'delete':
                    rem_count += i2-i1
                elif tag == 'insert':
                    add_count += j2-j1
            # if at least two changes, assume the heuristic completely fails
            # and nothing is modified
            if len(removed) > 1 and (add_count > 2 or rem_count > 2):
                modified = []
                is_valid = False
                break
            # otherwise, add the indices as a tuple
            modified.append((old_idx, new_idx))
        if is_valid:
            added = []
            removed = []
    return dict(
        moved=moved,
        added=added,
        removed=removed,
        modified=modified,
    )
