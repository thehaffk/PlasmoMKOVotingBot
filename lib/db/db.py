import pymysql



HOST = '54.37.129.120'
PORT = 3306
USER = 'pepega'
PASSWORD = '0MpnYfzNGV23LjVb'
DATABASE = 'plasmo_rp'

conn = pymysql.connect(host=HOST,
                       port=PORT,
                       user=USER,
                       passwd=PASSWORD,
                       db=DATABASE)
cur = conn.cursor()


def select(table='parliament_votes', columns='*', where='', args='', always_return_all=False, return_list=False):
    if where != '':
        where = 'WHERE ' + where
    request = f'SELECT {columns} FROM {table} {where} {args}'
    # print(request)
    response = cur.execute(request)
    if return_list:
        response = []
        for elem in cur.fetchall():
            response.append(elem[0])
        return response
    if response <= 1 and not always_return_all:
        return cur.fetchone()
    else:
        return cur.fetchall()


def insert(data, table='parliament_votes'):
    request = f'INSERT INTO {table} SET {data}'
    # print(request)
    cur.execute(request)
    conn.commit()
    return True


def delete(where, table='parliament_votes'):
    request = f'DELETE FROM {str(table)} WHERE {str(where)}'
    # print(request)
    cur.execute(request)
    conn.commit()


def update(data, where, table='parliament_votes'):
    request = f'UPDATE {table} SET {data} WHERE {where}'
    # print(request)
    cur.execute(request)
    conn.commit()
