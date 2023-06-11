import logging
import time
from random import randint

import pymysql
import requests
from bs4 import BeautifulSoup as bs

BASE_URL = 'https://www.transfermarkt.com/%s/marktwertverlauf/spieler/%s'
mysql_code = 'password'


def getDataLocal(id, name):
    # url = BASE_URL % (name, str(id))
    HTMLFileToBeOpened = open("test_soup_player.html", "r")
    # Reading the file and storing in a variable
    contents = HTMLFileToBeOpened.read()
    # page = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(contents, "html.parser")

    str_soup = str(soup)

    data = str(str_soup.split("x20value")[1])

    data = data.split("'y'")

    for i in range(1, len(data)):
        unpack_data(data[i])


def getData(tm_id, tm_name, id):
    url = BASE_URL % (tm_name, str(tm_id))
    page = requests.get(url, headers={
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(page.content, "html.parser")

    player_name = soup.find("div", {"class": "modal__content"}).find("img")['title']

    update_player_name(player_name, id)

    str_soup = str(soup)
    data = str(str_soup.split("x20value")[1])
    data = data.split("'y'")

    for i in range(1, len(data)):
        club, age, market_value, date = unpack_data(data[i])

        save_to_db(id, club, market_value, date, age)


def unpack_data(data):
    # club = clean_up_string(data.split("'verein': '")[1].split("',")[0])
    club = clean_up_string(data.split("verein")[1].split("',")[0]).replace("':'", '')
    # age = clean_up_string(data.split("'age': '")[1].split("',")[0])
    age = clean_up_string(data.split("age")[1].split("',")[0]).replace("':'", '')
    market_value = convert_value_to_nuber(clean_up_string(data.split('mw')[1].split("',")[0]).replace("':'", ''))
    date = clean_up_string(data.split("datum_mw'")[1].split("',")[0]).replace("':'", '').replace(":'", "")

    return club, age, market_value, date


def convert_value_to_nuber(value):
    if 'k' in value:
        return int(str(value).replace('k', '000'))
    if 'm' in value:
        return int(str(value).replace('m', '0000').replace('.', ''))


def clean_up_string(input_string):
    input_string = str(input_string).replace('\\u20ac', '').replace('\\u20AC', '')
    cleaned_string = input_string.encode('utf-8').decode('unicode_escape')
    return cleaned_string


def update_player_name(player_name, id):
    try:
        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd=mysql_code, db='economics_of_sports')
        cur = conn.cursor()

        query = "update tm_player set player_name = '%s' where id = '%s'"
        final_query = query % (player_name, id)

        cur.execute(final_query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.info("Error with query for id : " + str(id))
        logging.error(e)


def save_to_db(id, club, market_value, date, age):
    try:
        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd=mysql_code, db='economics_of_sports')
        cur = conn.cursor()

        query = "INSERT INTO tm_market_value_raw (`tm_player_id`,`team_name`,`market_value`,`date`,`player_age`) VALUES ('%s', '%s', '%s', '%s', '%s');"
        final_query = query % (id, club, market_value, date, age)

        cur.execute(final_query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.info("Error with query for id : " + str(id))
        logging.error(e)


def get_players():
    conn = pymysql.connect(host='localhost', user='root',
                           passwd="password", db='economics_of_sports')
    cur = conn.cursor()
    cur.execute('''SElECT tm_id, tm_name, tm_player.id FROM tm_player
left join tm_market_value_raw tmvr on tm_player.id = tmvr.tm_player_id
where tmvr.id is null''')
    data = list(cur.fetchall())
    conn.close()
    return data
    # %%


if __name__ == "__main__":
    data = get_players()

    for d in data:
        try:
            time.sleep(randint(3, 6))
            getData(d[0], d[1], d[2])
        except Exception as e:
            print(e)