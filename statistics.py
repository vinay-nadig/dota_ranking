
import sqlite3

def hero_img(hero):
    return '''<img height="14" width="28" src="http://www.gosugamers.net/bilder/heroes/GosuGamers-[''' + \
                                            hero.replace(' ', '%20') + '''].png"'''

def main():
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
        hero_dict[player_dict[t[0]]].append(hero_img(t[1]) + ''' title = "''' + str(t[1]) + '(' + str(t[2]) + '/' + str(t[3]) + '/' + str(t[4]) + ')' + '''" />''')

        if t[1] not in hero_count.keys():
            hero_count[t[1]] = 0
        hero_count[t[1]] += 1
    

    toreplace = '''<table id = "box-table-a"><tr><th>Name</th><th>Heroes</th></tr>'''


    for player, heroes in hero_dict.items():
        toreplace += "<tr><td>" + player + "</td><td>"
        br_count = 0
        for h in heroes:
            if br_count == 10:
                toreplace += "<br />"
                br_count = 0
            br_count += 1
            toreplace += h
        toreplace += "</td></tr>"
    toreplace += "</table>"

    toreplace_2 = '''<table id = "box-table-a"><tr><th>Hero</th><th>Count</th></tr>'''


    sorted_hero_count = sorted(hero_count.items(), key = lambda(k,v):(v,k), reverse = True)

    for hero, count in sorted_hero_count:
        toreplace_2 += "<tr><td>" + hero + " "+ hero_img(hero) + '''title = "''' + str(hero) + '''" />''' + '''</td><td>''' + str(count) + "</td></tr>"
    toreplace_2 += "</table>"
            

    # Write the HTML file
    fp = open("html/statistics.html", "w")
    template = open("html/statistics_template.txt", "r").read()
    template = template.replace("PLACEHOLDERTABLE1", toreplace)
    template = template.replace("PLACEHOLDERTABLE2", toreplace_2)

    fp.write(template)
    fp.close()

if __name__ == '__main__':
    main()
