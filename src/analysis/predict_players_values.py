import logging

import pymysql
import pandas as pd
import shap as shap
import matplotlib.pyplot as plt

def get_data_from_player(id):
    # Set up the connection details
    hostname = 'localhost'
    username = 'root'
    password = 'password'
    database = 'economics_of_sports'

    # Create a connection
    connection = pymysql.connect(host=hostname,
                                 user=username,
                                 password=password,
                                 db=database)

    # Create a cursor
    cursor = connection.cursor()

    query = '''
    SELECT p.ws_id,
        tmvr.market_value,
        p.name,
        p.nationality,
        p.continent,
        p.heigt,
        IF(LOCATE(' (', p.posistion) = 0, p.posistion, LEFT(p.posistion, LOCATE(' (', p.posistion) - 1)) AS posistion,
        tmvr.player_age,
        p.nationality = l.country AS is_local,
        tmvr.season,
        ws_nl.tournament AS nl_tournament,
        ws_nl.elo_score AS nl_elo_score,
        ws_nl.rating AS nl_rating,
        ws_nl.minutes_played AS nl_minutes_played,
        ws_nl.motm_awards AS nl_motm_awards,
        ws_ec.tournament AS ec_tournament,
        ws_ec.elo_score AS ec_elo_score,
        ws_ec.rating AS ec_rating,
        ws_ec.minutes_played AS ec_minutes_played,
        ws_ec.motm_awards AS ec_motm_awards,
        ws_ntc.tournament AS ntc_tournament,
        ws_ntc.elo_score AS ntc_elo_score,
        ws_ntc.rating AS ntc_rating,
        ws_ntc.minutes_played AS ntc_minutes_played,
        ws_ntc.motm_awards AS ntc_motm_awards,
        ws_nc.tournament AS nc_tournament,
        ws_nc.elo_score AS nc_elo_score,
        ws_nc.rating AS nc_rating,
        ws_nc.minutes_played AS nc_minutes_played,
        ws_nc.motm_awards AS nc_motm_awards
    FROM player p
    LEFT JOIN tm_market_value_raw tmvr ON p.tm_id = tmvr.tm_player_id
    LEFT JOIN team t ON tmvr.team_name = t.name
    LEFT JOIN league l ON t.league_id = l.id
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'National Leagues'
    ) AS ws_nl ON ws_nl.ws_player_id = p.ws_id AND ws_nl.season = tmvr.season
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'European Cups'
    ) AS ws_ec ON ws_ec.ws_player_id = p.ws_id AND ws_ec.season = tmvr.season
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'National Team Cups'
    ) AS ws_ntc ON ws_ntc.ws_player_id = p.ws_id AND ws_ntc.season = tmvr.season
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'National Cups'
    ) AS ws_nc ON ws_nc.ws_player_id = p.ws_id AND ws_nc.season = tmvr.season
    WHERE ws_nl.season IS NOT NULL
    GROUP BY p.ws_id, tmvr.market_value, p.name, p.nationality, p.continent, p.heigt, posistion, tmvr.player_age, is_local, tmvr.season, nl_tournament, nl_elo_score, nl_rating, nl_minutes_played, nl_motm_awards, ec_tournament, ec_elo_score, ec_rating, ec_minutes_played, ec_motm_awards, ntc_tournament, ntc_elo_score, ntc_rating, ntc_minutes_played, ntc_motm_awards, nc_tournament, nc_elo_score, nc_rating, nc_minutes_played, nc_motm_awards 
    ORDER BY name, tmvr.season;
    '''

    # Execute a query to select all from the "employees" table
    cursor.execute(query=query)

    # Fetch all the rows
    rows = cursor.fetchall()

    # Get column names
    column_names = [i[0] for i in cursor.description]

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(rows, columns=column_names)

    # Close the cursor and connection
    cursor.close()
    connection.close()

    targets=df.market_value
    df[["nl_rating"]] = df[["nl_rating"]].apply(pd.to_numeric)
    df[["ec_rating"]] = df[["ec_rating"]].apply(pd.to_numeric)
    df[["ntc_rating"]] = df[["ntc_rating"]].apply(pd.to_numeric)
    df[["nc_rating"]] = df[["nc_rating"]].apply(pd.to_numeric)
    inputs=df.drop(['name','nl_tournament', 'ec_tournament', 'ntc_tournament', 'nc_tournament', 'market_value'],axis='columns')

    inputs = pd.get_dummies(inputs)

    ws_id = "ws_id_" + str(id)

    inputs = inputs[inputs[ws_id] == 1]
    cols_to_drop = inputs.filter(regex='^ws_id_').columns
    inputs = inputs.drop(cols_to_drop, axis=1)

    return inputs

def get_training_data_excluding_player_id(id):
    # Set up the connection details
    hostname = 'localhost'
    username = 'root'
    password = 'password'
    database = 'economics_of_sports'

    # Create a connection
    connection = pymysql.connect(host=hostname,
                                 user=username,
                                 password=password,
                                 db=database)

    # Create a cursor
    cursor = connection.cursor()

    query = '''
    SELECT p.ws_id,
        tmvr.market_value,
        p.name,
        p.nationality,
        p.continent,
        p.heigt,
        IF(LOCATE(' (', p.posistion) = 0, p.posistion, LEFT(p.posistion, LOCATE(' (', p.posistion) - 1)) AS posistion,
        tmvr.player_age,
        p.nationality = l.country AS is_local,
        tmvr.season,
        ws_nl.tournament AS nl_tournament,
        ws_nl.elo_score AS nl_elo_score,
        ws_nl.rating AS nl_rating,
        ws_nl.minutes_played AS nl_minutes_played,
        ws_nl.motm_awards AS nl_motm_awards,
        ws_ec.tournament AS ec_tournament,
        ws_ec.elo_score AS ec_elo_score,
        ws_ec.rating AS ec_rating,
        ws_ec.minutes_played AS ec_minutes_played,
        ws_ec.motm_awards AS ec_motm_awards,
        ws_ntc.tournament AS ntc_tournament,
        ws_ntc.elo_score AS ntc_elo_score,
        ws_ntc.rating AS ntc_rating,
        ws_ntc.minutes_played AS ntc_minutes_played,
        ws_ntc.motm_awards AS ntc_motm_awards,
        ws_nc.tournament AS nc_tournament,
        ws_nc.elo_score AS nc_elo_score,
        ws_nc.rating AS nc_rating,
        ws_nc.minutes_played AS nc_minutes_played,
        ws_nc.motm_awards AS nc_motm_awards
    FROM player p
    LEFT JOIN tm_market_value_raw tmvr ON p.tm_id = tmvr.tm_player_id
    LEFT JOIN team t ON tmvr.team_name = t.name
    LEFT JOIN league l ON t.league_id = l.id
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'National Leagues'
    ) AS ws_nl ON ws_nl.ws_player_id = p.ws_id AND ws_nl.season = tmvr.season
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'European Cups'
    ) AS ws_ec ON ws_ec.ws_player_id = p.ws_id AND ws_ec.season = tmvr.season
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'National Team Cups'
    ) AS ws_ntc ON ws_ntc.ws_player_id = p.ws_id AND ws_ntc.season = tmvr.season
    LEFT JOIN (
        SELECT * FROM ws_season
        WHERE type = 'National Cups'
    ) AS ws_nc ON ws_nc.ws_player_id = p.ws_id AND ws_nc.season = tmvr.season
    WHERE ws_nl.season IS NOT NULL AND p.ws_id != ''' + str(id) + ''' 
    GROUP BY p.ws_id, tmvr.market_value, p.name, p.nationality, p.continent, p.heigt, posistion, tmvr.player_age, is_local, tmvr.season, nl_tournament, nl_elo_score, nl_rating, nl_minutes_played, nl_motm_awards, ec_tournament, ec_elo_score, ec_rating, ec_minutes_played, ec_motm_awards, ntc_tournament, ntc_elo_score, ntc_rating, ntc_minutes_played, ntc_motm_awards, nc_tournament, nc_elo_score, nc_rating, nc_minutes_played, nc_motm_awards
    ORDER BY name, tmvr.season;
    '''

    # Execute a query to select all from the "employees" table
    cursor.execute(query=query)

    # Fetch all the rows
    rows = cursor.fetchall()

    # Get column names
    column_names = [i[0] for i in cursor.description]

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(rows, columns=column_names)

    # Close the cursor and connection
    cursor.close()
    connection.close()

    targets=df.market_value
    df[["nl_rating"]] = df[["nl_rating"]].apply(pd.to_numeric)
    df[["ec_rating"]] = df[["ec_rating"]].apply(pd.to_numeric)
    df[["ntc_rating"]] = df[["ntc_rating"]].apply(pd.to_numeric)
    df[["nc_rating"]] = df[["nc_rating"]].apply(pd.to_numeric)
    inputs=df.drop(['ws_id', 'name','nl_tournament', 'ec_tournament', 'ntc_tournament', 'nc_tournament', 'market_value'],axis='columns')

    inputs = pd.get_dummies(inputs)

    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(inputs, targets, test_size=0.2, random_state=3)

    print("hello")

    from xgboost.sklearn import XGBRegressor

    params = {'colsample_bytree': 0.5, 'learning_rate': 0.1, 'max_depth': 4, 'n_estimators': 1000, 'subsample': 0.7}

    reg = XGBRegressor(**params)
    reg.fit(X_train, y_train)
    train_sq = reg.score(X_train, y_train)
    r_sq = reg.score(X_test, y_test)

    inputs = get_data_from_player(id)

    for index, input_row in inputs.iterrows():
        # reshape the row to be 2D, as required by reg.predict()
        input_data = input_row.values.reshape(1, -1)
        player_predection = reg.predict(input_data)
        save_predection(int(player_predection[0]), id, int(input_row['season']))


def save_predection(player_predection, ws_id, season):

    try:

        conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root',
                               passwd='password', db='economics_of_sports')
        cur = conn.cursor()

        query = "update tm_market_value_raw set xgboost_predection = " + str(player_predection) + " where tm_player_id in (select tm_id from player where ws_id = " + str(ws_id) + ") and season = " + str(season) + ";"
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        print(player_predection)
    except Exception as e:
        logging.error(e)


get_training_data_excluding_player_id(2995)

for i in range (2515,3038):
    try:
        get_training_data_excluding_player_id(i)
    except Exception as e:
        logging.error(e)