#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
dict = { hashtag: [date, freq]}
'''
import psycopg2 as pg2
from datetime import datetime
import json


def lot2list(lot):
    #Converting list of touples len 1 in list
    l = []
    for i in lot:
        l.append(i[0])
    return l

def make_timestamp(s):
    # Convert a string in a datetime object:
    # https://www.postgresql.org/docs/8.0/static/datatype-datetime.html
    return datetime.strptime(s, '%Y-%m-%d')


def lot2set(lot):
    #Converting list of touples len 1 in list
    s = set()
    for i in lot:
        s.add(i[0])
    return s

def get_days_list(cfg):
    #Return a list of hashtag from database
    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    cur.execute('''SELECT time FROM tweets''')
    fetchall = cur.fetchall()
    conn.close()
    days_set = lot2set(fetchall)
    return days_set

def get_hashtags_list(cfg):
    #Return a list of hashtag from database
    #try:
    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    cur.execute('''SELECT * from hashtags''')
    fetchall = cur.fetchall()
    conn.close()
    ht_list = lot2list(fetchall)
    #print(ht_list)
    return ht_list


def make_chart_json(ht_list, day_list, cfg):

    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    dic = dict()
    for h in ht_list:
        l = []
        for d in day_list:
            cur.execute('''SELECT COUNT(id)
                           FROM tweets
                           WHERE time = '{0}'
                           AND id IN (SELECT id
                                      FROM contains WHERE hname = '{1}');'''.format(d, h))
            count = int(cur.fetchone()[0])
            if count > 0:
                l.append([d.strftime('%Y%m%d'), count])
        dic[h] = l
        #print(dic)
    return dic


def write_to_json(d, filename):
    #Write the data to a json file
    with open(filename, 'w') as f:
        json.dump(d, f)

def main():

    cfg = {'host': '192.168.178.60',
           'user': 'elecuser',
           'pw': 'elecpass',
           'db': 'elections',
           'port': '5432'}
    jobj = make_chart_json(get_hashtags_list(cfg), get_days_list(cfg), cfg)
    #print(jobj)
    write_to_json(jobj, 'freq25.json')
if __name__ == '__main__':
    main()