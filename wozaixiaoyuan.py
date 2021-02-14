''' 日常打卡
'''
import datetime
import logging
import random
import time
import requests
from my_lib import MyLib
# 常用函数
lib = MyLib()
# 是否显示调试信息
#  lib.debug = True

# 发送提醒
def send_warn(text):
    ''' 发送提醒
    :param text: 提醒文本
    :return: void
    '''
    lib.send_message(text,"tzTCCaL")
    # 发送间隔60秒 因为云函数不允许单次休眠太久 所以分次
    time.sleep(16)
    time.sleep(16)
    time.sleep(16)
    time.sleep(16)

class WoZaiXiaoYuan():
    ''' 我在校园
    '''
    # 一日三检api
    heat_url = "https://student.wozaixiaoyuan.com/heat/save.json"
    # 健康打卡api
    health_url = "https://student.wozaixiaoyuan.com/health/save.json"

    headers = {
        "Host": "student.wozaixiaoyuan.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://servicewechat.com/wxce6d08f781975d91/150/page-frame.html",
        "token": "",  # 此处填写token
        }

    # 一日三检数据 自行修改
    sign_data = {
        "answers": '["0"]',
        "seq": "1",
        "temperature": "36.2",
        "latitude": "23.0923820000",
        "longitude": "113.3551850000",
        "country": "中国",
        "city": "广州市",
        "district": "海珠区",
        "province": "广东省",
        "township": "江海街道",
        "street": "上冲中约新街一巷",
            }

    # 健康打卡数据 自行修改
    health_data = {
        "answers": '["0"]',
         "latitude": "23.404326",
         "longitude": "113.220125",
         "country": "中国",
         "city": "广州市",
         "district": "花都区",
         "province": "广东省",
         "township": "花城街道",
         "street": "公益路",
         "areacode":"440114",
         }

    # 用户信息列表 可设置多用户
    user_info = [
        {
            "name":"",
            "token":"",
            # 抓到口令的日期 此字段影响提醒功能 建议填写
            "token_date":datetime.datetime.strptime(\
                    "2021-2-10 18:00:00", '%Y-%m-%d %H:%M:%S'),
            "txtpad_name":"", # 文本派名称 必填
            "txtpad_pwd":"",
            },
    ]

    # 获取随机体温
    def get_random_temprature(self):
        ''' 获得随机体温
        :return: 正常范围体温
        '''
        random.seed(time.ctime())
        return "{:.1f}".format(random.uniform(36.2, 36.7))

    def get_seq(self):
        ''' 获取打卡时段
        :return: seq值 || 0(不在打卡时间内)
        '''
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

    def get_token_dead_time(self, token_date):
        ''' 获取口令失效时间
        :param date_time: 口令获取时间
        :return: 状态码 || 剩余时间
        '''
        # 令牌三天过期
        token_date += datetime.timedelta(days=3)
        # 云函数计算慢8个小时
        current_time = datetime.datetime.now()  # + datetime.timedelta(hours=8)
        # 计算时间
        second = (token_date - current_time).total_seconds()
        minute = int(second / 60 % 60)
        hour = int(second / 60 / 60)
        # 根据时间返回结果
        if 0 <= hour < 24:
            # 剩余一天 提醒
            return str(hour)+" 小时 "+str(minute)+" 分钟"
        elif current_time < token_date:
            # 正常
            return 0
        else:
            # 过期
            return -1

    def get_token_info(self):
        ''' 获取令牌，并更新user_info
        :return: void
        '''
        for i in range(len(self.user_info)):
            # 修改获取文本的用户名
            arr = lib.get_netpad_text(self.user_info[i]["txtpad_name"])
            # 第一个文本 令牌
            self.user_info[i]["token"] = arr["note_content"].strip()
            # 第二个文本 令牌获取时间
            self.user_info[i]["token_date"] = datetime.datetime.strptime(\
                arr["updated_time"], '%Y-%m-%d %H:%M:%S')

    def punch_card(self,punch_card_api,punch_card_info,token,index):
        ''' 打卡
        :param url: 打卡的api
        :param data: 打卡提交的数据
        :param token: 口令
        :param index: 第几个用户
        :return: void
        '''
        # 检查口令状态 手动的自己填写日期
        token_statue = self.get_token_dead_time(self.user_info[index]["token_date"])
        if token_statue == -1:
            # 发送过期警告
            token_statue = str(
            self.user_info[index]["name"]+"的口令:" + self.headers["token"]+'\n'+"错误信息:口令过期")
            send_warn(token_statue)
            lib.log("过期")
        elif(token_statue == 0):
            # 正常
            pass
        else:
            # 发送将过期警告
            token_statue += '\n' + \
                str(self.user_info[index]["name"]+"的口令:" + self.headers["token"])
            send_warn(token_statue)
            lib.log("即将过期")
        # 设置口令，开始打卡
        self.headers["token"] = token
        response = None
        try:
            response = requests.post(
                punch_card_api,
                headers=self.headers,
                data=punch_card_info,
            ).json()
        except Exception as error:
            print("请求错误")
            print(error)
        lib.log(response)
        time.sleep(5)
        # 判断打卡是否成功
        if response["code"] == 0:
            #  print("恭喜你打卡成功!")
            pass
        else:
            token_statue = "请求错误:" + response["message"]
            token_statue += '\n' + \
                str(self.user_info[index]["name"]+"的口令:" + self.headers["token"])
            send_warn(token_statue)
            print(response)


# 云函数需要这两个参数
#  def main(event,context):
def main():
    ''' 打卡示例
    '''
    # 正常情况下 修改完data 和 user_info 字段信息就可以运行
    wzxy = WoZaiXiaoYuan()
    # 使用网络剪贴板获取token 不需要的可以手动在user_info添加
    wzxy.get_token_info()
    # 
    for index in range(len(wzxy.user_info)):
        # 调用健康打卡
        wzxy.punch_card(wzxy.health_url,wzxy.health_data,wzxy.user_info[index]["token"],index)

main()
