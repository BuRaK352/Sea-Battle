import json
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
USER_ID_FILE = BASE_DIR / "user_id.txt"

if not USER_ID_FILE.exists():
    user_id = uuid.uuid4().hex[:10]
    USER_ID_FILE.write_text(user_id)
else:
    user_id = USER_ID_FILE.read_text().strip()

USER_LOG_DIR = LOGS_DIR / user_id
USER_LOG_DIR.mkdir(parents=True, exist_ok=True)

def create_log_data(player1_ships, player2_ships):
    log_data = {
        "game_id": datetime.now().strftime("%Y_%m_%d_%Hh%Mm%Ss%Ms") + f"{user_id}",
        "user_id": user_id,
        "start_time": datetime.now().isoformat(),
        "player1_ships": [{"size": ship.size, "cells": ship.indexes} for ship in player1_ships],
        "player2_ships": [{"size": ship.size, "cells": ship.indexes} for ship in player2_ships],
        "moves": [],
        "hit_count": {"1": 0, "2": 0},
        "miss_count": {"1": 0, "2": 0},
        "sunk_ships": []
    }
    return log_data

def add_move(log_data, turn, player, index, result, ship_size=None):
    row, col = divmod(index, 10)
    move = {
        "turn": turn,
        "player": player,
        "cell": {"row": row, "col": col},
        "result": result
    }
    if ship_size is not None:
        move["ship_size"] = ship_size
        log_data["sunk_ships"].append({"turn": turn, "player": player, "ship_size": ship_size})

    log_data["moves"].append(move)

    if result == "hit" or result == "sunk":
        log_data["hit_count"][str(player)] += 1
    elif result == "miss":
        log_data["miss_count"][str(player)] += 1

def finalize_log(log_data, winner):
    log_data["end_time"] = datetime.now().isoformat()
    log_data["winner"] = winner
    log_data["total_turns"] = len(log_data["moves"])

    file_name = log_data["game_id"] + ".json"
    with open(USER_LOG_DIR / file_name, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    print(f"Log kaydedildi: {file_name}")
