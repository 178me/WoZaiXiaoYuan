# -*- coding: utf-8 -*-
import logging,warnings
import requests, time, random,datetime,json

# 获取随机体温
def get_random_temprature():
    random.seed(time.ctime())
    return "{:.1f}".format(random.uniform(36.2, 36.7))

# 获取打卡时段
def get_seq():
    current_hour = datetime.datetime.now() #+ datetime.timedelta(hours=8)
    current_hour = current_hour.hour
    if 0 <= current_hour <= 8:
        return "1"
    elif 11 <= current_hour < 15:
        return "2"
    elif 17 <= current_hour < 21:
        return "3"
    else:
        return 0

sign_headers = {
        "Host": "student.wozaixiaoyuan.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        #"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
        "Referer": "https://servicewechat.com/wxce6d08f781975d91/150/page-frame.html",
        "token": "",  # 此处填写token
        #"Content-Length": "360",
        }

sign_data = {
        "answers": '["0"]',
        "seq": get_seq(),
        "temperature": get_random_temprature(),
        "latitude": "23.0923820000",
        "longitude": "113.3551850000",
        "country": "中国",
        "city": "广州市",
        "district": "海珠区",
        "province": "广东省",
        "township": "江海街道",
        "street": "上冲中约新街一巷",
        }

token_class = [
        ["泽霖","口令","口令获取时间"],
        ["鹏程","口令","口令获取时间"],
        ["冠汝","口令","口令获取时间"],
        ]

token_headers = {
        "Host": "a6.qikekeji.com",
        "Connection": "keep-alive",
        "Accept": "enote_app/json, text/javascript, */*; q=0.01sec-ch-ua-mobile: ?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://txtpad.cn",
        "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://txtpad.cn/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        }

token_data = {
        "password":"",#如果设置了密码
        "txt_name":"文本名称",#文本派文本名称
        }

user_info = [
        ["文本名称"],
        ["文本名称"],
        ["文本名称"],
        ]

token_url = "https://a6.qikekeji.com/txt/data/detail/"

def get_token_info():
    for i in range(len(user_info)):
        # 修改获取文本的用户名
        token_data["txt_name"] = user_info[i][0]
        # 获取所有该用户名所有文本 verify是否忽略安全证书 我这里不忽略会报错
        warnings.simplefilter("ignore")
        token_info = requests.post(
                token_url,
                headers=token_headers,
                data=token_data,
                verify=False,
                ).text
        try:
            # 转换文本字符串为字典
            token_info = json.loads(token_info)
            token_info = json.loads(token_info["data"]["txt_content"])
        except Exception as e:
            # 可能域名错误
            print("请求错误")
            print(e)
            continue
        # 分割标题和内容，将内容写进token_class
        # 文本派说明 https://txtpad.cn/dailyInspectionReport_as
        # 第一个文本 令牌
        token_class[i][1] = token_info[0]["content"].splitlines()[1].strip()
        print(token_info[0]["content"].splitlines()[1])
        # 第二个文本 令牌获取时间
        token_class[i][2] = datetime.datetime.strptime(token_info[1]["content"].splitlines()[1],'%Y-%m-%d %H:%M')
        print(token_info[1]["content"].splitlines()[1])

# 获取令牌失效时间
def get_token_dead_time(date_time):
    # 令牌三天过期
    date_time += datetime.timedelta(days=3)
    # 云函数计算慢8个小时
    current_time = datetime.datetime.now() #+ datetime.timedelta(hours=8)
    # 计算时间
    second = (date_time - current_time).total_seconds()
    minute = int(second / 60 % 60)
    hour = int(second / 60 / 60)
    if(hour < 24 and hour > 0):
        # 剩余一天 提醒
        return str(hour)+" 小时 "+str(minute)+" 分钟"
    elif(current_time < date_time):
        # 正常
        return 0
    else:
        # 过期
        return -1


# 发送提醒
def send_warn(text):
    miao = requests.get(
            "http://miaotixing.com/trigger?id=tzTCCaL",
            {
                "id": "tzTCCaL",
                "text": text,
                "type": "json"
                }
            )
    return


# 函数计算需要这两个参数
#  def main(event,context):
def main():
    if sign_data['seq'] == 0:
        print("不在打卡时间内")
        return 0
    # 获取口令
    get_token_info()
    # 签到
    for index in range(len(token_class)):
        sign_headers["token"] = token_class[index][1]
        # 检查口令是否过期
        warn_info = get_token_dead_time(token_class[index][2])
        if(warn_info == -1):
            # 发送过期警告
            warn_info = str(token_class[index][0]+"的口令:"+ sign_headers["token"]+'\n'+"错误信息:口令过期")
            time.sleep(16)
            time.sleep(16)
            time.sleep(16)
            time.sleep(16)
            send_warn(warn_info)
            print("过期")
            continue
        elif(warn_info == 0):
            # 正常
            pass
        else:
            # 发送将过期警告
            warn_info += '\n' + str(token_class[index][0]+"的口令:"+ sign_headers["token"])
            send_warn(warn_info)
            print("即将过期")
        #  print("口令:"+headers["token"])
        sign_data["temperature"] = get_random_temprature();
        try:
            response = requests.post(
                    "https://student.wozaixiaoyuan.com/heat/save.json",
                    headers = sign_headers,
                    data = sign_data,
                    timeout=10
                    ).json()
        except Exception as e:
            print("请求错误")
            print(e)
            continue
        #  print("返回值:")
        #  print(response)
        time.sleep(5)
        if response["code"] == 0:
            #  print("恭喜你打卡成功!")
            pass
        else:
            warn_info = "请求错误"
            warn_info += '\n' + str(token_class[index][0]+"的口令:"+ sign_headers["token"])
            send_warn(warn_info)
            time.sleep(16)
            time.sleep(16)
            time.sleep(16)
            time.sleep(16)
            print(response)
    #print("所有帐号打卡完成")

main()

