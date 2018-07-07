import requests

REQUSET_URL = 'https://teamsmd.org/api'
SESSION_COOKIES = {}


def auth():
    r = requests.get(REQUSET_URL + '/auth',
                     {'password': 'ztudMEGx0CNtTlHj1fVvkS7aJoj9QZN5BP4toSXWwsexNE1iMJXys6jTacrvbz4F'})
    if r.text == 'OK':
        global SESSION_COOKIES
        print('Auth Succeed')
        SESSION_COOKIES = r.cookies
    else:
        print('Auth Failed')


def check_password(username: str, password: str):
    try:
        r = requests.get(REQUSET_URL + '/check_password',
                         {'username': username, 'password': password}, cookies = SESSION_COOKIES)
        return r.json()['ok']
    except Exception:
        return False


def get_coins(username: str)->int:
    try:
        r = requests.get(REQUSET_URL + '/get_coins', {'username': username}, cookies = SESSION_COOKIES)
        if 'error' in r.json():
            return -1
        else:
            return r.json()['coins']
    except Exception:
        return -2


def add_value(username: str, coins: int):
    r = requests.get(REQUSET_URL + '/add_value', {'username': username, 'coins': coins}, cookies = SESSION_COOKIES)