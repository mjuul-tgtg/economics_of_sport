import logging
from datetime import datetime

import pymysql


def do(dates, player_id):
    dates = [item[0] for item in dates]

    # Convert dates to datetime objects
    datetime_dates = [datetime.strptime(date, "%b %d, %Y") for date in dates]
    sorted_dates = sorted(datetime_dates, reverse=True)

    # Group dates by year
    dates_by_year = {}
    for date in sorted_dates:
        year = date.year
        if year not in dates_by_year:
            dates_by_year[year] = []
        dates_by_year[year].append(date)

    # Find the closest date to July 1 for each year
    closest_dates = {}
    for year, year_dates in dates_by_year.items():
        target_date = datetime(year, 9, 1)
        closest_date = min(year_dates, key=lambda d: abs(target_date - d))
        closest_dates[year] = closest_date

    # Print the closest dates
    for year, closest_date in closest_dates.items():
        add_season_to_graph(player_id[0], year, closest_date.strftime('%b %d, %Y').replace(' 0', ' ') )



def add_season_to_graph(player_id, year, date):
    print(player_id)
    print(date)
    print(year)

    try:

        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd='password', db='economics_of_sports')
        cur = conn.cursor()

        query = "update tm_market_value_raw set season = " + str(year) + " where tm_player_id = " + str(player_id) + " and date = '" + str(date) + "'"
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(e)

def get_dates_by_player(player_id):
    conn = pymysql.connect(host='localhost', user='root',
                           passwd="password", db='economics_of_sports')
    cur = conn.cursor()
    sql = "select tm_market_value_raw.date from tm_market_value_raw where tm_player_id = " + str(player_id[0])
    cur.execute(sql)
    data = list(cur.fetchall())
    conn.close()
    return data

def get_player_ids():
    conn = pymysql.connect(host='localhost', user='root',
                           passwd="password", db='economics_of_sports')
    cur = conn.cursor()
    cur.execute("select distinct tm_player_id from tm_market_value_raw")
    data = list(cur.fetchall())
    conn.close()
    return data

player_ids = get_player_ids()

for player_id in player_ids:
    dates = get_dates_by_player(player_id)
    do(dates, player_id)