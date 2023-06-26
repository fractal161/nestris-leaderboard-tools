import lxml.html
import gzip
import json
import csv
from multiprocessing import Pool
from collections import OrderedDict
import re
import os
import sys
import tqdm
from urllib.parse import unquote
import cProfile

def get_spreadsheet_history():
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


def write_all_csvs():
    pool = Pool()
    MAX = 39067
    MIN = 853
    for _ in tqdm.tqdm(pool.imap_unordered(write_csv, range(MIN, MAX)), total=MAX-MIN):
        pass

def write_csv(i):
    with open(f'data/raws/1078039113/{i}.html.gz', 'rb') as f:
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
        with open(f'data/revs/1078039113/{i}.csv', 'w') as g:
            writer = csv.writer(g)
            writer.writerows([
                [e for t in [get_csv_entry(td, i) for td in row.iter(tag='td')] for e in t]
                for row in table.iter(tag='tr')
            ])

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
                        timestamps[i]['users'] = [users[x] for x in timestamp['users']]
                    else:
                        timestamps[i]['users'] = [rev['description'] for rev in timestamp['systemRevs']]
    with open('data/timestamps.json', 'w') as f:
        json.dump(timestamps, f, indent=2)

#cProfile.run('get_csv()', 'app.profile')
#get_all_csvs()
if __name__ == '__main__':
    argc = len(sys.argv)
    if argc > 0:
        funcname = sys.argv[1]
        print(funcname)
        if funcname in locals():
            locals()[funcname](*sys.argv[2:])
