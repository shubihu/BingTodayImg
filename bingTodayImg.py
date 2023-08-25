import re
import json
from datetime import datetime
from urllib.parse import urljoin

import requests

url = 'https://cn.bing.com'

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}

res = requests.get(url, headers=headers)
res.encoding = res.apparent_encoding
ret = re.search("var _model =(\{.*?\});", res.text)
data = json.loads(ret.group(1))
image_content = data['MediaContents'][0]['ImageContent']

image_url = urljoin(url, image_content['Image']['Url'])
r = requests.get(image_url)
with open('today.png', 'wb') as f:
    f.write(r.content)



