#!/usr/bin/python2
# -*- coding: utf-8 -*-

import psycopg2 as pg2
import csv
import re
from datetime import datetime
import json
import numpy as np
from kmeans import *

def lot2set(lot):
    #Converting list of touples len 1 in list
    s = set()
    for i in lot:
        s.add(i[0])
    return s

def lot2list(lot):
    #Converting list of touples len 1 in list
    l = []
    for i in lot:
        l.append(i[0])
    return l

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
    #except:
    #    print('Conneciton Error')
    #    return None


# Return a list of dicts { label: hashtag, data: [howmanyalone, howmanynotalone]}
def get_metric(ht_list, cfg):
    # try:
    l = []
    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    for ht in ht_list:
        # select tweet ids where the ht appears and make a set
        cur.execute('''SELECT id
                        FROM contains
                        WHERE hname = '{0}'; '''.format(ht))
        fetchall = cur.fetchall()  # Take everything from db, return a list of touples
        ht_appears_set = lot2set(fetchall)
        # From the ids where ht appears, select the ones where others appear
        cur.execute('''SELECT id
                        FROM contains
                        WHERE id
                        IN (SELECT id
                            FROM contains
                            WHERE hname = '{0}')
                        AND NOT hname = '{0}'; '''.format(ht))
        fetchall = cur.fetchall()  # Take everything from db, return a list of touples
        ht_withothers_set = lot2set(fetchall)
        # appears \ appears with other = appears alone
        ht_alone_set = ht_appears_set - ht_withothers_set

        # add to dic
        l.append({'label': ht,
                  'data': [len(ht_alone_set), len(ht_withothers_set)]})
    conn.close()
    return l
    # except:
    #    print('Conneciton Error')
    #    return None

def find_maxs(table):
    maxs = []
    for i in range(len(table[0]['data'])):
        m = 0.0
        for j in table:
            print(j['data'])
            if j['data'][i] > m:
                m = j['data'][i]
        maxs.append(m)
    print(maxs)
    return maxs

def relativize_table(table):
    maxs = find_maxs(table)
    print(maxs)
    for i in range(len(table[0]['data'])):
        for j in table:
            j['data'][i] = float(j['data'][i]) / maxs[i]
    return table


def write_to_json(d, filename):
    # Write the data to a json file
    with open(filename, 'w') as f:
        json.dump(d, f)


def main():

    cfg = {'host': '192.168.178.60',
           'user': 'elecuser',
           'pw': 'elecpass',
           'db': 'elections',
           'port': '5432'}
    write_to_json(relativize_table(get_metric(get_hashtags_list(cfg), cfg)), 'for_clustering.jsonax')

if __name__ == '__main__':
    main()