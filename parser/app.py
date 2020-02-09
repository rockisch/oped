import hashlib
import json

import reddit
from models import ParserData
from parse import parse_year


auth_data = {
    "grant_type": "password",
    "username": "rockisch",
    "password": "vfw5ZEkNPMGN5eki",
}
user_agent = "windows:oped_client:0.1 (by /u/rockisch)"
subreddit = "animethemes"

rc = reddit.Client(auth_data, user_agent)
pages = rc.wiki_pages(subreddit)

data = ParserData()

for page_name in pages:
    parser = None
    try:
        int(page_name[0])
    except Exception:
        pass
    else:
        parser = parse_year

    if parser is None:
        continue

    print(f'PARSING PAGE {page_name}')
    page = rc.wiki_page(subreddit, page_name)
    content = page["content_md"].replace('\r', '')
    parser(content, data)

json_data = json.dumps(data.serialize())
m = hashlib.md5()
m.update(json_data.encode('utf-8'))
filename = m.hexdigest()
with open(f"storage/{filename}.json", 'w+') as f:
    f.write(json_data)

metadata = {'most_recent': filename}
with open('storage/metadata.json', 'w+') as f:
    f.write(json.dumps(metadata))
