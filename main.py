from wxbot import *
import SMD_api


op_status = {}


class Bot(WXBot):
    def handle_msg_all(self, msg):
        pass


if __name__ == '__main__':
    SMD_api.auth()