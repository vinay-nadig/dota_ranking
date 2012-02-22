#!/usr/bin/env python
""" Script to parse dota details from file
		and store values in database. """

# Import the required modules
import sqlite3
import os
import herolist
from linecache import getline, clearcache
from lib import classes


# Establish the connections to the databases
conn1 = sqlite3.connect("database/dota.db")
conn2 = sqlite3.connect("database/files.db")
conn3 = sqlite3.connect("database/heroes.db")
cur1 = conn1.cursor()
cur2 = conn2.cursor()
cur3 = conn3.cursor()
clearcache()

# dic defining code for each player
dic = {  'shi' : 'shinigami',
				'bud' : 'buddhenator',
				'sle' : 'sleepy',
				'kri' : 'krishtalysis',
				'mon' : 'monk',
				'mar' : 'marvin',
				'whi' : 'whiplash',
				'mas' : 'massino(spark)',
				'911' : '911',
				'kra' : 'krazzy',
				'rge' : 'rgenx',
				'lee' : 'leeonidas',
				'bli' : 'blinken',
				'ind' : 'inductor',
				'mrc' : 'mrc[labrinth]'}
			


def main():
		new_files = file_db_maintain()
		cur2.execute("select * from files")
		if(new_files):																			# if there are new games
				for _file in new_files:													# for each game
						game = classes.Game()
						file_parser("file_dir/" + _file, game)
#		upload_player_stats()
		write_html()
		herolist.main()
		conn1.commit()
		conn1.close()
		conn2.commit()
		conn2.close()

def write_html():
		fp = open("html/ranking.html", "w")
		template = open("html/ranking_template.txt", "r").read()

		cur1.execute("select * from player order by points desc")
		to_write = ""
		rank = 1
		for row in cur1.fetchall():
				if(row[5]):
						to_write += "<tr><td>" + str(rank) + "</td><td>" + str(row[0]) + "</td><td>" + str(row[1]) + "</td><td>" + str(row[2]) + "</td><td>" + str(row[3]) + "</td><td>" + str(row[4]) + "</td><td>" +  str(row[5]) + "</td><td>" + str(row[6]) + "</td></tr>"
						rank += 1

		template = template.replace("PLACEHOLDER", to_write)
		fp.write(template)

		fp.close()

# Uploads value to the Player table
def upload_player_stats1(player, game, points):
		t = (player.pid,)
		cur1.execute("select count(*) from gameplay where pid=?", t)
		tot_matches = cur1.fetchall()[0][0]
		cur1.execute("select sum(Kills) from gameplay where pid=?", t)
		tot_Kills = cur1.fetchall()[0][0]
		cur1.execute("select sum(Deaths) from gameplay where pid=?", t)
		tot_Deaths = cur1.fetchall()[0][0]
		cur1.execute("select sum(Assists) from gameplay where pid=?", t)
		tot_Assists = cur1.fetchall()[0][0]
		t = (tot_Kills, tot_Deaths, tot_Assists, tot_matches, player.pid)
		cur1.execute("update player set Total_Kills=?, Total_Deaths=?, Total_Assists=?, Total_Matches=? where Id=?", t)


# Uploads value to the Game table
def upload_game_info(game):
		t = (game.Id, game.map_name, game.datetime, game.game_name, game.host_name, game.duration, game.mode, game.no_of_players, game.winner)
		cur1.execute("Insert into Game values(?,?,?,?,?,?,?,?,?)", t)    
		 
				
# Uploads values into gameplay gtables
def upload_player_info(player, game, player_code):
		# to check if he is a new player
		if(player_code in dic.keys()):
				t = (dic[player_code],)
				cur1.execute("select id from player where name=?", t)
				player.pid = cur1.fetchall()[0][0]
		else:
				response = raw_input("Enter %s into database?(y or n)"%player.name)
				if(response.strip().lower() == 'n'):
						return
				else:
						cur1.execute("select max(id) from player")
						player.pid = cur1.fetchall()[0][0] + 1
						t = (player.pid, player.name, 0, 0, 0 ,0, 100)
						cur1.execute("insert into player values(?,?,?,?,?,?,?)", t)
						dic[player_code] = player.name
#		try:
#				t = (dic[player_code],)
#				cur1.execute("select id from player where name=?", t)
#				player.pid = cur1.fetchall()[0][0]
		# if he is a new player, create a new id and add to database
#		except:
#				cur1.execute("select max(id) from player")
#				player.pid = cur1.fetchall()[0][0] + 1
#				t = (player.pid, player.name, 0, 0, 0, 0, 0)
#				cur1.execute("insert into player values(?,?,?,?,?,?,?)", t)
#				dic[player_code] = player.name
		t = (player.hero,)
		cur3.execute("select cp, sp, dm from heroes where name=?", t)
		res = cur3.fetchall()
		# for newly added maps and heroes
		try:
				cp, sp, dm = res[0][0], res[0][1], res[0][2]
		except:
				cp, sp, dm = 0.5, 0.5, 0.5
		t = (game.Id, player.pid, player.item_list[0], player.item_list[1], player.item_list[2], player.item_list[3], player.item_list[4], player.item_list[5], player.kills, player.deaths, player.hero, player.ck, player.cd, player.assists, player.gold, player.nk)
		cur1.execute("insert into gameplay values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t)
		t = (player.pid,)
		cur1.execute("select count(*) from gameplay where pid=?", t)
		tot_matches = cur1.fetchall()[0][0]
		cur1.execute("select points from player where id=?", t)
		points = cur1.fetchall()[0][0]
		if(player.team.strip() == game.winner.strip()):
				points = points + (cp*player.kills + sp*player.assists - 2*dm*player.deaths + 1)
		else:
				points = points + (cp*player.kills + sp*player.assists - 2*dm*player.deaths)
		upload_player_stats1(player, game, points)

# Function to maintain the file database.
def file_db_maintain():
		ls_of_files1 = os.listdir("file_dir/")
		cur2.execute("select * from files")	
		res = cur2.fetchall()
		ls_of_files2 = [i[1] for i in res]
		ls_of_new_files = list(set(ls_of_files1) - set(ls_of_files2))
		if(ls_of_new_files):
				for f in ls_of_new_files:
						t = (hash(f).__abs__(),f)
						cur2.execute("insert into files values(?,?)", t)
				return ls_of_new_files
		
# function that extracts variables from the parsed file
def file_parser(filename, game):
		cur1.execute("select Name from Player")
		res = cur1.fetchall()
		ls_of_all_players = [x[0] for x in res]
		game.datetime = getline(filename, 5).rstrip()
		game.Id = int("".join([x for x in game.datetime if x in ['0','1','2','3','4','5','6','7','8','9']]))
		game.map_name = getline(filename, 1).rstrip()
		game.game_name = getline(filename, 7).rstrip()
		game.host_name = getline(filename, 6).rstrip()
		game.duration = getline(filename, 4).rstrip()
		game.mode = getline(filename, 3).rstrip()
		game.no_of_players = int(getline(filename, 8).rstrip()[0]) + int(getline(filename, 8).rstrip()[2])
		game.winner = getline(filename, 9).rstrip()
		upload_game_info(game)
		for player_no in range(1, game.no_of_players+1):
				info = getline(filename, player_no + 10).split("|")
				player_name = info[0].strip()
				player_code = player_name[:3].strip().lower()
				# Create a new instance of a player
				player = classes.Player()
				player.hero = info[3].strip()
				player.name = player_name
				player.team = info[1]
				player.gold = int(info[4])
				player.lvl = int(info[6].rstrip())
				player.item_list = info[5].split(",")[:-1]
				stats = info[2]
				stats = stats.replace("CS:", "/")
				player_stats = "".join([x for x in stats if x in ['0','1','2','3','4','5','6','7','8','9','/']]).split("/")
				player.kills = int(player_stats[0])
				player.deaths = int(player_stats[1])
				player.assists = int(player_stats[2])
				player.ck = int(player_stats[3])
				player.cd = int(player_stats[4])
				player.nk = int(player_stats[5])
				upload_player_info(player, game, player_code)
		moderate_points(game)

def moderate_points(game):
		dic_of_temp_scores = {}
		dic_of_final_points = {}
		dic_of_points = {}
		max_score = game.no_of_players*5
		total_g, total_l = 0, 0
		dic_of_stats = {}
		t = (game.Id,)
		cur1.execute("select pid from gameplay where gid=?", t)
		res = cur1.fetchall()
		for i in res:
				t = (game.Id, i[0])
				cur1.execute("select kills, deaths, assists, hero from gameplay where gid=? and pid=?", t)
				res1 = cur1.fetchall()
				dic_of_stats[i[0]] = (res1[0][0], res1[0][1], res1[0][2], res1[0][3])
		for i in dic_of_stats:
				t = (dic_of_stats[i][3],)
				cur3.execute("select cp, sp, dm from heroes where name=?", t)
				res = cur3.fetchall()
				if(res):
						cp, sp, dm = res[0][0], res[0][1], res[0][2]
				else:
						cp, sp, dm = 0.5, 0.5, 0.5
				dic_of_temp_scores[i] = ((dic_of_stats[i][0]*cp + dic_of_stats[i][2]*sp), (-dm*dic_of_stats[i][1]))
		for i in dic_of_temp_scores:
				total_g += dic_of_temp_scores[i][0]
				total_l += abs(dic_of_temp_scores[i][1])
		for i in dic_of_temp_scores:
				dic_of_points[i] = ((((dic_of_temp_scores[i][0]/total_g)*max_score)-5), (((dic_of_temp_scores[i][1]/total_l)*max_score)+5))
		for i in dic_of_points:
				cur1.execute("select points from player where player.id=?", (i,))
				points = cur1.fetchall()[0][0]
				dic_of_final_points[i] = points + dic_of_points[i][0] + dic_of_points[i][1]
				t = (round(dic_of_final_points[i], 2), i)
				cur1.execute("update player set points=? where id=?", t)


		
		
if __name__ == "__main__":
		main()
