import logging
import re
import time
from random import randint
from time import sleep

import pymysql
import requests
from bs4 import BeautifulSoup as bs

BASE_URL = 'https://www.transfermarkt.com/%s/marktwertverlauf/spieler/%s'
mysql_code = 'password'


def getDataLocal():
    #url = BASE_URL % (name, str(id))
    HTMLFileToBeOpened = open("test_soup_leage.html", "r")
    # Reading the file and storing in a variable
    contents = HTMLFileToBeOpened.read()
    #page = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(contents, "html.parser")
    teams = soup.find_all("td", {"class": "hauptlink no-border-links"})

    for team in teams:
        unpack_team_data(team)

def unpack_team_data(data):
    a = data.findNext('a')

    name = a['title']
    link = a['href']
    print(name)
    print(link)
    save_to_db(name,link)

def getData(url):
    url = url
    page = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
    soup = bs(page.content, "html.parser")
    teams = soup.find_all("td", {"class": "hauptlink no-border-links"})

    for team in teams:
        unpack_team_data(team)

def clean_up_string(input_string):
    input_string = str(input_string).replace('\\u20ac', '').replace('\\u20AC', '')
    cleaned_string = input_string.encode('utf-8').decode('unicode_escape')
    return cleaned_string


def save_to_db(name, url):

    try:
        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd=mysql_code, db='economics_of_sports')
        cur = conn.cursor()

        query = "INSERT INTO tm_team (`name`,`url`) VALUES ('%s', '%s');"
        final_query = query % (name, url)

        cur.execute(final_query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.info("Error with query for id : " + str(id))
        logging.error(e)



if __name__ == "__main__":
    getData('https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1')
    #getDataLocal()