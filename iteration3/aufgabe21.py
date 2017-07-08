#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2 as pg2
import csv
import re
from datetime import datetime
import json
import numpy as np

# Todo: Create an hashtag object



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

# Make a dictionary {hashtag : id }
def get_ht_ids(ht_list):

    d = dict()
    i = 0
    for ht in ht_list:
        d[ht] = i
        i += 1
    return d


# Return a JSON Object {hashtag: [howmanyalone, howmanynotalone]}
def make_nodes(ht_id_dict, cfg):
    # try:
    l = []
    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    for ht in ht_id_dict:
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

        # add to list
        l.append({'id': ht_id_dict[ht], 'label': ht, 'x': len(ht_alone_set), 'y' : len(ht_withothers_set), 'size': len(ht_appears_set)})

    conn.close()
    return l


def find_max(d,n):
    m = 0.0
    for i in d:
        if d[i][n] > m:
            print(d[i][n])
            m = d[i][n]
    if m == 0.0:
        print('Warning max = 0!')
    return float(m)


# take a table {parameter: [x, y]} and make it relative
def relativize_table(table):
    #find max x
    xmax= find_max(table, 0)
    ymax = find_max(table, 1)
    print(xmax, ymax)
    for i in table:
        print(i, table[i])
        table[i][0] = table[i][0] / xmax
        print(table[i][0])
        table[i][1] = table[i][1] / ymax
    return table


def make_stack_label(table):
    labels = []
    stack = []
    for i in table:
        labels.append(i)
        stack.append(table[i])

    stack = np.stack(stack)
    return stack, labels

def make_edges(cfg, ht_ids):

    l = []
    conn = pg2.connect(host=cfg['host'],
                       user=cfg['user'],
                       password=cfg['pw'],
                       database=cfg['db'],
                       sslmode='require',
                       port='5432')  # Verbindung
    cur = conn.cursor()  # Kursor
    edge_nr = 0
    for ht in ht_ids:
        cur.execute('''SELECT hname
                        FROM contains
                        WHERE id
                        IN (SELECT id
                            FROM contains
                            WHERE hname = '{0}')
                        AND NOT hname = '{0}'; '''.format(ht))
        fetchall = cur.fetchall()
        ht_conn = lot2list(fetchall)
        print(ht_conn)

        conn_nr = len(ht_conn)

        for ht2 in ht_conn:
            print('id', edge_nr, 'source', ht, 'target', ht2)
            l.append({'id': edge_nr, 'source': ht_ids[ht], 'target': ht_ids[ht2]})
            edge_nr += 1
    return l


def make_graph_json(nodes, edges):

    d = dict()
    d['nodes'] = nodes
    d['edges'] = edges

    return d


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

    hashtags_list = get_hashtags_list(cfg)
    ht_ids = get_ht_ids(hashtags_list)
    print(ht_ids['VoterRegistrationDay'])
    nodes = make_nodes(ht_ids, cfg)
    edges = make_edges(cfg, ht_ids)
    graph_json = make_graph_json(nodes, edges)
    write_to_json(graph_json, 'graph.json')


if __name__ == '__main__':
    main()