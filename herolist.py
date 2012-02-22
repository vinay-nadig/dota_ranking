import sqlite3

if __name__ == '__main__':
    connection = sqlite3.connect("database/dota.db")
    cursor = connection.cursor()
    cursor.execute("select Id, Name from Player")

    # (PID, Name)
    player_dict = {}
    for t in cursor.fetchall():
        player_dict[t[0]] = t[1]

    cursor.execute("select Pid, Hero, Kills, Deaths, Assists from Gameplay")
    # (Id, Hero)
    hero_dict = {}
    # (Hero, Count)
    hero_count = {}
    for t in cursor.fetchall():
        if player_dict[t[0]] not in hero_dict.keys():
            hero_dict[player_dict[t[0]]] = []
        hero_dict[player_dict[t[0]]].append('''<img height = "14" width = "28" src="http://www.gosugamers.net/bilder/heroes/GosuGamers-[''' + \
                                            t[1].replace(' ', '%20') + '''].png" title = "''' + str(t[1]) + '(' + str(t[2]) + '/' + str(t[3]) + '/' + str(t[4]) + ')' + '''" />''')

        if t[1] not in hero_count.keys():
            hero_count[t[1]] = 0
        hero_count[t[1]] += 1
    

    toreplace = '''<table id = "box-table-a"><tr><th>Name</th><th>Heroes</th></tr>'''
    
    for player, heroes in hero_dict.items():
        toreplace += "<tr><td>" + player + "</td><td>"
        for h in heroes:
            toreplace += h
        toreplace += "</td></tr>"
    toreplace += "</table>"

    toreplace_2 = '''<table id = "box-table-a"><tr><th>Hero</th><th>Count</th></tr>'''

    for hero, count in hero_count.items():
        toreplace_2 += "<tr><td>" + hero + " "+ '''<img height = "14" width = "28" src="http://www.gosugamers.net/bilder/heroes/GosuGamers-[''' + \
                      hero.replace(' ', '%20') + '''].png" title = ''' + hero + '''" />''' + '''</td><td>''' + str(count) + "</td></tr>"
        

    toreplace_2 += "</table>"
            

    # Write the HTML file
    fp = open("html/heroes.html", "w")
    template = open("html/heroes_template.txt", "r").read()
    template = template.replace("PLACEHOLDERTABLE1", toreplace)
    template = template.replace("PLACEHOLDERTABLE2", toreplace_2)

    fp.write(template)
    fp.close()

