from htmx.av_list import get_av_html
from htmx.uav_list import get_uav_html
from htmx.match import match_html
from fastapi import FastAPI
from fastapi import HTTPException
import sqlite3
from fastapi.responses import HTMLResponse
import random

from pydantic import BaseModel
'''
UserCreateclass BookCreate(BaseModel):
 title: str
 author: str

class Book(BookCreate):
 id: int
'''
app = FastAPI()


class UserCreate(BaseModel):
  display_name: str
  first_name: str = None
  last_name: str = None


class User(UserCreate):
  id: int


# Model for Match


class Match(BaseModel):
  side_1_user_1_id: int
  side_1_user_2_id: int = None
  side_2_user_1_id: int
  side_2_user_2_id: int = None
  set_1_side_1_score: int=None
  set_1_side_2_score: int=None
  set_2_side_1_score: int=None
  set_2_side_2_score: int=None
  set_3_side_1_score: int=None
  set_3_side_2_score: int=None

# Model for Available


class Available(BaseModel):
  user_id: int


# Model for Elo


class Elo(BaseModel):
  user_id: int
  elo: float


# Create Match


@app.post("/matches/")
def create_match(match: Match):
  return create_match_db(match)


def create_match_db(match):
  connection = create_connection()
  cursor = connection.cursor()
  INSERT_MATCH = "INSERT INTO matches (side_1_user_1_id, side_1_user_2_id, side_2_user_1_id, side_2_user_2_id) VALUES (?, ?, ?, ?)"
  cursor.execute(INSERT_MATCH,
                 (match.side_1_user_1_id, match.side_1_user_2_id,
                  match.side_2_user_1_id, match.side_2_user_2_id))
  connection.commit()
  match_id = cursor.lastrowid
  connection.close()
  return {"id": match_id, **match.model_dump()}


# Create Available


@app.post("/availables/")
def create_available_endpoint(available: Available):
  return create_available(available)


def create_available(available):
  connection = create_connection()
  cursor = connection.cursor()
  INSERT_AVAILABLE = "INSERT INTO availables (user_id) VALUES (?)"
  cursor.execute(INSERT_AVAILABLE, (available.user_id, ))
  connection.commit()
  available_id = cursor.lastrowid
  connection.close()
  return {"id": available_id, **available.model_dump()}


# Create Elo


@app.post("/elos/")
def create_elo(elo: Elo):
  connection = create_connection()
  cursor = connection.cursor()
  INSERT_ELO = "INSERT INTO elos (user_id, elo) VALUES (?, ?)"
  cursor.execute(INSERT_ELO, (elo.user_id, elo.elo))
  connection.commit()
  elo_id = cursor.lastrowid
  connection.close()
  return {"id": elo_id, **elo.model_dump()}


def create_connection():
  connection = sqlite3.connect("puma.db")
  return connection


def create_user(user: UserCreate):
  connection = create_connection()
  cursor = connection.cursor()
  INSERT_USER = "INSERT INTO users (display_name, first_name, last_name) VALUES (?, ?, ?)"
  cursor.execute(INSERT_USER,
                 (user.display_name, user.first_name, user.last_name))
  connection.commit()
  user_id = cursor.lastrowid
  connection.close()
  return {"id": user_id, **user.model_dump()}


@app.post("/users/")
def create_user_endpoint(user: UserCreate):
  return create_user(user)

@app.post("/available/update/{user_id}", response_class=HTMLResponse)
def update_available(user_id):
  def user_in_available(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    SELECT_USER = "SELECT user_id FROM availables WHERE user_id = ?"
    cursor.execute(SELECT_USER, (user_id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None
  if user_in_available(user_id):
    remove_players_from_available([user_id])
  else:
    create_available(Available(user_id=user_id))
  return get_available_html()

@app.post('/availables/save', response_class=HTMLResponse)
def save_available():
  connection = create_connection()
  cursor = connection.cursor()
  DELETE_SAVE = 'DELETE from save'
  cursor.execute(DELETE_SAVE)
  # connection.commit()
  
  INSERT_SAVE = "INSERT INTO save (user_id) SELECT user_id FROM availables"
  cursor.execute(INSERT_SAVE)
  connection.commit()
  connection.close()
  return get_available_html()

@app.get('/availables/load', response_class=HTMLResponse)
def load_available():
  connection = create_connection()
  cursor = connection.cursor()
  DELETE_AVAILABLES = 'DELETE from availables'
  cursor.execute(DELETE_AVAILABLES)
  connection.commit()
  INSERT_SAVE_INTO_AVAILABLES = '''
  INSERT INTO availables (user_id) SELECT user_id FROM save
  '''
  cursor.execute(INSERT_SAVE_INTO_AVAILABLES)
  connection.commit()
  connection.close()
  return get_available_html()

@app.get('/available-html', response_class=HTMLResponse)
def get_available_html():
  availables = get_all_availables()
  availables.sort(key=lambda a: a['elo'], reverse=True)
  av_html = get_av_html(availables)

  unavailables = get_all_unavailables()
  unavailables.sort(key=lambda a: a['elo'], reverse=True)
  uav_html = get_uav_html(unavailables)
  container = '''
      <div id="av-container">
       <div>
          <button hx-post="/availables/save" hx-target="#av-container" hx-swap="outerHTML">Save</button>
          <button hx-get="/availables/load" hx-target="#av-container" hx-swap="outerHTML" class="load-button">Load</button>
        </div>
        <div class="container">
          <div class="column">
              <h2>Available</h2>
        ''' + av_html + '''
          </div>
          <div class="column">
              <h2>Unavailable</h2>
        '''+ uav_html + '''
          </div>
        </div>
    </div>
  '''
  return container

@app.get("/match-html", response_class=HTMLResponse)
def get_match_html():
    match_list = get_all_matches()
    html = match_html(match_list)
    return html
  
@app.get("/", response_class=HTMLResponse)
def read_root():
  
  
  content = ''
  with open('./htmx/index.html', 'r') as f:
    content = f.read()
  return HTMLResponse(content=content, status_code=200)


@app.get("/users/")
def get_all_users():
  connection = create_connection()
  cursor = connection.cursor()
  SELECT_ALL_USERS = "SELECT * FROM users"
  cursor.execute(SELECT_ALL_USERS)
  users = cursor.fetchall()
  connection.close()
  user_list = []
  for user in users:
    user_dict = {
        "id": user[0],
        "display_name": user[1],
        "first_name": user[2],
        "last_name": user[3],
    }
    user_list.append(user_dict)
  return user_list

def get_all_unavailables():
  connection = create_connection()
  cursor = connection.cursor()
  SELECT_ALL_UNAVAILABLES = """
        SELECT users.id, users.display_name, elos.elo,
        case when save.id is not null then 1 else 0 end as is_saved
        FROM users
        left JOIN availables ON availables.user_id = users.id
        left JOIN elos ON elos.user_id = users.id
        left join save on save.user_id = users.id
        where availables.user_id is null
    """
  cursor.execute(SELECT_ALL_UNAVAILABLES)
  unavailables = cursor.fetchall()
  connection.close()
  unavailable_list = []
  for unavailable in unavailables:
    unavailable_dict = {
        "user_id": unavailable[0],
        "display_name": unavailable[1],
        "elo": unavailable[2],
        "is_saved": unavailable[3]
    }
    unavailable_list.append(unavailable_dict)
  return unavailable_list
 

@app.get("/availables/")
def get_all_availables():
  connection = create_connection()
  cursor = connection.cursor()
  SELECT_ALL_AVAILABLES = """
        SELECT availables.id, availables.user_id, users.display_name, users.first_name, users.last_name, elos.elo,
        case when save.id is not null then 1 else 0 end as is_saved
        FROM availables
        JOIN users ON availables.user_id = users.id
        LEFT JOIN elos ON elos.user_id = availables.user_id
        LEFT JOIN save ON save.user_id = availables.user_id
    """
  cursor.execute(SELECT_ALL_AVAILABLES)
  availables = cursor.fetchall()
  connection.close()
  available_list = []
  for available in availables:
    available_dict = {
        "id": available[0],
        "user_id": available[1],
        "display_name": available[2],
        "first_name": available[3],
        "last_name": available[4],
        "elo": available[5],
        "is_saved": available[6]
    }
    available_list.append(available_dict)
  return available_list


@app.get("/matches/")
def get_all_matches():
  connection = create_connection()
  cursor = connection.cursor()
  SELECT_ALL_MATCHES = """
        SELECT matches.id, matches.side_1_user_1_id, matches.side_1_user_2_id,
               matches.side_2_user_1_id, matches.side_2_user_2_id, matches.side_1_score, 
               matches.side_2_score, 
               u1.display_name AS side_1_user_1_display_name,
               u1.first_name AS side_1_user_1_first_name,
               u1.last_name AS side_1_user_1_last_name,
               u2.display_name AS side_1_user_2_display_name,
               u2.first_name AS side_1_user_2_first_name,
               u2.last_name AS side_1_user_2_last_name,
               u3.display_name AS side_2_user_1_display_name,
               u3.first_name AS side_2_user_1_first_name,
               u3.last_name AS side_2_user_1_last_name,
               u4.display_name AS side_2_user_2_display_name,
               u4.first_name AS side_2_user_2_first_name,
               u4.last_name AS side_2_user_2_last_name
        FROM matches
        LEFT JOIN users AS u1 ON matches.side_1_user_1_id = u1.id
        LEFT JOIN users AS u2 ON matches.side_1_user_2_id = u2.id
        LEFT JOIN users AS u3 ON matches.side_2_user_1_id = u3.id
        LEFT JOIN users AS u4 ON matches.side_2_user_2_id = u4.id
        ORDER BY matches.id DESC
    """
  cursor.execute(SELECT_ALL_MATCHES)
  matches = cursor.fetchall()
  connection.close()
  match_list = []
  for match in matches:
    match_dict = {
        "id": match[0],
        "side_1_user_1_id": match[1],
        "side_1_user_2_id": match[2],
        "side_2_user_1_id": match[3],
        "side_2_user_2_id": match[4],
        "side_1_score": match[5],
        "side_2_score": match[6],
        "side_1_user_1_display_name": match[7],
        "side_1_user_1_first_name": match[8],
        "side_1_user_1_last_name": match[9],
        "side_1_user_2_display_name": match[10],
        "side_1_user_2_first_name": match[11],
        "side_1_user_2_last_name": match[12],
        "side_2_user_1_display_name": match[13],
        "side_2_user_1_first_name": match[14],
        "side_2_user_1_last_name": match[15],
        "side_2_user_2_display_name": match[16],
        "side_2_user_2_first_name": match[17],
        "side_2_user_2_last_name": match[18]
    }
    match_list.append(match_dict)
  return match_list


@app.get("/elos/")
def get_all_elos():
  connection = create_connection()
  cursor = connection.cursor()
  SELECT_ALL_ELOS = """
        SELECT elos.id, elos.user_id, elos.elo, users.display_name, users.first_name, users.last_name
        FROM elos
        JOIN users ON elos.user_id = users.id
    """
  cursor.execute(SELECT_ALL_ELOS)
  elos = cursor.fetchall()
  connection.close()
  elo_list = []
  for elo in elos:
    elo_dict = {
        "id": elo[0],
        "user_id": elo[1],
        "elo": elo[2],
        "display_name": elo[3],
        "first_name": elo[4],
        "last_name": elo[5]
    }
    elo_list.append(elo_dict)
  return elo_list


# Define a Pydantic model for the score update


class ScoreUpdate(BaseModel):
  side_1_score: int
  side_2_score: int


@app.put("/matches/{match_id}/update-score")
def update_match_score(match_id: int, score_update: ScoreUpdate):
  connection = create_connection()
  cursor = connection.cursor()
  UPDATE_MATCH_SCORE = """
        UPDATE matches
        SET side_1_score = ?, side_2_score = ?
        WHERE id = ?
    """
  cursor.execute(
      UPDATE_MATCH_SCORE,
      (score_update.side_1_score, score_update.side_2_score, match_id))
  rows_affected = cursor.rowcount
  INSERT_MATCH_PLAYERS_AVAILABLE = """
        INSERT INTO availables (user_id) 
        SELECT side_1_user_1_id from matches
        WHERE matches.id = :match_id
        UNION
        SELECT side_1_user_2_id from matches
        WHERE matches.id = :match_id
        UNION
        SELECT side_2_user_1_id from matches
        WHERE matches.id = :match_id
        UNION
        SELECT side_2_user_2_id from matches
        WHERE matches.id = :match_id
    """
  cursor.execute(INSERT_MATCH_PLAYERS_AVAILABLE, {'match_id': match_id})
  connection.commit()
  connection.close()
  if rows_affected == 0:
    raise HTTPException(status_code=404, detail="Match not found")

  return {"message": f"Match {match_id} score updated successfully"}


# Function to get a match by id without displaying scores
def get_match_by_id(match_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    SELECT_MATCH = """
        SELECT matches.id, matches.side_1_user_1_id, matches.side_1_user_2_id,
               matches.side_2_user_1_id, matches.side_2_user_2_id,
               u1.display_name AS side_1_user_1_display_name,
               u2.display_name AS side_1_user_2_display_name,
               u3.display_name AS side_2_user_1_display_name,
               u4.display_name AS side_2_user_2_display_name
        FROM matches
        LEFT JOIN users AS u1 ON matches.side_1_user_1_id = u1.id
        LEFT JOIN users AS u2 ON matches.side_1_user_2_id = u2.id
        LEFT JOIN users AS u3 ON matches.side_2_user_1_id = u3.id
        LEFT JOIN users AS u4 ON matches.side_2_user_2_id = u4.id
        WHERE matches.id = ?
    """
    cursor.execute(SELECT_MATCH, (match_id,))
    match_data = cursor.fetchone()
    connection.close()
    if match_data:
        match_dict = {
            "id": match_data[0],
            "side_1_user_1_id": match_data[1],
            "side_1_user_2_id": match_data[2],
            "side_2_user_1_id": match_data[3],
            "side_2_user_2_id": match_data[4],
            "side_1_user_1_display_name": match_data[5],
            "side_1_user_2_display_name": match_data[6] if match_data[6] is not None else None,
            "side_2_user_1_display_name": match_data[7],
            "side_2_user_2_display_name": match_data[8] if match_data[8] is not None else None
        }
        return match_dict
    else:
        return None

def get_available_players(rank_from: int = None, rank_to: int = None):
  connection = create_connection()
  cursor = connection.cursor()
  SELECT_AVAILABLE_PLAYERS = """
        SELECT availables.user_id,elos.elo FROM availables JOIN elos ON availables.user_id = elos.user_id ORDER BY elo"""
  if rank_to is not None:
    SELECT_AVAILABLE_PLAYERS += f" LIMIT {rank_to-rank_from}"
    if rank_from is not None:
      SELECT_AVAILABLE_PLAYERS += f" OFFSET {rank_from}"
  cursor.execute(SELECT_AVAILABLE_PLAYERS)
  available_players = [row[0] for row in cursor.fetchall()]
  connection.close()
  return available_players


# Function to remove players from available list


def remove_players_from_available(players: list):
  connection = create_connection()
  cursor = connection.cursor()
  try:
    # Remove each player from the available list
    for player_id in players:
      REMOVE_PLAYER = """
                DELETE FROM availables WHERE user_id = ?
            """
      cursor.execute(REMOVE_PLAYER, (player_id, ))
    connection.commit()
  except Exception as e:
    connection.rollback()
    raise HTTPException(status_code=500,
                        detail=f"Error removing players: {str(e)}")
  finally:
    connection.close()


  
@app.post("/matches/create", response_class=HTMLResponse)
def create_match(random_players: int = 4,
                 rank_from: int = None,
                 rank_to: int = None):
  # Check if min_rank is greater than max_rank

  # Fetch available players based on Elo rank range
  available_players = get_available_players(rank_from, rank_to)

  # Check if there are enough available players
  if len(available_players) < random_players:
    raise HTTPException(status_code=400, detail="Not enough available players")

  # Randomly select players
  selected_players = random.sample(available_players, random_players)
  # Create the match in the database with selected players
  connection = create_connection()
  cursor = connection.cursor()
  INSERT_MATCH = "INSERT INTO matches (side_1_user_1_id, side_1_user_2_id, side_2_user_1_id, side_2_user_2_id) VALUES (?, ?, ?, ?)"
  cursor.execute(INSERT_MATCH, (selected_players[0], selected_players[1],
                                selected_players[2], selected_players[3]))
  match_id = cursor.lastrowid
  connection.commit()
  connection.close()

  # Remove selected players from available list
  remove_players_from_available(selected_players)

  return get_match_html()


# Function to fetch available players based on Elo rank range


# Endpoint to remove a player from the available pool


@app.delete("/availables/{user_id}/remove")
def remove_player_from_available(user_id: int):
  try:
    # Remove the player from the available list
    remove_player(user_id)
    return {"message": f"Player with ID {user_id} removed from available pool"}
  except Exception as e:
    raise HTTPException(status_code=500,
                        detail=f"Error removing player: {str(e)}")


# Function to remove a player from the available pool


def remove_player(user_id: int):
  connection = create_connection()
  cursor = connection.cursor()
  try:
    # Remove the player from the available list
    REMOVE_PLAYER = """
            DELETE FROM availables WHERE user_id = ?
        """
    cursor.execute(REMOVE_PLAYER, (user_id, ))
    connection.commit()
  except Exception as e:
    connection.rollback()
    raise e
  finally:
    connection.close()
