import lxml.html
import gzip
import json
import csv
from multiprocessing import Pool
from collections import OrderedDict
import re
import sys
import tqdm
import cProfile

def get_spreadsheet_history():
    sheet_history = dict()

    for i in range(1, 39067):
        with open(f'data/score/rev-{i}.html.gz', 'rb') as f:
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


def get_all_csvs():
    pool = Pool()
    MAX = 39067
    MIN = 853
    for _ in tqdm.tqdm(pool.imap_unordered(get_csv, range(MIN, MAX)), total=MAX-MIN):
        pass

def get_csv(i):
    with open(f'data/score/rev-{i}.html.gz', 'rb') as f:
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
        tree = lxml.html.fromstring(content)
        table = tree.xpath('//table')[0]
        assert(table != None)
        with open(f'data/score-csv/rev-{i}.csv', 'w') as g:
            writer = csv.writer(g)
            writer.writerows([
                [td.text or '' for td in row.iter(tag='td')]
                #row.itertext(tag='td')
                for row in table.xpath('./tbody/tr')
            ])

#cProfile.run('get_csv()', 'app.profile')
#get_all_csvs()
get_spreadsheet_history()
