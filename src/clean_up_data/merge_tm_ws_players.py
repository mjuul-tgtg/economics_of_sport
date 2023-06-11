from datetime import datetime
import logging

import pymysql



def insert_player(name, nationality, posistion, birth_year, height, ws_is, tm_id):

    name = str(name).replace("'","''")

    try:
        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd='password', db='economics_of_sports')
        cur = conn.cursor()

        query = "INSERT INTO player (`name`,`nationality`,`posistion`,`birth_year`,`heigt`,`ws_id`,`tm_id`) VALUES ('%s', '%s', '%s', '%s', '%s','%s', '%s');"
        final_query = query % (name, nationality, posistion, convert_date_format(birth_year), height, ws_is, tm_id)

        cur.execute(final_query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.info("Error with query for id : " + str(id))
        logging.error(e)



def get_tm_player_by_name(name):
    conn = pymysql.connect(host='localhost', user='root',
                           passwd="password", db='economics_of_sports')
    cur = conn.cursor()
    cur.execute("select * from tm_player where player_name = '" + name +"'")
    data = list(cur.fetchall())
    conn.close()
    return data
    # %%

def get_all_players_ws():
    conn = pymysql.connect(host='localhost', user='root',
                           passwd="password", db='economics_of_sports')
    cur = conn.cursor()
    cur.execute('''select * from ws_player''')
    data = list(cur.fetchall())
    conn.close()
    return data
    # %%

def convert_date_format(date):
    """
    This function converts date from 'DD-MM-YYYY' format to 'YYYY-MM-DD' format.

    :param date: str
        Date in 'DD-MM-YYYY' format
    :return: str
        Date in 'YYYY-MM-DD' format
    """
    original_date = datetime.strptime(date, "%d-%m-%Y")
    converted_date = datetime.strftime(original_date, "%Y-%m-%d")
    return converted_date

if __name__ == "__main__":
    all_ws_players = get_all_players_ws()

    for ws_player in all_ws_players:
        try:
            tm_player = get_tm_player_by_name(ws_player[1])
            insert_player(ws_player[1],ws_player[3],ws_player[4],ws_player[5],ws_player[2],ws_player[0],tm_player[0][0])
        except Exception as e:
            logging.error(e)





