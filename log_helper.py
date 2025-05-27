# log_helper.py
import json
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
USER_INFO_FILE = BASE_DIR / "user_info.json"


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


def set_username(name):
    global username, user_id, user_info
    username = name.strip()
    if username in user_info:
        user_id = user_info[username]
    else:
        user_id = uuid.uuid4().hex[:10]
        user_info[username] = user_id
        save_user_info(user_info)
    USER_LOG_DIR = LOGS_DIR / user_id
    USER_LOG_DIR.mkdir(parents=True, exist_ok=True)
    return user_id


def get_username():
    return username


def create_log_data(player1_ships, player2_ships):
    if user_id is None:
        raise ValueError("User ID not set. Call set_username() before logging.")
    return {
        "game_id": datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{user_id}",
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


def finalize_log(log_data, winner):
    if user_id is None:
        raise ValueError("User ID not set. Call set_username() before finalizing log.")

    log_data["end_time"] = datetime.now().isoformat()
    log_data["winner"] = winner
    log_data["total_turns"] = len(log_data["moves"])

    # Her oyun için ayrı dosya
    game_file = LOGS_DIR / username / f"game_{log_data['game_id']}.json"

    # Dosyayı kaydet
    with open(game_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    # Oyunu combined_logs.json'a da ekleyelim (opsiyonel)
    combined_file = LOGS_DIR / username / "combined_logs.json"
    logs = []
    if combined_file.exists():
        try:
            with open(combined_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(log_data)
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)