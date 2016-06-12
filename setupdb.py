#!/usr/bin/env python3

import sys
try:
    import psycopg2
    postgres = True
except:
    import sqlite3
    postgres = False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("You must supply the database name as the first argument")
        sys.exit()
    if postgres:
        conn = psycopg2.connect(sys.argv[1])
        c = conn.cursor()
        c.execute("""CREATE TABLE admins
        (
          admin_id bigserial NOT NULL,
          user_id integer NOT NULL,
          level smallint NOT NULL DEFAULT 1,
          CONSTRAINT admins_pkey PRIMARY KEY (admin_id),
          CONSTRAINT admins_user_id_key UNIQUE (user_id)
        );""")
        c.execute("""CREATE TABLE posts_per_channel
        (
          post_id bigserial NOT NULL,
          replyto_id integer,
          channel_id integer NOT NULL,
          message_id integer NOT NULL,
          contenttype text,
          contenttext text,
          file_id text,
          CONSTRAINT posts_per_channel_pkey PRIMARY KEY (post_id)
        );""")
        c.execute("""CREATE TABLE channels
        (
          channel_id bigserial NOT NULL,
          channelname text NOT NULL,
          channelurl text,
          CONSTRAINT channels_pkey PRIMARY KEY (channel_id)
        );""")
    else:
        conn = sqlite3.connect(sys.argv[1])
        c = conn.cursor()
        c.execute("""CREATE TABLE "Channels" (
        `Channel_ID`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `ChannelName`   TEXT NOT NULL,
        `ChannelURL`    TEXT NOT NULL UNIQUE
        );""")
        c.execute("""CREATE TABLE `Posts_per_Channel` (
        `Post_ID`       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `Replyto_ID`    INTEGER,
        `Channel_ID`    INTEGER NOT NULL,
        `Message_ID`    INTEGER NOT NULL,
        `ContentType`   TEXT NOT NULL,
        `ContentText`   TEXT NOT NULL,
        `File_ID`       TEXT
        );""")
        c.execute("""CREATE TABLE `Admins` (
        `Admin_ID`  INTEGER NOT NULL UNIQUE,
        `User_ID` INTEGER NOT NULL UNIQUE,
        `Level` INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY(Admin_ID)
        );""")
        conn.commit()
        conn.close()
