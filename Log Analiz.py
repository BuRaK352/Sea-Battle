import json
import glob
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Log dosyalarını oku ve DataFrame'e dönüştür

def load_logs(root_dir):
    records = []
    ship_placement = []
    for path in glob.glob(os.path.join(root_dir, "*", "*.json")):
        data = json.load(open(path, encoding='utf-8'))
        gid = data['game_id']
        uid = data['user_id']
        total_turns = data['total_turns']
        winner = data['winner']
        # hamle kayıtları
        for mv in data['moves']:
            records.append({
                'game_id': gid,
                'user_id': uid,
                'winner': winner,
                'total_turns': total_turns,
                'turn': mv['turn'],
                'player': mv['player'],
                'row': mv['cell']['row'],
                'col': mv['cell']['col'],
                'result': mv['result']
            })
        # gemi yerleşimleri
        for p, ships in [('player1', data['player1_ships']), ('player2', data['player2_ships'])]:
            for ship in ships:
                for idx in ship['cells']:
                    r, c = divmod(idx, 10)
                    ship_placement.append({
                        'game_id': gid,
                        'user_id': uid,
                        'player': p,
                        'size': ship['size'],
                        'row': r,
                        'col': c
                    })
    df_moves = pd.DataFrame(records)
    df_ships = pd.DataFrame(ship_placement)
    return df_moves, df_ships

# 2. Genel istatistikler

def plot_average_turns(df_moves):
    games = df_moves[['game_id','total_turns']].drop_duplicates()
    plt.figure()
    games['total_turns'].hist(bins=20)
    plt.title('Oyun Başına Atış Sayısı Dağılımı')
    plt.xlabel('Atış Sayısı')
    plt.ylabel('Oyun Adedi')
    plt.show()

# 3. Genel heatmap (tüm hamleler)

def plot_heatmap(df_moves, title='Heatmap - All Moves'):
    heat = np.zeros((10,10), int)
    for _, mv in df_moves.iterrows():
        heat[mv.row, mv.col] += 1
    heat_norm = heat / heat.max()
    plt.figure(figsize=(6,6))
    plt.imshow(heat_norm, origin='upper', interpolation='nearest')
    plt.colorbar(label='Normalized Count')
    plt.title(title)
    plt.xlabel('Col')
    plt.ylabel('Row')
    plt.show()

# 4. Tur bazlı heatmap (örnek: first N turns)

def plot_turn_heatmaps(df_moves, max_turn=5):
    for t in range(1, max_turn+1):
        subset = df_moves[df_moves['turn'] == t]
        plot_heatmap(subset, title=f'Heatmap - Turn {t}')

# 5. Gemi yerleşim heatmap (tüm gemiler)

def plot_ship_placement(df_ships, size=None):
    heat = np.zeros((10,10), int)
    subset = df_ships if size is None else df_ships[df_ships['size']==size]
    for _, s in subset.iterrows():
        heat[s.row, s.col] += 1
    heat_norm = heat / heat.max()
    plt.figure(figsize=(6,6))
    plt.imshow(heat_norm, origin='upper', interpolation='nearest')
    lbl = 'All Ships' if size is None else f'Size {size}'
    plt.title(f'Ship Placement Heatmap - {lbl}')
    plt.colorbar()
    plt.show()

# 6. Kişiye özel analiz

def user_specific(df_moves, df_ships, user_id):
    dm = df_moves[df_moves['user_id']==user_id]
    ds = df_ships[df_ships['user_id']==user_id]
    plot_average_turns(dm)
    plot_heatmap(dm, title=f'Heatmap Moves - User {user_id}')
    plot_ship_placement(ds)
    for size in sorted(ds['size'].unique()):
        plot_ship_placement(ds, size)

# 7. Ana fonksiyon

def main():
    root = 'logs'
    df_moves, df_ships = load_logs(root)
    # Genel
    plot_average_turns(df_moves)
    plot_heatmap(df_moves)
    plot_turn_heatmaps(df_moves, max_turn=5)
    plot_ship_placement(df_ships)
    for sz in sorted(df_ships['size'].unique()):
        plot_ship_placement(df_ships, size=sz)
    # Kişisel (örnek: ilk user)
    users = df_moves['user_id'].unique()
    if len(users):
        user_specific(df_moves, df_ships, users[0])

if __name__ == '__main__':
    main()
