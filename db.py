import sqlite3


def connect():
    return sqlite3.connect('data.db')


def make_table():
    conn = connect()
    conn.execute('create table bindings(wxid TEXT, smd_user TEXT)')
    conn.commit()
    conn.close()


def get_bindings():
    conn = connect()
    cur = conn.cursor()
    cur.execute('select * from bindings')
    r = cur.fetchall()
    bindings = {}
    if r.__len__() == 0:
        return {}
    for b in r:
        bindings[b[0]] = b[1]
    conn.close()
    return bindings


def get_binding(wxid: str):
    conn = connect()
    cur = conn.cursor()
    cur.execute('select count(*) from bindings where wxid = ?', (wxid,))
    r = cur.fetchall()
    if r[0][0] != 0:
        r = cur.execute('select * from bindings where wxid = ?;', (wxid,)).fetchall()[0][1]
        return r
    else:
        conn.close()
        return 0


def unbind(wxid: str):
    conn = connect()
    cur = conn.cursor()
    print(wxid)
    cur.execute('delete from bindings where wxid = ?', (wxid, ))
    conn.commit()
    conn.close()


def bind(wxid: str, username: str):
    conn = connect()
    if get_binding(wxid) != 0:
        cur = conn.cursor()
        cur.execute('update bindings set smd_user = ? where wxid = ?', (username, wxid))
        conn.commit()
        conn.close()
    else:
        conn.execute('insert into bindings values (?, ?)', (wxid, username))
        conn.commit()
        conn.close()


def get_users():
    conn = connect()
    cur = conn.cursor()
    cur.execute('select wxid from bindings')
    r = cur.fetchall()
    lst_users = []
    for u in r:
        lst_users.append(u[0])
    conn.close()
    return lst_users


if __name__ == '__main__':
    make_table()
    print('make table OK')
