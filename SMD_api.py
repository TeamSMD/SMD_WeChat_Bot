import requests

REQUSET_URL = 'http://localhost/api'

class SMDapi:
    SESSION_COOKIES = {}

    def auth(self):
        r = requests.get(REQUSET_URL + '/auth',
                         {'password': 'ztudMEGx0CNtTlHj1fVvkS7aJoj9QZN5BP4toSXWwsexNE1iMJXys6jTacrvbz4F'})
        if r.text == 'OK':
            print('Auth Succeed')
            self.SESSION_COOKIES = r.cookies
        else:
            print('Auth Failed')


    def check_password(self, username: str, password: str)->bool:
        try:
            r = requests.get(REQUSET_URL + '/check_password',
                             {'username': username, 'password': password}, cookies = self.SESSION_COOKIES)
            return r.json()['ok']
        except Exception:
            return False


    def get_coins(self, username: str)->int:
        try:
            r = requests.get(REQUSET_URL + '/get_coins', {'username': username}, cookies = self.SESSION_COOKIES)
            if 'error' in r.json():
                return -1
            else:
                return r.json()['coins']
        except Exception:
            return -2


    def add_value(self, username: str, coins: int)->bool:
        r = requests.get(REQUSET_URL + '/add_value', {'username': username, 'coins': coins}, cookies = self.SESSION_COOKIES)
        if r.text == 'OK':
            return True
        else:
            return False


    def check_user_exists(self, username: str)->bool:
        r = requests.get(REQUSET_URL + '/check_user_exists', {'username': username}, cookies = self.SESSION_COOKIES)
        if r.text == 'True':
            return True
        else:
            return False
