import json
import csv
import os

from datatypes import *

'''
utility functions for loading various data files
'''

def get_raw_sheet(id: str, rev: int) -> bytes:
    with open(f'data/raws/{id}/{rev}.html.gz', 'rb') as f:
        return f.read()

def get_rev_csv(id: str, rev: int) -> list[list[str]]:
    with open(f'data/revs/{id}/{rev}.csv', 'r') as f:
        sheet = csv.reader(f)
        return list(sheet)

def get_unique_revs(id: str) -> list[int]:
    with open(f'data/revs/{id}/unique_revs.json', 'r') as f:
        return json.load(f)

def get_dirty_revs(id: str) -> list[int]:
    if not os.path.exists(f'data/revs/{id}/dirty_revs.json'):
        return []
    with open(f'data/revs/{id}/dirty_revs.json', 'r') as f:
        revs = []
        intervals = json.load(f)
        for interval in intervals:
            start, end = interval['start'], interval['end']
            for i in range(start, end+1):
                revs.append(i)
        return revs

def get_sheet_history() -> SheetHistory:
    with open('data/sheet_history.json', 'r') as f:
        return json.load(f)

def get_leaderboards() -> Leaderboards:
    with open('data/leaderboards.json', 'r') as f:
        return json.load(f)

def get_timestamps() -> list[Timestamp]:
    with open('data/timestamps.json', 'r') as f:
        return json.load(f)
