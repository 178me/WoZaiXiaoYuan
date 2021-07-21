'''常用方法
    保存一些常用的函数
'''
import warnings
import json
import time
import requests


class MyLib():
    ''' 函数类 '''
    debug = False

    def log(self, obj=""):
        ''' 调试输出
        :param obj: 输出对象
        :return: void
        '''
        if self.debug:
            print("--->", obj)

    def get_txtpad_text(self, txtpad_name, text_title="all", txtpad_password=""):
        ''' 获取文本派指定用户的文本,需要json request warnings库
        :param txtpad_name: 文本派用户名
        :param text_title: 文本标题，默认获取全部
        :param txtpad_password: 用户密码 默认为空
        :return: 一个文本数组 || None
        '''
        # 如果标题为空的话获取所有标题
        text_title = text_title.strip() if text_title != "all" else "all"
        txtpad_url = "https://a6.qikekeji.com/txt/data/detail/"
        txtpad_data = {
            "password": txtpad_password,
            "txt_name": txtpad_name,
        }
        # 获取所有该用户名所有文本 verify是否忽略安全证书 我这里不忽略会报错
        warnings.simplefilter("ignore")
        result = requests.post(
            txtpad_url,
            data=txtpad_data,
            verify=False,
        ).json()
        self.log(result)
        # 提取内容
        txt_content = json.loads(result["data"]["txt_content"])
        # all 提取所有内容
        if text_title == "all":
            return txt_content
        else:
            # 提取指定内容
            text_array = None
            for i in range(len(txt_content)):
                if txt_content[i]["title"].strip() == text_title:
                    text_array = txt_content[i]["content"].splitlines()[1:]
                    break
            else:
                self.log("没有找到 " + text_title + " 标题，请确定标题是否正确")
            return text_array

    def get_netpad_text(self, note_id=""):
        ''' 获取网络剪贴板的内容,需要json request warnings库
        :param note_id: 剪贴板id
        :return: data || error
        '''
        # 如果标题为空的话获取所有标题
        netpad_url = "https://netcut.cn/api/note/data/?note_id=" + \
            note_id + "&_=" + str(int(time.time()))
        # 获取所有该用户名所有文本 verify是否忽略安全证书 我这里不忽略会报错
        warnings.simplefilter("ignore")
        result = requests.post(
            netpad_url,
            verify=False,
        ).json()
        self.log(result)
        if result["error"] == "":
            del result["data"]["log_list"]
            return result["data"]
        else:
            self.log("遇到错误 " + result['error'])
            return result['error']

    def send_message(self, text, txt_id):
        ''' 发送喵提醒消息:
        :param text: 消息
        :param txt_id: 喵文本id
        :return: True || False
        '''
        result = requests.get(
            "http://miaotixing.com/trigger?id="+txt_id,
            {
                "id": txt_id,
                "text": text,
                "type": "json"
            }
        )
        if result.status_code == 502:
            self.send_message(text, txt_id)
            return True
        result = result.json()
        self.log(result)
        if result['code'] == 0:
            return True
        if result['code'] == 102:
            for _ in range(0, 4):
                time.sleep((result["data"]["remaining"]+5)/4)
            return True
            #  self.send_message(text, txt_id)
        else:
            self.log(result['msg'])
            return False


def test():
    ''' 测试
    '''
    #  lib = MyLib()


#  test()
