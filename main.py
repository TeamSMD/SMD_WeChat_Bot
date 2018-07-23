from wxbot import *
import db
import SMD_api
import logging
import time
import threading
import re

bot = WXBot
SMDapi = SMD_api.SMDapi
op_status = {}
bindings = {}
AwaitQueue = {}
user_extra = {}
flag_time_pause = False


def queue_processor():
    global flag_time_pause

    while True:
        if AwaitQueue.__len__() != 0:
            first_item_key = list(AwaitQueue.keys())[0]
            if AwaitQueue[first_item_key] >= 120:
                flag_time_pause = True
                op_status[first_item_key] = 'paying'
                bot.send_msg_by_uid('轮到你啦~', first_item_key)
                bot.send_msg_by_uid('为了不让后面的人等太久，你现在有120秒的时间来完成支付', first_item_key)
                bot.send_msg_by_uid('扫描下面的二维码，输入数额来完成充值', first_item_key)
                bot.send_img_msg_by_uid('qrcode.jpg', first_item_key)
                AwaitQueue[first_item_key] = 119
                flag_time_pause = False
        else:
            pass

        time.sleep(0.1)


def queue_time_man():
    global flag_time_pause

    while True:
        if not flag_time_pause:
            if AwaitQueue.__len__() != 0:
                if AwaitQueue[list(AwaitQueue.keys())[0]] > 0:
                    AwaitQueue[list(AwaitQueue.keys())[0]] -= 1
                else:
                    bot.send_msg_by_uid('支付超时啦，要重新排队哦~下次要抓紧时间呀', list(AwaitQueue.keys())[0])
                    op_status[list(AwaitQueue.keys())[0]] = 'idle'
                    del AwaitQueue[list(AwaitQueue.keys())[0]]

        time.sleep(1)


class Bot(WXBot):
    @staticmethod
    def check_is_idle(user_id):
        return op_status[user_id] == 'idle'

    @staticmethod
    def check_bind_status(user_id):
        if user_id in bindings and bindings[user_id] != '':
            return bindings[user_id]
        else:
            return ''

    def user_msg(self, msg_data, user_id):

        if user_id in op_status:
            # 如果不是新用户
            if self.check_is_idle(user_id):
                # 如果当前不在某操作期间
                if msg_data == '绑定':
                    if self.check_bind_status(user_id) == '':
                        op_status[user_id] = 'binding'
                        self.send_msg_by_uid(
                            '你的SMD账号是什么？如果还没有的话可以去teamsmd.org/artexpo/register注册哦~', user_id)
                    else:
                        self.send_msg_by_uid('你的微信已经绑定了SMD账号了，对我说"解绑"来解除绑定', user_id)
                elif msg_data == '硬币':
                    if self.check_bind_status(user_id) != '':
                        self.send_msg_by_uid('你还有 ' + str(SMDapi.get_coins(bindings[user_id])) + " 个金币", user_id)
                    else:
                        self.send_msg_by_uid('客官还没有绑定哦~对我说"绑定"来绑定你的SMD账号吧', user_id)
                elif msg_data == '充值' or msg_data == '冲值':
                    if self.check_bind_status(user_id) != '':
                        op_status[user_id] = 'await'
                        self.send_msg_by_uid('你已经进入等待队列啦，要轮流来哦~', user_id)
                        # 加入等待列表
                        AwaitQueue[user_id] = 121  # 加一秒容错
                elif msg_data == '解绑':
                    if self.check_bind_status(user_id) != '':
                        bindings[user_id] = ''
                        db.unbind(user_id)
                        self.send_msg_by_uid('解绑成功', user_id)
                else:
                    self.send_msg_by_uid('啊？风太大没听清~', user_id)
            else:
                # 如果在操作期间
                # 等待支付状态
                if op_status[user_id] == 'await':
                    if msg_data == '为什么要等':
                        self.send_msg_by_uid('因为如果同时有两个人付款，电脑容易把两个订单弄混哦~', user_id)
                        self.send_msg_by_uid('如果你觉得你等了很久还没有轮到你，可以找在场的工作人员哒~', user_id)
                    elif msg_data == '取消':
                        del AwaitQueue[user_id]
                        op_status[user_id] = 'idle'
                        self.send_msg_by_uid('退出等待队列啦~', user_id)
                    else:
                        self.send_msg_by_uid('麻烦稍等下哦~别人正在付款呢', user_id)
                        self.send_msg_by_uid('如果你想知道为什么要轮流付款，你可以问我"为什么要等"', user_id)
                # 绑定中
                elif op_status[user_id] == 'binding':
                    if msg_data == '取消':
                        op_status[user_id] = 'idle'
                        self.send_msg_by_uid('操作取消啦', user_id)
                    else:
                        if SMDapi.check_user_exists(msg_data):
                            op_status[user_id] = 'binding_pwd'
                            user_extra[user_id] = {}
                            user_extra[user_id]['bind_username'] = msg_data
                            self.send_msg_by_uid('你的密码是多少？', user_id)
                        else:
                            self.send_msg_by_uid('用户名不存在，核对一下用户名？或者对我说"取消"来结束操作', user_id)
                # 绑定状态，等待验证
                elif op_status[user_id] == 'binding_pwd':
                    if msg_data == '取消':
                        op_status[user_id] = 'idle'
                        self.send_msg_by_uid('操作取消啦~', user_id)
                    else:
                        if SMDapi.check_password(user_extra[user_id]['bind_username'], msg_data):
                            bindings[user_id] = user_extra[user_id]['bind_username']
                            db.bind(user_id, user_extra[user_id]['bind_username'])
                            self.send_msg_by_uid('绑定成功', user_id)
                            op_status[user_id] = 'idle'
                        else:
                            self.send_msg_by_uid('密码不对哦~对我说"取消"可以取消操作哦~', user_id)
                elif op_status[user_id] == 'paying':
                    if msg_data == '取消':
                        op_status[user_id] = 'idle'
                        self.send_msg_by_uid('得')
                        del AwaitQueue[user_id]
        else:
            # 是新用户
            op_status[user_id] = 'idle'
            self.send_msg_by_uid('欢迎~对我说"绑定"来绑定你的SMD账号吧~', user_id)

    def handle_msg_all(self, msg):
        global flag_time_pause
        global bot

        if msg['content']['type'] == 0 and msg['msg_type_id'] == 4:
            # 是联系人发的文本消息
            self.user_msg(msg['content']['data'], msg['user']['id'])
        elif msg['msg_type_id'] == 5 or msg['msg_type_id'] == 6:
            # 是公众号发的消息
            flag_time_pause = True
            match = re.findall(r'微信支付收款(.+?)元', msg['content']['data']['title'])
            if match and AwaitQueue.__len__() != 0:
                if float(match[0]) >= 1.0 and float(match[0]).is_integer():
                    SMDapi.add_value(bindings[list(AwaitQueue.keys())[0]], int(float(match[0])))
                    bot.send_msg_by_uid('支付成功，收到了你的 ' + str(int(float(match[0]))) + 'rmb',
                                        list(AwaitQueue.keys())[0])
                    bot.send_msg_by_uid('谢谢你嗷~', list(AwaitQueue.keys())[0])
                    op_status[list(AwaitQueue.keys())[0]] = 'idle'
                    del AwaitQueue[list(AwaitQueue.keys())[0]]
                else:
                    bot.send_msg_by_uid('只能发整数哦~找我们工作人员退回给你吧~', list(AwaitQueue.keys())[0])
            flag_time_pause = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='log.log')
    try:
        SMDapi = SMD_api.SMDapi()
    except Exception:
        print('Auth Failed')
        cont = input('continue?')
        if cont.lower() == 'n':
            exit(0)
        elif cont.lower() == 'y':
            pass
        else:
            print('fuck you')
    users = db.get_users()
    for u in users:
        op_status[u] = 'idle'
    del users
    timer = threading.Thread(target=queue_time_man)
    queue_proc = threading.Thread(target=queue_processor)
    timer.start()
    queue_proc.start()
    bindings = db.get_bindings()
    bot = Bot()
    # bot.conf['qr'] = 'tty'
    bot.DEBUG = True
    bot.run()
