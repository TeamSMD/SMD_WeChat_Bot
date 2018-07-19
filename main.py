from wxbot import *
import db
import SMD_api

SMDapi = SMD_api.SMDapi
op_status = {}
bindings = {}
AwaitQueue = {}
user_extra = {}


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
                        self.send_msg_by_uid('你的SMD账号是什么？', user_id)
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
                        # 加入等待列表
                        AwaitQueue[user_id] = 120
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
                        self.send_msg_by_uid('我会告诉你的哦~', user_id)
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
                            del user_extra[user_id]
                            bindings[user_id] = user_extra[user_id]['bind_username']
                            db.bind(user_id, user_extra[user_id]['bind_username'])
                            self.send_msg_by_uid('绑定成功', user_id)
                            op_status[user_id] = 'idle'
                        else:
                            self.send_msg_by_uid('密码不对哦~对我说"取消"可以取消操作哦~', user_id)
        else:
        # 是新用户
            op_status[user_id] = 'idle'
            self.send_msg_by_uid('欢迎~对我说"绑定"来绑定你的SMD账号吧~', user_id)

    def handle_msg_all(self, msg):
        if msg['content']['type'] == 0:
            bot.user_msg(msg['content']['data'], msg['user']['id'])


if __name__ == '__main__':
    SMDapi = SMD_api.SMDapi()
    users = db.get_users()
    for u in users:
        op_status[u] = 'idle'
    del users
    bindings = db.get_bindings()
    bot = Bot()
    bot.run()
