#!/usr/bin/env python

import sqlite3
import os

def main():
		os.remove("database/dota.db")
		os.remove("database/files.db")
		conn1 = sqlite3.connect("database/dota.db")
		conn2 = sqlite3.connect("database/files.db")
		cur1 = conn1.cursor()
		cur2 = conn2.cursor()
		cmd1 = open("schema/dota_schema.txt").read()
		cmd2 = open("schema/file_db_schema.txt").read()
		cmd3 = open("schema/player_info.txt").read()
		cur1.executescript(cmd1)
		cur1.executescript(cmd3)
		cur2.execute(cmd2)
		conn1.close()
		conn2.close()

if __name__ == "__main__":
		main()

		
