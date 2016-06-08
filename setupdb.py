#!/usr/bin/env python3

import sys
import sqlite3

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("You must supply the database name as the first argument")
		sys.exit()
	conn = sqlite3.connect(sys.argv[1])
	c = conn.cursor()
	c.execute("CREATE TABLE Channels (Channel_ID integer, ChannelName text, ChannelURL text)")
	c.execute("CREATE TABLE Posts_per_Channel (Post_ID integer, Replyto_ID integer, Channel_ID integer, ContentType text)")
	conn.commit()
	conn.exit()
