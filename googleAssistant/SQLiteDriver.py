import math
import sqlite3
import time

ADD_USER = "INSERT into USERS(name, email, mac_address, google_key) VALUES(?, ?, ?, ?)"  # crea user
GET_USER_ID = "SELECT id FROM USERS where email=?"
ADD_LOGS = "INSERT into LOGS VALUES(?,?)"  # crea valore ultimo accesso
ADD_EVENT = "INSERT INTO EVENTS	(type,sender,target,timedate,priority) VALUES(?,?,?,?,?)"  # crea evento
UPDATE_LOGS = "UPDATE LOGS SET last_seen=? WHERE user_id=?"  # aggiorna ultimo accesso
GET_EVENTS = "SELECT * FROM EVENTS,USERS,LOGS where USERS.id=? AND USERS.id=LOGS.user_id AND (EVENTS.target=USERS.email OR EVENTS.target ISNULL) AND EVENTS.timedate>LOGS.last_seen"  # ottieni nuovi eventi dell'utente
GET_LIST = "SELECT * FROM LIST"  # ottieni elementi lista spesa
ADD_LIST_ITEM = "INSERT INTO LIST(name,price,qt,user) VALUES(?,?,?,?)"  #aggiungi prodotto a lista spesa
DELETE_EVENTS = "DELETE FROM EVENTS WHERE EVENTS.timedate<?"  # cancella eventi piu vecchi di una certa data
DELETE_LIST = "DELETE FROM LIST"  # cancella elementi lista spesa


def create_connection(url):
    return sqlite3.connect(url)


def add_user(conn, name, email, MAC, key):
    cursor = conn.cursor()

    # adding to users
    data = (name, email, MAC, key)
    cursor.execute(ADD_USER, data)
    conn.commit()

    # adding to logs
    cursor.execute(GET_USER_ID, (email,))
    _id = cursor.fetchone()[0]

    cursor.execute(ADD_LOGS, (_id, math.floor(time.time())))

    conn.commit()


def add_event(conn, sender, target, type, timestamp, priority):
    cursor = conn.cursor()
    cursor.execute(ADD_EVENT, (type, sender, target, timestamp, priority))
    conn.commit()
    return


def get_events(conn, email):
    data = [[]]
    cursor = conn.cursor()

    cursor.execute(GET_USER_ID, (email, ))
    user_id = cursor.fetchone()[0]

    cursor.execute(GET_EVENTS, (user_id, ))

    # get colums names
    i = 0
    indexes = dict([])

    print(cursor)

    for description in cursor.description:
        name = description[0]
        indexes[name] = i
        i += 1

    # the header of return obj is a dictionary with column names
    data[0] = indexes

    # fill obj with results
    i = 1
    for row in cursor:
        data.append(row)

    return data


def get_list(conn):
    data = [[]]
    cursor = conn.cursor()

    cursor.execute(GET_LIST)

    # get colums names
    i = 0
    indexes = dict([])

    print(cursor)

    for description in cursor.description:
        name = description[0]
        indexes[name] = i
        i += 1

    # the header of return obj is a dictionary with column names
    data[0] = indexes

    # fill obj with results
    i = 1
    for row in cursor:
        data.append(row)

    return data


def delete_events(conn, timestamp):
    cursor = conn.cursor()
    cursor.execute(DELETE_EVENTS, (timestamp,))
    conn.commit()
    return


def delete_list(conn):
    cursor = conn.cursor()
    cursor.execute(DELETE_LIST)
    conn.commit()
    return


def add_list_item(conn, name, price, qt, email):
    cursor = conn.cursor()

    cursor.execute(GET_USER_ID, (email, ))
    user_id = cursor.fetchone()[0]

    cursor.execute(ADD_LIST_ITEM, (name, price, qt, user_id))
    conn.commit()
    return


def update_logs(conn, email):
    cursor = conn.cursor()

    # adding to logs
    cursor.execute(GET_USER_ID, (email,))
    _id = cursor.fetchone()[0]

    cursor.execute(UPDATE_LOGS, (math.floor(time.time()), _id))

    conn.commit()

