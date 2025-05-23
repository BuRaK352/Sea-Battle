# log_helper.py
import json
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
USER_INFO_FILE = BASE_DIR / "user_info.json"

# Load/save user info mapping username to user_id
def load_user_info():
    if USER_INFO_FILE.exists():
        with open(USER_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_info(info):
    with open(USER_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

user_info = load_user_info()
username = None
user_id = None

# Set or retrieve user_id for a given username
def set_username(name):
    global username, user_id, user_info
    username = name.strip()
    if username in user_info:
        user_id = user_info[username]
    else:
        user_id = uuid.uuid4().hex[:10]
        user_info[username] = user_id
        save_user_info(user_info)
    return user_id

def get_username():
    return username

# Create log data structure for a new game
def create_log_data(player1_ships, player2_ships):
    if user_id is None:
        raise ValueError("User ID not set. Call set_username() before logging.")
    log_data = {
        "game_id": datetime.now().strftime("%Y_%m_%d_%Hh%Mm%Ss%f") + f"_{user_id}",
        "user_id": user_id,
        "username": username,
        "start_time": datetime.now().isoformat(),
        "player1_ships": [{"size": ship.size, "cells": ship.indexes} for ship in player1_ships],
        "player2_ships": [{"size": ship.size, "cells": ship.indexes} for ship in player2_ships],
        "moves": [],
        "hit_count": {"1": 0, "2": 0},
        "miss_count": {"1": 0, "2": 0},
        "sunk_ships": []
    }
    return log_data

# Add a move entry to log_data
def add_move(log_data, turn, player, index, result, ship_size=None):
    row, col = divmod(index, 10)
    move = {"turn": turn, "player": player, "cell": {"row": row, "col": col}, "result": result}
    if ship_size is not None:
        move["ship_size"] = ship_size
        log_data["sunk_ships"].append({"turn": turn, "player": player, "ship_size": ship_size})
    log_data["moves"].append(move)
    if result in ("hit", "sunk"):
        log_data["hit_count"][str(player)] += 1
    elif result == "miss":
        log_data["miss_count"][str(player)] += 1

# Finalize and write log data to file
def finalize_log(log_data, winner):
    if user_id is None:
        raise ValueError("User ID not set. Call set_username() before finalizing log.")
    log_data["end_time"] = datetime.now().isoformat()
    log_data["winner"] = winner
    log_data["total_turns"] = len(log_data["moves"])
    # Determine user's log directory by user_id
    user_log_dir = LOGS_DIR / log_data["username"]
    user_log_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{log_data['game_id']}.json"
    with open(user_log_dir / file_name, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)
    print(f"Log kaydedildi: {file_name}")
