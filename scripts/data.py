import json
import csv
import os
import pandas as pd

from datatypes import *

'''
utility functions for loading various data files
'''

def get_raw_sheet(id: str, rev: int) -> bytes:
    with open(f'data/raws/{id}/{rev}.html.gz', 'rb') as f:
        return f.read()

def get_rev_as_list(id: str, rev: int) -> list[list[str]]:
    with open(f'data/revs/{id}/{rev}.csv', 'r') as f:
        sheet = csv.reader(f)
        return list(sheet)

def get_rev_as_df(id: str, rev: int) -> pd.DataFrame:
    with open(f'findings/sheets/{id}/headers.json', 'r') as f:
        all_headers = json.load(f)
        headers = []
        for header_range in all_headers:
            if header_range['start'] <= rev and rev <= header_range['end']:
                headers = header_range['headers']
                break
        if len(headers) == 0:
            raise ValueError('BAD REVISION')
        df = pd.read_csv(f'data/revs/{id}/{rev}.csv')
        df.columns.values[:len(headers)] = headers
        return df

def get_unique_revs(id: str) -> list[int]:
    with open(f'findings/sheets/{id}/unique_revs.json', 'r') as f:
        return json.load(f)

def get_dirty_revs(id: str) -> list[int]:
    if not os.path.exists(f'findings/sheets/{id}/unusual_revs.json'):
        return []
    with open(f'findings/sheets/{id}/unusual_revs.json', 'r') as f:
        revs = []
        intervals = json.load(f)
        for interval in intervals:
            start, end = interval['start'], interval['end']
            if interval['dirty']:
                for i in range(start, end+1):
                    revs.append(i)
        return revs

def get_clean_unusual_revs(id: str) -> list[int]:
    if not os.path.exists(f'findings/sheets/{id}/unusual_revs.json'):
        return []
    with open(f'findings/sheets/{id}/unusual_revs.json', 'r') as f:
        revs = []
        intervals = json.load(f)
        for interval in intervals:
            start, end = interval['start'], interval['end']
            if not interval['dirty']:
                for i in range(start, end+1):
                    revs.append(i)
        return revs

def get_clean_revs(id: str) -> list[int]:
    unique_revs = get_unique_revs(id)
    dirty_revs = get_dirty_revs(id)
    clean = []
    for rev in unique_revs:
        if rev not in dirty_revs:
            clean.append(rev)
    return clean

def get_sheet_history() -> SheetHistory:
    with open('data/sheet_history.json', 'r') as f:
        return json.load(f)

def get_leaderboards() -> Leaderboards:
    with open('data/leaderboards.json', 'r') as f:
        return json.load(f)

def get_timestamps() -> list[Timestamp]:
    with open('data/timestamps.json', 'r') as f:
        return json.load(f)
