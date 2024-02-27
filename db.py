import sqlite3


def create_connection():
  connection = sqlite3.connect("puma.db")
  return connection


CREATE_USERS = '''
 CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 display_name TEXT ,
 first_name TEXT ,
 last_name TEXT 
 )
'''

CREATE_MATCHES = '''
CREATE TABLE IF NOT EXISTS matches (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 side_1_user_1_id INTEGER NOT NULL,
 side_1_user_2_id INTEGER ,
 side_2_user_1_id INTEGER NOT NULL,
 side_2_user_2_id INTEGER ,
 set_1_side_1_score INTEGER,
 set_1_side_2_score INTEGER,
 set_2_side_1_score INTEGER,
 set_2_side_2_score INTEGER,
 set_3_side_1_score INTEGER,
 set_3_side_2_score INTEGER,
 on_court INTEGER
 )
'''

CREATE_AVAILABLES = '''
CREATE TABLE IF NOT EXISTS availables (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL UNIQUE
 )
'''

CREATE_ELOS = '''
CREATE TABLE IF NOT EXISTS elos (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL,
 elo REAL NOT NULL
 )
'''

CREATE_SAVE = '''
CREATE TABLE IF NOT EXISTS save (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL
 )
'''

def create_table():
  connection = create_connection()
  cursor = connection.cursor()
  cursor.execute(CREATE_USERS)
  cursor.execute(CREATE_MATCHES)
  cursor.execute(CREATE_AVAILABLES)
  cursor.execute(CREATE_ELOS)
  cursor.execute(CREATE_SAVE)
  connection.commit()
  connection.close()


create_table()  # Call this function to create the table
