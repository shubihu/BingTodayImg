import re
import time
import json
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

class WechatMessagePush:
    def __init__(self, appid, appsecret, temple_id):
        self.appid = appid
        self.appsecret = appsecret

        # 模板id,参考公众号后面的模板消息接口 -> 模板ID(用于接口调用):IG1Kwxxxx
        self.temple_id = temple_id

        self.token = self.get_Wechat_access_token()
   

    def get_Wechat_access_token(self):
        '''
        获取微信的access_token： 获取调用接口凭证
        :return:
        '''
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        response = requests.get(url)

        res = response.json()
        if "access_token" in res:
            token = res["access_token"]
            return token

    def get_wechat_accout_fans_count(self):
        '''
        获取微信公众号所有粉丝的openid
        '''
        next_openid = ''
        url = f"https://api.weixin.qq.com/cgi-bin/user/get?access_token={self.token}&next_openid={next_openid}"
        response = requests.get(url)
        res = response.json()['data']['openid']
        return res

    def send_wechat_temple_msg(self, content=None):
        '''
        发送微信公众号的模板消息'''
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.token}"

        fan_open_id = self.get_wechat_accout_fans_count()
        # print(fan_open_id)
        for open_id in fan_open_id:
            body = {
                "touser": open_id,
                'template_id': self.temple_id,
                # "topcolor": "#667F00",
                # "data": {
                #     "price1": {"value":'老庙:605.00'}
                # }
                "data": content
            }
            headers = {"Content-type": "application/json"}
            data = json.JSONEncoder().encode(body)
            res = requests.post(url=url, data=data, headers=headers)

def getPrice():
    url='https://vip.stock.finance.sina.com.cn/q//view/vGold_Matter_History.php?page=1&pp=0&pz=0&'
    res = requests.get(url)
    if res.status_code == 200:
        data = pd.read_html(res.text)[0]
    data.columns = data.iloc[0,:]
    data = data.iloc[1:,:]
    current_date = datetime.now().strftime('%Y-%m-%d')
    data = data[(data['日期'] == current_date) & (data['产品'] == '黄金价格')]
    goldPrice = [f'{i}:{j}' for i,j in zip(data['品牌'], data['价格'])][:6]
    with open('goldPrice.txt', 'a+') as fw:
        fw.write(current_date + '\t' + '\t'.join(goldPrice) + '\n')
    goldPrice_dict = {}
    for i, j in enumerate(goldPrice, start = 1):
        key = f'price{i}'
        value = {'value': j, 'color':"#173177"}
        goldPrice_dict[key] = value
    return goldPrice_dict

def testUrl(url):
    start_time = time.time()
    response = requests.get(url)
    if response.status_code == 200:
        end_time = time.time()
        delay = end_time - start_time
        if delay < 6:
            return url

if __name__ == '__main__':
    url = 'https://cn.bing.com'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    
    res = requests.get(url, headers=headers)
    res.encoding = res.apparent_encoding
    ret = re.search("var _model =(\{.*?\});", res.text)
    if ret:
        data = json.loads(ret.group(1))
        image_content = data['MediaContents'][0]['ImageContent']
        
        image_url = urljoin(url, image_content['Image']['Url'])
        r = requests.get(image_url)
        with open('today.png', 'wb') as f:
            f.write(r.content)

    appid = "wx43bc06f0eaedf902"
    screct = "226d73a58fe21c0ab564e1836bb02599"
    template_id = 'K0KwLFPLXYlEaCb_VVm-6ZqbaI3uDtNuH3ifpcVVMC0'
    goldPrice = getPrice()
    WechatMessagePush(appid, screct, template_id).send_wechat_temple_msg(content=goldPrice)

    fw_m3u = open('tv.m3u', 'w')
    fw_txt = open('tv.txt', 'w')
    fw_m3u.write('#EXTM3U\n')
    fw_txt.write('国内,#genre#\n')
    
    with open('tvName.txt') as f:
        for tv in f:
            tv = tv.strip().upper()
            try:
                # res = requests.get(f'https://api.pearktrue.cn/api/tv/search.php?name={tv}&page=1')
                res = requests.get(f'http://tonkiang.us/?s={tv}')
                # data = res.json().get('data', [])
                soup = BeautifulSoup(res.text, 'html.parser')
                channel_divs = soup.find_all('div', class_='channel')
                channel_names = [c.get_text().strip() for c in channel_divs]
                channel_names = [c for c in channel_names if c.upper()==tv]
                num = min(5, len(channel_names))
                tables = soup.find_all('table')

                for t in tables[:num]:
                    fw_m3u.write(f'#EXTINF:-1 group-title="国内",{tv}\n')
                    url = t.find_all('td')[1].get_text().strip()
                    fw_m3u.write(url + '\n')
                    fw_txt.write(f'{tv},{url}\n')
                    
                
                # for item in data:
                #     if item['videoname'].strip().lower() == tv:
                #         url = item.get('link', '')
                #         if url.endswith('m3u8'):
                #             fw_m3u.write(f'#EXTINF:-1 group-title="国内",{tv.upper()}\n')
                #             url = testUrl(url)
                #             if url:
                #                 fw_m3u.write(url + '\n')
                #                 fw_txt.write(f'{tv.upper()},{url}\n')

                time.sleep(5)
            except Exception as e:
                print(f"Error processing {tv}: {e}")

    fw_m3u.close()
    fw_txt.close()
    



