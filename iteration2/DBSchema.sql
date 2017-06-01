CREATE TABLE tweets (
    handle           varchar(15) NOT NULL,
    text             varchar(500) NOT NULL,
    time             date NOT NULL,
    retweet_count    integer,
    favorite_count  integer,
    truncated        boolean,
    id               serial PRIMARY KEY);

CREATE TABLE contains (
    hname varchar(140) NOT NULL,
    id integer NOT NULL);


CREATE TABLE hashtags (
    hname varchar(140) NOT NULL);

