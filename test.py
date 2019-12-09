import json
from collections import defaultdict

with open('storage/2019-12-08T21-12.json') as f1:
    data1 = json.loads(f1.read())

with open('storage/2019-12-08T21-13.json') as f2:
    data2 = json.loads(f2.read())

diff = defaultdict(dict)

# for top_key, entries in data2.items():
#     for k, v2 in entries.items():
#         v1 = data1[top_key].get(k)
#         if v1 is None or v1 != v2:
#             diff[top_key][k] = v2

# print(json.dumps(diff))
