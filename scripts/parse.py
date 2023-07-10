from json.encoder import INFINITY
import lxml.html
import gzip
import json
import hashlib
import csv
from multiprocessing import Pool
from collections import OrderedDict
import re
import os
import sys
import tqdm
from urllib.parse import unquote
import cProfile

def compute_spreadsheet_history():
    sheet_history = dict()

    for i in range(1, 39067):
        with open(f'data/raws/1078039113/{i}.html.gz', 'rb') as f:
            content = str(gzip.decompress(f.read()), encoding='utf-8')
            script_start = content.rfind('<script')
            script_end = content.rfind('</script>')
            if script_start == -1 or script_end == -1:
                print(f'REV {i} is weird')
                print(content)
                sys.exit(1)

            script_line = content[script_start:script_end].split('\n')[2]
            start = script_line.find('[')
            end = script_line.rfind(']')
            if start == -1 or end == -1:
                print(f'REV {i} is weird')
                print(content)
                sys.exit(1)

            current_sheet_names = dict(map(
                lambda x: (int(x['id']), x['name']),
                json.loads(script_line[start:end+1])
            ))
            for sheet_id, name in current_sheet_names.items():
                # sheet is created
                if sheet_id not in sheet_history.keys():
                    interval = OrderedDict()
                    interval['title'] = name
                    interval['start'] = i
                    interval['end'] = None
                    sheet_history[sheet_id] = [interval]
                    print(f'REV {i}: added {(sheet_id, name)}')
                # sheet changes name
                elif sheet_history[sheet_id][-1]['title'] != name:
                    sheet_history[sheet_id][-1]['end'] = i - 1
                    print(f'REV {i}: renamed sheet {sheet_id} to {name}')
                    interval = OrderedDict()
                    interval['title'] = name
                    interval['start'] = i
                    interval['end'] = None
                    sheet_history[sheet_id].append(interval)

            for sheet_id, intervals in sheet_history.items():
                # sheet is deleted
                if sheet_id not in current_sheet_names and intervals[-1]['end'] == None:
                    intervals[-1]['end'] = i
                    print(f'REV {i}: removed {sheet_id}')

    for sheet_id, intervals in sheet_history.items():
        if intervals[-1]['end'] == None:
            intervals[-1]['end'] = 39066
    with open('data/sheet_history.json', 'w') as f:
        json.dump(sheet_history, f, indent=2)

# needed so pool.imap_unordered is happy
class CsvWriter(object):
    def __init__(self, gid):
        self.gid = gid
    def __call__(self, i):
        write_csv(i, self.gid)

def write_all_csvs(gid, min_rev, max_rev):
    min_rev = int(min_rev)
    max_rev = int(max_rev)
    if not os.path.exists(f'data/revs/{gid}'):
        os.makedirs(f'data/revs/{gid}')
    pool = Pool()
    for _ in tqdm.tqdm(pool.imap_unordered(
        CsvWriter(gid),
        range(min_rev, max_rev+1)
    ), total=max_rev-min_rev+1):
        pass

def write_csv(i, gid):
    with open(f'data/raws/{gid}/{i}.html.gz', 'rb') as f:
        content = gzip.decompress(f.read())
        # try getting rid of fluff
        content = re.sub(b' tabindex="-1"', b'', content)
        content = re.sub(b' dir="ltr"', b'', content)
        content = re.sub(b' class="s\\d+"', b'', content)
        content = re.sub(b' style="height: 20px;"', b'', content)
        #content = re.sub(rb'(<td [^>]*?></td>)*</tr>', b'</tr>', content)
        ##content = re.sub(rb'<td .*?>', b'<td>', content)
        #content = re.sub(rb'(<tr></td>)*</tr>', b'</tr>', content)
        #content = re.sub(rb'th .*?>', b'th>', content)
        #content = re.sub(b' class=".*?"', b'', content)
        #content = re.sub(b' style=".*?"', b'', content)
        #content = re.sub(rb'(<tr><th><div>\d*</div></th></tr>)*</tbody>', b'</tbody>', content)
        tree = lxml.html.fromstring(str(content, encoding='utf-8'))
        table = tree.find('.//table/tbody')
        assert(table != None)
        with open(f'data/revs/{gid}/{i}.csv', 'w') as g:
            writer = csv.writer(g)
            writer.writerows([
                [e for t in [get_csv_entry(td, i) for td in row.iter(tag='td')] for e in t]
                for row in table.iter(tag='tr')
            ])

# taken from https://www.programiz.com/python-programming/examples/hash-file lmao
def hash_file(filename):
    """"This function returns the SHA-1 hash
    of the file passed into it"""

    # make a hash object
    h = hashlib.sha1()

    # open file for reading in binary mode
    with open(filename,'rb') as file:

        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()

def compute_unique_csv_revs(gid):
    with open('data/sheet_history.json', 'r') as infile:
        history = json.load(infile)
        if gid not in history:
            raise ValueError('invalid gid')
        editions = history[gid]
        start, end = editions[0]['start'], editions[0]['end']
        for edition in editions:
            start = min(start, edition['start'])
            end = max(end, edition['end'])
        unique_revs = [start]
        filehash = hash_file(f'data/revs/{gid}/{start}.csv')
        for i in tqdm.tqdm(range(start+1, end+1)):
            newhash = hash_file(f'data/revs/{gid}/{i}.csv')
            if filehash != newhash:
                unique_revs.append(i)
            filehash = newhash
        print(len(unique_revs), 'distinct revisions')
        with open(f'data/revs/{gid}/unique_revs.json', 'w') as outfile:
            json.dump(unique_revs, outfile)

    # open sheet_history to get start/end revisions
    # add first revision to array
    # compare adjacent hashes, if the second is distinct, add it to array
    # write array to file using json or something

def get_csv_entry(tag, i):
    text = ''
    span = None
    if 'colspan' in tag.attrib:
        span = int(tag.attrib['colspan'])
    for child in tag.iter():
        if child.tag == 'a':
            url = child.attrib['href']
            url = re.sub(r'^https://www.google.com/url\?q=', '', url)
            url = re.sub('&sa=D&.*', '', url)
            text = unquote(url)
            break
        elif child.tag == tag.tag:
            text += child.text or ''
        else:
            text +=  get_csv_entry(child, i)
            if child.tag != 'div':
                print(child.tag)
    if span:
        return (text or '' for _ in range(span))
    elif tag.tag == 'td':
        return (text,)
    return text or ''

def merge_timestamp_chunks():
    timestamps = [{} for _ in range(39068)]
    for chunk_name in os.listdir('data/timestamp-chunks'):
        print('handling', chunk_name)
        with open(os.path.join('data/timestamp-chunks', chunk_name), 'r') as f:
            chunk = json.load(f)
            users = dict()
            for user_id, user_info in chunk['userMap'].items():
                users[user_id] = user_info['name']
            for timestamp in chunk['tileInfo']:
                start, end = timestamp['start'], timestamp['end']
                time = timestamp['endMillis']
                if len(timestamp['users']) > 1:
                    print(f'rev {start} has mutiple users')
                if timestamp['expandable']:
                    print(f'rev {start} is expandable')
                for i in range(start, end+1):
                    timestamps[i]['time'] = time
                    if len(timestamp['users']) > 0:
                        timestamps[i]['editors'] = [users[x] for x in timestamp['users']]
                    else:
                        timestamps[i]['editors'] = [rev['description'] for rev in timestamp['systemRevs']]
    with open('data/timestamps.json', 'w') as f:
        json.dump(timestamps, f, indent=2)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc > 0:
        funcname = sys.argv[1]
        print(funcname)
        if funcname in locals():
            locals()[funcname](*sys.argv[2:])
