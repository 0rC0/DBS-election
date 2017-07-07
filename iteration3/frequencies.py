#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
4.  Visualisieren  Sie  die  H ̈aufigkeit  des  Auftretens  aller  ”Hashtags”  im
Laufe  der  Zeit  mit  Balkendiagrammen  entlang  einer  Zeitachse.   Die
kleinste Einheit entlang Ihrer Zeitachse soll ein Tag sein.
5.  Visualisieren Sie die H ̈aufigkeit des Auftretens eines ausw ̈ahlbaren ”Hash-
tags” im Laufe der Zeit mit Balkendiagrammen entlang einer Zeitachse.'''

#!/usr/bin/python

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


def freq2dic(l):
    #convert a list in a dictionary with: key = list's element
    #                                     value = how many time is in the list
    d = dict()
    for i in l:
        if i in d:
            d[i] += 1
        else:
            d[i] = 1
    return d


def ht_freq(days_set, cfg):
    #return a dictionary with:
    #                       keys: hashtags
    #                       values: frequencies

    #try:
    d = dict()
    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    #print(days_set)
    for day in days_set:
        timestamp = make_timestamp(str(day))
        cur.execute(''' SELECT hname 
                        FROM contains 
                        WHERE id IN (SELECT id 
                                    FROM tweets
                                     WHERE time = '{0}') '''.format(timestamp))
        f = cur.fetchall()
        freq_dic = freq2dic(lot2list(f))
        d[str(day)] = freq_dic
    conn.close()
    return d
    #except:
    #    print('Connection Error')
    #    return None

def write_to_json(d, filename):
    #Write the data to a json file
    with open(filename, 'w') as f:
        json.dump(d, f)

def main():

    cfg = {'host': 'localhost',
           'user': 'elecuser',
           'pw': 'elecpass',
           'db': 'elections',
           'port': '5432'}
    write_to_json(ht_freq(get_days_list(cfg), cfg), 'ht_freq.json')

if __name__ == '__main__':
    main()