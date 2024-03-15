import json

import re

def extract_gg_getportinfo_table(info_output):
    start_line_match = re.search(r'^Entry\s+Port.*$', info_output, re.MULTILINE)
    if not start_line_match:
        return None
    start_index = start_line_match.start()
    info_output = info_output[start_index:]
    end_index = info_output.find("GGSCI (")
    if end_index == -1:
        end_index = None
    info_table = info_output[:end_index].strip()
    return info_table

def gg_getportinfo_to_json(info_output):
    info_table = extract_gg_getportinfo_table(info_output)
    if info_table is None:
        return None
    lines = info_table.split('\n')
    data = []
    for line in lines[2:]: 
        columns = re.split(r'\s{2,}', line.strip())
        columns = [col if col else '<none>' for col in columns]
        entry = columns[0] if len(columns) > 0 else '<none>'
        port = columns[1] if len(columns) > 1 else '<none>'
        erro = columns[2] if len(columns) > 2 else '<none>'
        process = columns[3] if len(columns) > 3 else '<none>'
        assignated = columns[4] if len(columns) > 4 else '<none>'
        program = columns[5] if len(columns) > 4 else '<none>'
        data.append({
            "Entry": entry,
            "Port": port,
            "Error": erro,
            "Process": process,
            "Assigned": assignated,
            "Program":program
        })
    json_data = json.dumps(data, indent=2)
    return json_data

info_output = """
send mgr getportinfo

Sending GETPORTINFO request to MANAGER ...

Dynamic Port List

Starting Index 0
Entry Port  Error  Process     Assigned             Program
----- ----- ----- ----------   -------------------  -------
   0  30010     0       7560   2023/11/19 12:40:15  SERVER
   1  30011     0         59   2023/10/29 02:51:58  SERVER
   2  30012     0      18938   2024/01/25 09:45:07  SERVER
   3  30013     0      18942   2024/01/25 09:45:08  SERVER
   4  30014     0      18946   2024/01/25 09:45:14  SERVER
   5  30015     0      18950   2024/01/25 09:45:16  SERVER
   6  30016     0      18954   2024/01/25 09:45:29  SERVER
   7  30017     0      18958   2024/01/25 09:45:31  SERVER
   8  30018     0       7619   2023/11/19 12:46:13  SERVER
   9  30019     0       7623   2023/11/19 12:46:13  SERVER
  10  30020     0       7625   2023/11/19 12:46:13  SERVER
  11  30021     0       7626   2023/11/19 12:46:13  SERVER
  12  30022     0       7627   2023/11/19 12:46:14  SERVER
  13  30023     0       7628   2023/11/19 12:46:14  SERVER
  14  30024     0       7629   2023/11/19 12:46:14  SERVER
  15  30025     0       7668   2023/11/19 14:23:12  SERVER
  16  30026     0      18962   2024/01/25 09:45:34  SERVER
  17  30027     0      18229   2024/01/21 09:31:06  SERVER



GGSCI (ggready-5cdb555946-vkmzs) 2>

"""

json_data = gg_info_to_json(info_output)
print(json_data)

