from wxbot import *
import SMD_api


SMD_api = SMD_api.SMDapi()
op_status = {}
bindings = {}
AwaitQueue = {}


class Bot(WXBot):
    def check_is_idle(self, user_id):
        return op_status[user_id] == 'idle'


    def check_bind_status(self, user_id):
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
                        self.send_msg_by_uid('你还有 ' + str(SMD_api.get_coins(user_id)) + " 个金币", user_id)
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
                        self.send_msg_by_uid('解绑成功', user_id)
                else:
                    self.send_msg_by_uid('啊？风太大没听清~', user_id)
            else:
                # 如果在操作期间
                if op_status[user_id] == 'await':
                    pass
                elif op_status[user_id] == 'binding':
                    pass


    def handle_msg_all(self, msg):
        if msg['content']['type'] == 0:
            print(msg['user']['id'] + ': ' + msg['content']['data'])
            self.send_msg_by_uid('hi', msg['user']['id'])


if __name__ == '__main__':
    SMD_api.auth()
    bot = Bot()
    bot.run()
