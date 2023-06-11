import logging
import re
import time
from random import randint
from time import sleep

import pymysql
import requests
from bs4 import BeautifulSoup as bs

BASE_URL = 'https://www.transfermarkt.com'
mysql_code = 'password'


def getDataLocal(team_id):
    #url = BASE_URL % (name, str(id))
    HTMLFileToBeOpened = open("test_soup_team.html", "r")
    # Reading the file and storing in a variable
    contents = HTMLFileToBeOpened.read()
    #page = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(contents, "html.parser")
    players = soup.find_all("td", {"class": "rechts hauptlink"})

    for player in players:
        unpack_player_data(team_id, player)


def unpack_player_data(team_id, data):
    id = str(data).split('spieler/')[1].split('">')[0]
    name = str(data).split('href="/')[1].split('/')[0]
    print(id)
    print(name)

    save_to_db(team_id, id, name)

def getData(team_id, url):
    url = BASE_URL + url
    page = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(page.content, "html.parser")
    players = soup.find_all("td", {"class": "rechts hauptlink"})

    for player in players:
        try:
            unpack_player_data(team_id, player)
        except Exception as e:
            print(e)


def clean_up_string(input_string):
    input_string = str(input_string).replace('\\u20ac', '').replace('\\u20AC', '')
    cleaned_string = input_string.encode('utf-8').decode('unicode_escape')
    return cleaned_string


def save_to_db(team_id, id, name):

    try:
        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd=mysql_code, db='economics_of_sports')
        cur = conn.cursor()

        query = "INSERT INTO tm_player (`team_id`,`tm_id`,`tm_name`) VALUES ('%s', '%s', '%s');"
        final_query = query % (team_id, id, name)

        cur.execute(final_query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.info("Error with query for id : " + str(id))
        logging.error(e)


def get_teams():
    conn = pymysql.connect(host='localhost', user='root',
                           passwd="password", db='economics_of_sports')
    cur = conn.cursor()
    cur.execute(
        "SElECT id, url FROM tm_team")
    data = list(cur.fetchall())
    conn.close()
    return data
    # %%



if __name__ == "__main__":

    data = get_teams()

    for d in data:
        time.sleep(randint(5,10))
        getData(d[0],d[1])

    #getData()
    #getDataLocal()