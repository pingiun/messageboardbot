#!/usr/bin/env python3

import sys
import sqlite3

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("You must supply the database name as the first argument")
		sys.exit()
	conn = sqlite3.connect(sys.argv[1])
	c = conn.cursor()
	c.execute("""CREATE TABLE "Channels" (
	`Channel_ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`ChannelName`	TEXT NOT NULL,
	`ChannelURL`	TEXT NOT NULL UNIQUE
)""")
	c.execute("""CREATE TABLE "Posts_per_Channel" (
	`Post_ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Replyto_ID`	INTEGER,
	`Channel_ID`	INTEGER NOT NULL,
	`ContentType`	TEXT NOT NULL,
	`Message_ID`	INTEGER NOT NULL UNIQUE
)""")
	conn.commit()
	conn.exit()
