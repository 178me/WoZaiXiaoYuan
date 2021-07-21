''' 日常打卡
'''
import datetime
import logging
import random
import time
import requests
import json
from my_lib import MyLib
# 常用函数
lib = MyLib()
# 是否显示调试信息
#  lib.debug = True


def send_warn(text):
    ''' 发送提醒
    :param text: 提醒文本
    :return: void
    '''
    lib.send_message(text, "")  # 换你自己的喵码
    # 发送间隔60秒 因为云函数不允许单次休眠太久 所以分次
    time.sleep(16)
    time.sleep(16)
    time.sleep(16)
    time.sleep(16)


class WoZaiXiaoYuan():
    ''' 我在校园自动打卡
    '''

    def __init__(self):
        # 一日三检api
        self.heat_url = "https://student.wozaixiaoyuan.com/heat/save.json"
        # 健康打卡api
        self.health_url = "https://student.wozaixiaoyuan.com/health/save.json"

        self.headers = {
            "Host": "student.wozaixiaoyuan.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://servicewechat.com/wxce6d08f781975d91/150/page-frame.html",
            "token": "",
        }

        # 默认一日三检数据 自行修改
        self.heat_data = {
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

        # 默认健康打卡数据 自行修改
        self.health_data = {
            "answers": '["0"]',
            "latitude": "23.404326",
            "longitude": "113.220125",
            "country": "中国",
            "city": "广州市",
            "district": "花都区",
            "province": "广东省",
            "township": "花城街道",
            "street": "公益路",
            "areacode": "440114",
        }

        # 用户信息列表 可设置多用户
        self.user_info = [
            {
                "token": "",  # 如果不使用网络剪贴板则填写此字段即可
                # 需要管理的填写
                "name": "",  # 用户名
                "netcut_id": "",  # 剪贴板ID
                "netcut_pwd": "",  # 剪贴板密码
                "token_end_date": "",  # 口令过期时间
                "token_status": "Normal",  # 口令状态
                # 自定义地区
                "data": {
                }
            },
        ]

    # 设置随机体温
    def set_random_temprature(self):
        ''' 设置随机体温
        '''
        random.seed(time.ctime())
        self.heat_data["temperature"] = "{:.1f}".format(
            random.uniform(36.2, 36.7))

    def set_seq(self):
        ''' 获取打卡时段
        '''
        current_hour = datetime.datetime.now()  # + datetime.timedelta(hours=8)
        current_hour = current_hour.hour
        if 0 <= current_hour <= 8:
            self.heat_data["seq"] = "1"
        elif 11 <= current_hour < 15:
            self.heat_data["seq"] = "2"
        elif 17 <= current_hour < 21:
            self.heat_data["seq"] = "3"
        else:
            self.heat_data["seq"] = "0"

    def set_token_end_date(self, token_begin_date, user_index):
        ''' 设置口令结束日期
        :param  user_index: 用户下标
        '''
        # 令牌三天过期
        self.user_info[user_index]["token_end_date"] = token_begin_date + \
            datetime.timedelta(days=3)

    def set_token_status(self, user_index):
        ''' 设置令牌状态
        :param user_index: 用户下标
        '''
        # 云函数计算慢8个小时
        current_time = datetime.datetime.now()  # + datetime.timedelta(hours=8)
        # 计算时间
        remaining_time = (
            self.user_info[user_index]["token_end_date"]-current_time)
        # 根据时间返回结果
        if remaining_time.total_seconds() > (1 * 24 * 60 * 60):
            # 正常
            self.user_info[user_index]["token_status"] = "Normal"
        elif 0 < remaining_time.total_seconds() <= (1 * 24 * 60 * 60):
            # 剩余一天 提醒
            self.user_info[user_index]["token_status"] = "Warn"
        else:
            # 过期
            self.user_info[user_index]["token_status"] = "Invalid"

    def set_user_info_from_netcut(self):
        ''' 从剪贴板设置用户信息
        :return: void
        '''
        for user_index in range(len(self.user_info)):
            # 修改获取文本的用户名
            try:
                netcut_data = lib.get_netpad_text(
                    self.user_info[user_index]["netcut_id"])
                # 设置令牌结束时间
                self.user_info[user_index]["token_end_date"] = datetime.datetime.strptime(
                    netcut_data["updated_time"], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=3)
                self.set_token_status(user_index)
                note_content = json.loads(netcut_data["note_content"])
                # 设置令牌
                self.user_info[user_index]["token"] = note_content["token"]
                self.user_info[user_index]["data"] = note_content["data"]
            except:
                lib.log(self.user_info[user_index]["name"] + " 获取用户信息失败")

    def get_heat_data(self, user_index):
        ''' 获取每日三检数据
        :param user_index: user_index
        :return: 打卡数据
        '''
        self.set_seq()
        self.set_random_temprature()
        heat_data = self.heat_data
        for key, value in self.user_info[user_index]["data"].items():
            if value == "":
                heat_data = self.heat_data
                break
            if key == "areacode":
                continue
            heat_data[key] = value
        return heat_data

    def get_health_data(self, user_index):
        ''' 获取健康打卡数据
        :param user_index: user_index
        :return: 打卡数据
        '''
        health_data = self.health_data
        for key, value in self.user_info[user_index]["data"].items():
            if value == "":
                health_data = self.health_data
                break
            health_data[key] = value
        return health_data

    def check_token_status(self, user_index):
        ''' 处理口令状态
        :param user_index: 用户下标
        :return: 口令状态
        '''
        if self.user_info[user_index]["token_status"] == "Warn":
            # 云函数计算慢8个小时
            current_time = datetime.datetime.now()  # + datetime.timedelta(hours=8)
            # 计算时间
            # 计算时间
            remaining_time = (
                self.user_info[user_index]["token_end_date"]-current_time)
            second = remaining_time.total_seconds()
            minute = int(second / 60 % 60)
            hour = int(second / 60 / 60)
            warn_msg = self.user_info[user_index]["name"] + \
                " 的口令剩余" + str(hour) + " 小时 "+str(minute)+" 分钟过期"
            send_warn(warn_msg)
        elif self.user_info[user_index]["token_status"] == "Invalid":
            err_msg = self.user_info[user_index]["name"] + " 的口令已过期"
            send_warn(err_msg)
        return self.user_info[user_index]["token_status"]

    def punch_card(self, punch_card_type=1):
        ''' 打卡
        :param punch_card_type: 打卡类型 1 = 健康打卡 | 2 = 每日三检
        '''
        punch_card_api = None
        punch_card_data = None
        # 设置口令，开始打卡
        for user_index in range(len(self.user_info)):
            # 判断打卡类型
            if punch_card_type == 1:
                punch_card_api = self.heat_url
                punch_card_data = self.get_health_data(user_index)
            elif punch_card_type == 2:
                punch_card_api = self.health_url
                punch_card_data = self.get_heat_data(user_index)
                # 是否在一日三检时间段
                if punch_card_data["seq"] == "0":
                    continue
            else:
                break
            # 检查口令状态
            if self.check_token_status(user_index) == "Invalid":
                continue
            self.headers["token"] = self.user_info[user_index]["token"]
            respone_body = None
            break
            try:
                respone_body = requests.post(
                    punch_card_api,
                    headers=self.headers,
                    data=punch_card_data,
                ).json()
            except Exception as error:
                print("请求错误", error)
            lib.log(respone_body)
            time.sleep(5)
            # 判断打卡是否成功
            if respone_body["code"] != 0:
                err_msg = "请求错误:" + respone_body["message"] + '\n'
                err_msg += str(self.user_info[user_index]
                               ["name"] + "的口令:" + self.headers["token"])
                send_warn(err_msg)
                lib.log(respone_body)


# 云函数需要这两个参数
#  def main(event,context):
def main():
    ''' 打卡示例
    '''
    # 正常情况下 修改完data 和 user_info 字段信息就可以运行
    wzxy = WoZaiXiaoYuan()
    # 使用网络剪贴板获取token 不需要的可以手动在user_info添加token并注释此功能
    wzxy.set_user_info_from_netcut()
    wzxy.punch_card(2)

main()
