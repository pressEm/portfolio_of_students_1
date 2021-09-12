CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS info_student (
id integer PRIMARY KEY AUTOINCREMENT,
study text NOT NULL,
work_ text NOT NULL,
about_student text NOT NULL,
url text NOT NULL,
date_ integer NOT NULL,
--time integer NOT NULL
user_id integer,
FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
id integer PRIMARY KEY AUTOINCREMENT,
author_id text NOT NULL,
location_id text NOT NULL,
content text NOT NULL,
date_ integer NOT NULL,
FOREIGN KEY (location_id) REFERENCES users(id)
);