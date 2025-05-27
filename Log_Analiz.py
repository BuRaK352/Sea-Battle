# Log_Analiz.py
import json
import glob
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from log_helper import LOGS_DIR

# 1. Log dosyalarını oku ve DataFrame'e dönüştürn

def load_logs(root_dir=LOGS_DIR):
    """
    root_dir: Path veya string. log_helper.LOGS_DIR kullanılarak log dizinini alır.
    """
    records = []
    ship_placement = []
    root = Path(root_dir)

    # Her kullanıcı için combined_logs.json veya bireysel loglar
    for user_dir in root.iterdir():
        if not user_dir.is_dir():
            continue
        combined_file = user_dir / "combined_logs.json"
        if combined_file.exists():
            json_paths = [combined_file]
        else:
            json_paths = list(user_dir.glob("*.json"))

        for path in json_paths:
            try:
                data_list = json.load(open(path, encoding='utf-8'))
            except Exception:
                continue

            entries = data_list if isinstance(data_list, list) else [data_list]
            for data in entries:
                gid = data.get('game_id')
                uid = data.get('user_id')
                total_turns = data.get('total_turns')
                winner = data.get('winner')

                # Hamle kayıtları
                for mv in data.get('moves', []):
                    records.append({
                        'game_id': gid,
                        'user_id': uid,
                        'winner': winner,
                        'total_turns': total_turns,
                        'turn': mv.get('turn'),
                        'player': mv.get('player'),
                        'row': mv.get('cell', {}).get('row'),
                        'col': mv.get('cell', {}).get('col'),
                        'result': mv.get('result')
                    })

                # Gemi yerleşimleri
                for player_label in ['player1_ships', 'player2_ships']:
                    for ship in data.get(player_label, []):
                        size = ship.get('size')
                        for idx in ship.get('cells', []):
                            r, c = divmod(idx, 10)
                            ship_placement.append({
                                'game_id': gid,
                                'user_id': uid,
                                'player': player_label,
                                'size': size,
                                'row': r,
                                'col': c
                            })

    df_moves = pd.DataFrame(records)
    df_ships = pd.DataFrame(ship_placement)
    return df_moves, df_ships

# 2. Genel istatistikler

def plot_average_turns(df_moves):
    games = df_moves[['game_id', 'total_turns']].drop_duplicates()
    plt.figure()
    games['total_turns'].hist(bins=20)
    plt.title('Oyun Başına Atış Sayısı Dağılımı')
    plt.xlabel('Atış Sayısı')
    plt.ylabel('Oyun Adedi')
    plt.show()

# 3. Genel heatmap (tüm hamleler)

def plot_heatmap(df_moves, title='Heatmap - All Moves'):
    heat = np.zeros((10, 10), int)
    for _, mv in df_moves.iterrows():
        heat[mv.row, mv.col] += 1
    heat_norm = heat / heat.max() if heat.max() > 0 else heat
    plt.figure(figsize=(6, 6))
    plt.imshow(heat_norm, origin='upper', interpolation='nearest')
    plt.colorbar(label='Normalized Count')
    plt.title(title)
    plt.xlabel('Col')
    plt.ylabel('Row')
    plt.show()

# 4. Tur bazlı heatmap (örnek: first N turns)

def plot_turn_heatmaps(df_moves, max_turn=5):
    for t in range(1, max_turn + 1):
        subset = df_moves[df_moves['turn'] == t]
        plot_heatmap(subset, title=f'Heatmap - Turn {t}')

# 5. Gemi yerleşim heatmap (tüm gemiler)

def plot_ship_placement(df_ships, size=None):
    heat = np.zeros((10, 10), int)
    subset = df_ships if size is None else df_ships[df_ships['size'] == size]
    for _, s in subset.iterrows():
        heat[s.row, s.col] += 1
    heat_norm = heat / heat.max() if heat.max() > 0 else heat
    plt.figure(figsize=(6, 6))
    plt.imshow(heat_norm, origin='upper', interpolation='nearest')
    lbl = 'All Ships' if size is None else f'Size {size}'
    plt.title(f'Ship Placement Heatmap - {lbl}')
    plt.colorbar(label='Normalized Count')
    plt.show()

# 6. Kişiye özel analiz

def user_specific(df_moves, df_ships, user_id):
    dm = df_moves[df_moves['user_id'] == user_id]
    ds = df_ships[df_ships['user_id'] == user_id]
    plot_average_turns(dm)
    plot_heatmap(dm, title=f'Heatmap Moves - User {user_id}')
    plot_ship_placement(ds)
    for size in sorted(ds['size'].unique()):
        plot_ship_placement(ds, size)

# 7. Genel istatistik hesaplama

def compute_overall_stats(root_dir=LOGS_DIR):
    df_moves, df_ships = load_logs(root_dir)
    games = df_moves[['game_id', 'total_turns']].drop_duplicates()
    avg_shots = games['total_turns'].mean()
    win_counts = df_moves[df_moves['player'] == 1].groupby('game_id').first()['winner']
    win_rate = (win_counts == 1).mean() * 100
    return avg_shots, win_rate

# 8. Ana fonksiyon

def main():
    df_moves, df_ships = load_logs()
    # Genel analiz
    plot_average_turns(df_moves)
    plot_heatmap(df_moves)
    plot_turn_heatmaps(df_moves, max_turn=5)
    plot_ship_placement(df_ships)
    for sz in sorted(df_ships['size'].unique()):
        plot_ship_placement(df_ships, size=sz)

    # Örnek kullanıcı analizi
    users = df_moves['user_id'].unique()
    if len(users):
        user_specific(df_moves, df_ships, users[0])

if __name__ == '__main__':
    main()
