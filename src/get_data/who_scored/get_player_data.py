import logging
import re
import time
from random import randint
from time import sleep

import pymysql
import requests
from bs4 import BeautifulSoup as bs
import cloudscraper

mysql_code = 'password'

def getDataLocal(i, team):
    #url = BASE_URL % (name, str(id))
    HTMLFileToBeOpened = open("player_data/" + team + "/" + str(i) +".html", "r")
    # Reading the file and storing in a variable
    contents = HTMLFileToBeOpened.read()
    #page = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(contents, "html.parser")

    name = get_name(soup).strip()
    height = str(get_heigt(soup)).strip()
    nationality = get_nationality(soup).strip()
    position = get_position(soup).strip()
    birth_date = str(get_birth_date(soup)).strip()

    print("Name: ", name)
    print("Height: ", height)
    print("Nationality: ", nationality)
    print("Position: ", position)
    print("Birth Date: ", birth_date)

    update_static_player_stats(name, height, nationality, position, birth_date)

    playerId = getPlayerId()[0][0]

    tbody = soup.find("tbody", {"id": "player-table-statistics-body"})
    rows = tbody.find_all('tr')

    for row in rows:
        season = str(checkForNull(get_season(row))).strip()
        team = checkForNull(get_team(row)).strip()
        rating = checkForNull(get_rating(row))
        minutes_played = checkForNull(get_min_played(row))
        goals = checkForNull(get_goal(row))
        assists = checkForNull(get_assist(row))
        yellow_cards = checkForNull(get_yellow(row))
        red_cards = checkForNull(get_red(row))
        shots = checkForNull(get_shots(row))
        pass_success_rate = checkForNull(get_pass_success(row))
        motm_awards = checkForNull(get_motm(row))
        tournament = checkForNull(get_tournement(row)).strip()

        print("Season: ", season)
        print("Team: ", team)
        print("Rating: ", rating)
        print("Minutes Played: ", minutes_played)
        print("Goals: ", goals)
        print("Assists: ", assists)
        print("Yellow Cards: ", yellow_cards)
        print("Red Cards: ", red_cards)
        print("Shots: ", shots)
        print("Pass Success Rate: ", pass_success_rate)
        print("Man of the Match Awards: ", motm_awards)
        print("Tournament: ", tournament)
        print("---------------------")

        add_season_stats(playerId, season, team, rating, minutes_played, goals, assists, yellow_cards, red_cards, shots, pass_success_rate, motm_awards, tournament);


def update_static_player_stats(name, height, nationality, position, birth_date):
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                           passwd=mysql_code, db='economics_of_sports')
    cur = conn.cursor()

    query = "INSERT INTO ws_player (`name`,`height`,`nationality`,`position`,`birth_date`) VALUES ('%s', '%s', '%s', '%s', '%s');"
    final_query = query % (name, height, nationality, position, birth_date)

    cur.execute(final_query)
    conn.commit()
    cur.close()
    conn.close()


def add_season_stats(playerId, season, team, rating, minutes_played, goals, assists, yellow_cards, red_cards, shots, pass_success_rate, motm_awards, tournament):
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                           passwd=mysql_code, db='economics_of_sports')
    cur = conn.cursor()

    query = "INSERT INTO ws_season (`ws_player_id`, `season`,`team`,`rating`,`minutes_played`,`goals`,`assists`,`yellow_card`,`red_card`,`shots`,`pass_sucess_rate`,`motm_awards`,`tournament`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s','%s', '%s');"
    final_query = query % (playerId, season, team, rating, minutes_played, goals, assists, yellow_cards, red_cards, shots, pass_success_rate, motm_awards, tournament)

    cur.execute(final_query)
    conn.commit()
    cur.close()
    conn.close()

def checkForNull(value):
    if value is 'None':
        return 0
    if value is None:
        return 0
    if value == '-\t':
        return 0
    if value == '-':
        return 0
    return value


def get_season(row):
    try:
        return row.find("td", {"class": "col12-lg-1 col12-m-1 col12-s-2 col12-xs-2 grid-abs overflow-text"}).text
    except Exception as e:
        logging.info(e)

def get_team(row):
    try:
        return row.find("a", {"class": "team-link"}).text
    except Exception as e:
        logging.info(e)

def get_rating(row):
    try:
        return row.find("td", {"class": "rating"}).text
    except Exception as e:
        logging.info(e)

def get_min_played(row):
    try:
        return row.find("td", {"class": "minsPlayed"}).text
    except Exception as e:
        logging.info(e)

def get_goal(row):
    try:
        return row.find("td", {"class": "goal"}).text
    except Exception as e:
        logging.info(e)

def get_assist(row):
    try:
        return row.find("td", {"class": "assistTotal"}).text
    except Exception as e:
        logging.info(e)

def get_yellow(row):
    try:
        return row.find("td", {"class": "yellowCard"}).text
    except Exception as e:
        logging.info(e)

def get_red(row):
    try:
        return row.find("td", {"class": "redCard"}).text
    except Exception as e:
        logging.info(e)

def get_shots(row):
    try:
        return row.find("td", {"class": "shotsPerGame"}).text
    except Exception as e:
        logging.info(e)

def get_pass_success(row):
    try:
        return row.find("td", {"class": "passSuccess"}).text
    except Exception as e:
        logging.info(e)

def get_arial(row):
    try:
        return row.find("td", {"class": "aerialWonPerGame"}).text
    except Exception as e:
        logging.info(e)

def get_motm(row):
    try:
        return row.find("td", {"class": "manOfTheMatch"}).text
    except Exception as e:
        logging.info(e)

def get_tournement(row):
    try:
        return str(row).split('/Tournaments/')[1].split('/')[1].split('">')[0]
    except Exception as e:
        logging.info(e)

def get_name(data):
    try:
        return str(data).split('Name: </span>')[1].split('</div>')[0].replace('\n','')
    except Exception as e:
        logging.info(e)

def get_heigt(data):
    try:
        return str(data).split('Height: </span>')[1].split('cm')[0].replace('\n','')
    except Exception as e:
        logging.info(e)

def get_nationality(data):
    try:
        return str(data).split('Nationality: </span>')[1].split('>')[1].split(' <')[0].replace('\n','')
    except Exception as e:
        logging.info(e)

def get_position(data):
    try:
        return str(data).split('Positions:')[1].split('<span style="display: inline-block;">')[1].split('</span>')[0].replace('\n','')
    except Exception as e:
        logging.info(e)

def get_birth_date(data):
    try:
        return str(data).split('>Age: ')[1].split('<i>')[1].split('</i>')[0].replace('\n','')
    except Exception as e:
        logging.info(e)

def save_to_db(name, url):
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                           passwd=mysql_code, db='economics_of_sports')
    cur = conn.cursor()

    query = "INSERT INTO ws_team (`name`,`link`) VALUES ('%s', '%s');"
    final_query = query % (name, url)

    cur.execute(final_query)
    conn.commit()
    cur.close()
    conn.close()

def getPlayerId():
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                           passwd=mysql_code, db='economics_of_sports')
    cur = conn.cursor()
    cur.execute(
        """select id from ws_player order by id desc limit 1 ;
            """)
    data = list(cur.fetchall())
    conn.close()
    return data

if __name__ == "__main__":

    teams = ['arsenal', 'aston_villa', 'bournemouth', 'brentford', 'brigthon', 'chelsea', 'crystal_palace', 'everton',
             'fullham', 'leeds', 'leicester', 'liverpool', 'man_city', 'man_united', 'newcastle', 'notthingham_forrest',
             'southampton', 'tottenham', 'west_ham', 'wolverhampton']

    for team in teams:

        for i in range(0,33):
            try:
                getDataLocal(i, team)
            except Exception as e:
                print(e)
