#!/usr/bin/python

import psycopg2 as pg2
import csv
import re
from datetime import datetime

# Hilfsfunktionen
# =========================

def extract_hashtags(s):
    # Extract Hashtags from a string with regular expression and
    # return a list of those
    #source :https://stackoverflow.com/questions/2527892/parsing-a-tweet-to-extract-hashtags-into-an-array-in-python
    return re.findall(r"#(\w+)", s)


def string_to_bool(s):
    #Convert True and False from string to Boolean
    return s == 'True'


def make_timestamp(s):
    # Convert a string in a datetime object:
    # https://www.postgresql.org/docs/8.0/static/datatype-datetime.html
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def rm_bad_formatted_chars(s):
    # Encode in utf8 and eventually remove bad encoded characters
    try:
        output = s.encode('utf8')
    except:
        output = ''
        for char in s:
            try:
                char = char.encode('utf-8')
            except:
                char = ' '
            output += char
    return output


def mod_special_chars(s):
    # Characters like quote or semicolon can be annoing....
    return s.replace(';', ' ').replace("'", " ")

# Aufgabe 1
# ===================================

def aufgabe1(cfg):
    # 1. Erstellen Sie in Ihrer Datenbank "Election" ein zu Ihrem relationalen
    # Modell passendes Datenbankschema mit allen Constraints.

    try:
        conn = pg2.connect(host = cfg['host'],
                            user = cfg['user'],
                            password = cfg['pw'],
                            database = cfg['db'],
                            sslmode = 'require',
                            port = cfg['port']) # Verbindung
        cur = conn.cursor() # Kursor

        # Erstelle die Relationen/Tabelle
        cur.execute('''
            CREATE TABLE tweets (
                handle           varchar(15) NOT NULL,
                text             varchar(500) NOT NULL,
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
    except:
        print 'ConnectionProblem'


# Aufgabe 2
# =================================

def aufgabe2():
    # Stellen Sie sicher, dass alle Daten, die Sie spaeter importieren werden
    # fehlerfrei sind. Reparieren oder verwerfen Sie betreffende Datensaetze.
    # Schreiben Sie ein Programm in einer Programmiersprache Ihrer Wahl,
    # dass diese Aufgabe fuer Sie uebernimmt.
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
            d['text'] = mod_special_chars(rm_bad_formatted_chars(row[1]))
            d['hashtags'] = hashtags
            d['time'] = make_timestamp(row[4])
            d['retweet_count'] = int(row[7])
            d['favorite_count'] = int(row[8])
            d['truncated'] = string_to_bool(row[10])
            tweets.append(d)
    return tweets, hashtags

# Aufgabe 3
# =============================

def aufgabe3(cfg, tweets, hashtags):
    # Importieren Sie die aufbereiteten Daten in Ihre Datenbank "Election".
    # Schreiben Sie hierzu ein Programm in einer Programmiersprache Ihrer
    # Wahl.
    try:
        conn = pg2.connect(host = cfg['host'],
                            user = cfg['user'],
                            password = cfg['pw'],
                            database = cfg['db'],
                            sslmode = 'require',
                            port = cfg['port']) # Verbindung
        cur = conn.cursor() # Kursor

        # Importiere die tweets
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

        # Importiere die Hashtags
        for ht in hashtags:
            cur.execute('''
            INSERT INTO hashtags(hname) VALUES ('{0}')
            '''.format(ht))
            print('#' + ht)
            cur.execute('''
            SELECT id FROM tweets WHERE text LIKE '%{0}%';
            '''.format('#' + ht))
            ids = cur.fetchall() # touple of ids
            for i in ids:
                cur.execute('''
                INSERT INTO contains(hname, id) VALUES ('{0}', '{1}')
                '''.format(ht, i[0]))
        conn.commit()
    except:
        print 'ConnectionProblem'


def main():
    cfg = {'host': '192.168.178.60',
           'user': 'elecuser',
           'pw': 'elecpass',
           'db': 'elections',
           'port': '5432'}
    aufgabe1(cfg)
    tweets, hashtags = aufgabe2()
    aufgabe3(cfg, tweets, hashtags)


if __name__ == '__main__':
    main()