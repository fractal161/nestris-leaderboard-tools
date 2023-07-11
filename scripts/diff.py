from difflib import SequenceMatcher

'''
basically copy the strategy from the ts version
first just hash the rows
then check to see if there are any movements
then check to see if only one delete/add
'''
def diffSheets(sheet1: list[list[str]], sheet2: list[list[str]]):
    # imsheet is "immutable sheet", for passing in to difflib
    imsheet1 = [tuple(r[1:]) for r in sheet1]
    imsheet2 = [tuple(r[1:]) for r in sheet2]
    diff = SequenceMatcher(None, imsheet1, imsheet2)
    changed_rows1 = {}
    changed_rows2 = {}
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
            moved.append([i1, i2])
        else:
            removed.append(i1)
    for row, i in changed_rows2.items():
        if row not in changed_rows1:
            added.append(i)
    return dict(
        moved=moved,
        added=added,
        removed=removed
    )
