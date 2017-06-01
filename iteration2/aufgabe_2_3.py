#!/usr/bin/python

import psycopg2 as pg2
import csv
import re
from datetime import datetime

def extract_hashtags(s):
    # Extract Hashtags from a string with regular expression and
    # return a list of those
    #source :https://stackoverflow.com/questions/2527892/parsing-a-tweet-to-extract-hashtags-into-an-array-in-python
    return re.findall(r"#(\w+)", s)


def string_to_bool(s):
    #Convert True and False from string to Boolean
    return s == 'True'


def make_timestamp(s):
    #Convert a string in a datetime object:
    # https://www.postgresql.org/docs/8.0/static/datatype-datetime.html
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def rm_bad_formatted_chars(s):

    try:
        output = s.encode('utf8')
    except:
        output = ''
        for char in s:
            try:
                char = char.encode('utf-8')
            except:
                char = char.encode('hex')
            output += char
    return output


def execute(cmd, cfg):
    # Erstelle Verbindung mit DB und mache Abfrage
    try:
        conn = pg2.connect(host = cfg['host'],
                            user = cfg['user'],
                            password = cfg['pw'],
                            database = cfg['db'],
                            sslmode = 'require',
                            port = cfg['port']) # Verbindung
        cur = conn.cursor() # Kursor
    except:
        print 'ConnectionProblem'
    cur.execute(cmd)



def aufgabe1(cfg):

    try:
        conn = pg2.connect(host = cfg['host'],
                            user = cfg['user'],
                            password = cfg['pw'],
                            database = cfg['db'],
                            sslmode = 'require',
                            port = cfg['port']) # Verbindung
        cur = conn.cursor() # Kursor
    except:
        print 'ConnectionProblem'

    cur.execute('''
        CREATE TABLE tweets (
            handle           varchar(15) NOT NULL,
            text             varchar(140) NOT NULL,
            time             date NOT NULL,
            retweet_count    integer,
            favorite_count  integer,
            truncated        boolean,
            id               serial PRIMARY KEY);
        ''')
    cur.execute('''
        CREATE TABLE contains (
        hname varchar(140) NOT NULL,
        id integer NOT NULL);
        ''')
    cur.execute('''
        CREATE TABLE hashtags (
        hname varchar(140) NOT NULL);
        ''')
    conn.commit()


def aufgabe2():

    csv_file_name = 'american-election-tweets.csv'
    tweets = []
    hashtags = set()
    with open(csv_file_name, 'r') as f:
        datareader = csv.reader(f, delimiter=';')
        next(datareader)  # skip the header
        for row in datareader:
            # Format the data and put everything in a nice-looking JSON format
            d = dict()
            tweet_ht = extract_hashtags(row[1])
            for ht in tweet_ht:
                hashtags.add(ht)
            d['handle'] = row[0]
            d['text'] = rm_bad_formatted_chars(row[1])
            d['hashtags'] = hashtags
            d['time'] = make_timestamp(row[4])
            d['retweet_count'] = int(row[7])
            d['favorite_count'] = int(row[8])
            d['truncated'] = string_to_bool(row[10])
            tweets.append(d)
    return tweets, hashtags


def aufgabe3(cfg, tweets, hashtags):

    try:
        conn = pg2.connect(host = cfg['host'],
                            user = cfg['user'],
                            password = cfg['pw'],
                            database = cfg['db'],
                            sslmode = 'require',
                            port = cfg['port']) # Verbindung
        cur = conn.cursor() # Kursor
    except:
        print 'ConnectionProblem'

    for d in tweets:
        cur.execute('''
        INSERT INTO tweets(handle, text, time, retweet_count, favorite_count, truncated)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
        '''.format(d['handle'],
                   d['text'],
                   d['time'],
                   d['retweet_count'],
                   d['favorite_count'],
                   d['truncated']))
    conn.commit()
    for ht in hashtags:
        cur.execute('''
        INSERT INTO hashtags(hname) VALUES ({0})
        '''.format(ht))
    for h in d['hashtags']:
        cur.execute('''
        SELECT id FROM tweets WHERE text LIKE {0}
        '''.format(ht))
        res = cur.fetchall() # touple of ids
        print res
        cur.execute('''
        INSERT INTO contains(hname, id) VALUES ({0}, {1})
        '''.format(h, d['id']))


def main():
    cfg = {'host': '192.168.178.60',
           'user': 'testuser',
           'pw': 'testpass',
           'db': 'dbs',
           'port': '5432'}
    aufgabe1(cfg)
    tweets, hashtags = aufgabe2()
    aufgabe3(cfg, tweets, hashtags)


if __name__ == '__main__':
    main()