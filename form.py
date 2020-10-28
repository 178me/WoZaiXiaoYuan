import requests, time, random


def get_random_temprature():
    random.seed(time.ctime())
    return "{:.1f}".format(random.uniform(36.2, 36.7))


def get_seq():
    current_hour = time.localtime(time.time()).tm_hour
    if 0 < current_hour < 8:
        return "1"
    elif 11 < current_hour < 15:
        return "2"
    else:
        return "3"


headers = {
    "Host": "student.wozaixiaoyuan.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
    "Referer": "https://servicewechat.com/wxce6d08f781975d91/147/page-frame.html",
    "token": "0432eed3-5387-4af0-9714-cafc0d3ef366",  # 此处填写token
    "Content-Length": "360",
}

data = {
    "answers": '["0"]',
    "seq": get_seq(),
    "temperature": get_random_temprature(),
    "latitude": "23.0922820000",
    "longitude": "113.3541850000",
    "country": "中国",
    "city": "广州市",
    "district": "海珠区",
    "province": "广东省",
    "township": "江海街道",
    "street": "上冲中约新街一巷",
}


def main():
    response = requests.post(
        "https://student.wozaixiaoyuan.com/heat/save.json",
        headers=headers,
        data=data,
    ).json()
    print(response)
    print(get_random_temprature())
    r = response["code"]
    if r == 0:
        print("恭喜你打卡成功!")
    else:
        print(response["message"])


if __name__ == "__main__":
    main()
