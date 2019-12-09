import datetime
import hashlib
import json

import reddit
from parse import parse_year

auth_data = {
    "grant_type": "password",
    "username": "rockisch",
    "password": "vfw5ZEkNPMGN5eki",
}
user_agent = "windows:oped_client:0.1 (by /u/rockisch)"
subreddit = "animethemes"

data = {
    "animes": {},
    "aliases": {},
    "kinds": {
        1: "OP",
        2: "ED",
    },
    "metas": {},
    "artists": {},
    "regions": {},
    "__metas": {},
    "__artists": {},
    "__regions": {},
}

rc = reddit.Client(auth_data, user_agent)
pages = rc.wiki_pages(subreddit)

for p in pages:
    try:
        int(p[0])
    except:
        print(f'INVALID PAGE {p}')
        continue

    print(f'PARSING PAGE {p}')
    try:
        page = rc.wiki_page(subreddit, p)
        entries = parse_year(page["content_md"].replace('\r', ''), data)
    except Exception as e:
        print(f'FAILED TO PARSE PAGE: {e}')

for key in list(data.keys()):
    if key.startswith('__'):
        del data[key]

data = json.dumps(data)
m = hashlib.md5()
m.update(data.encode('utf-8'))
filename = m.hexdigest()
with open(f"storage/{filename}.json", 'w+') as f:
    f.write(data)

metadata= {'most_recent': filename}
with open('storage/metadata.json', 'w+') as f:
    f.write(json.dumps(metadata))
