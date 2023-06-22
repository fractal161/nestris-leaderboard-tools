from bs4 import BeautifulSoup, SoupStrainer
import gzip
import json
import cchardet
import lxml
import re
import sys
import cProfile

def track_spreadsheets():
    sheets = dict()

    for i in range(1, 34000):
        with open(f'data/rev-{i}.html.gz', 'rb') as f:
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

            current_sheets = dict(map(
                lambda x: (int(x['id']), x['name']),
                json.loads(script_line[start:end+1])
            ))
            for sheet_id, name in current_sheets.items():
                if sheet_id not in sheets.keys():
                    sheets[sheet_id] = name
                    print(f'REV {i}: added {(sheet_id, name)}')
                elif sheets[sheet_id] != name:
                    print(f'REV {i}: renamed {(sheet_id, sheets[sheet_id])} to {(sheet_id, name)}')
                    sheets[sheet_id] = name
            removed = []
            for sheet_id, _ in sheets.items():
                if sheet_id not in current_sheets:
                    removed.append(sheet_id)

            for sheet_id in removed:
                print(f'REV {i}: removed {(sheet_id, sheets[sheet_id])}')
                del sheets[sheet_id]


def get_table():
    only_table = SoupStrainer('table')
    for i in range(33999, 34000):
        print('parsing revision', i)
        with open(f'data/rev-{i}.html.gz', 'rb') as f:
            content = gzip.decompress(f.read())
            # try getting rid of fluff
            content = re.sub(b' tabindex="-1"', b'', content)
            content = re.sub(rb'(<td [^>]*?></td>)*</tr>', b'</tr>', content)
            #content = re.sub(rb'<td .*?>', b'<td>', content)
            #content = re.sub(rb'(<tr></td>)*</tr>', b'</tr>', content)
            content = re.sub(rb'th .*?>', b'th>', content)
            content = re.sub(b' class=".*?"', b'', content)
            content = re.sub(b' style=".*?"', b'', content)
            content = re.sub(rb'(<tr><th><div>\d*</div></th></tr>)*</tbody>', b'</tbody>', content)
            parser = BeautifulSoup(content, 'lxml', parse_only=only_table)
            table = parser.table
            assert(table != None)
            with open(f'stripped/rev-{i}-stripped.html', 'w') as g:
                g.write(str(table))

get_table()
#cProfile.run('get_table()', 'app.profile')
