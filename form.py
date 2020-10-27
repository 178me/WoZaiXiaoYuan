import requests

cookies = {
        'SESSION': 'NDllNDdjMzktZDRhZi00MjUwLTkxZGMtZGM4NDRjMDYwYzU1',#填写你抓包得到的SEESION
        #'SESSION': 'NDllNDdjMzktZDRhZi00MjUwLTkxZGMtZGM4NDRjMDYwYzU1',#填写你抓包得到的SEESION
        'path': '/',
        }

headers = {
        'Host': 'student.wozaixiaoyuan.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
        'Referer': 'https://servicewechat.com/wxce6d08f781975d91/147/page-frame.html',
        #'token': '66719e6a-47f7-4ee7-8472-6f9e4f343ce3',#此处填写token
        'token': 'ddfa86f6-8440-48d4-9612-92ce0f578b7b',#此处填写token
        'Content-Length': '360',
        }

data = {
    "answers": '["0"]',
    "seq": "1",
    "temperature": "36.5",
    "latitude": "23.0922820000",
    "longitude": "113.3541850000",
    "country": "中国",
    "city": "广州市",
    "district": "海珠区",
    "province": "广东省",
    "township": "江海街道",
    "street": "上冲中约新街一巷",
            }

def Autodo():
    response = requests.post(
        "https://student.wozaixiaoyuan.com/heat/save.json",
        headers=headers,
        data=data,
    ).json()
    print(response)
    r = response["code"]
    if r == 0:
        print("恭喜你打卡成功!")
    else:
        print(response["message"])
    # requests.get('https://sc.ftqq.com/此处填写你的Serve酱SCKEY.send?text='+response['message']+'&desp=签到了失败了噢')



def main_handler(event, context):
    return Autodo()

if __name__ == '__main__':
    Autodo()
