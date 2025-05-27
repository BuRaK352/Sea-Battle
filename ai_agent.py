# ai_agent.py
import os
import json
from pathlib import Path
from collections import defaultdict
import pickle
import numpy as np
import random
import matplotlib.pyplot as plt

class QLearningAgent:
    def __init__(
        self, user_id, alpha=0.3, gamma=0.9, epsilon=0.5,
        min_epsilon=0.05, decay=0.99, model_filename="qtable.pkl"
    ):
        self.user_id = user_id
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.decay = decay
        self.ship_sizes = [5, 4, 3, 3, 2]
        self.q_table = defaultdict(self._default_q)
        self.target_queue = []

        self.user_dir = Path("logs") / self.user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        self.q_file = self.user_dir / model_filename

        self._load_q_table()
        self.learn_from_logs()

    def _default_q(self):
        return np.zeros(100)

    def _load_q_table(self):
        if self.q_file.exists() and self.q_file.stat().st_size > 0:
            try:
                with open(self.q_file, 'rb') as f:
                    data = pickle.load(f)
                self.q_table = defaultdict(self._default_q, data)
            except Exception:
                self.q_table = defaultdict(self._default_q)

    def save(self):
        with open(self.q_file, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def state_from_grid(self, grid):
        return tuple(np.array(grid).flatten().tolist())

    def get_neighbors(self, idx):
        row, col = divmod(idx, 10)
        neighbors = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 10 and 0 <= nc < 10:
                neighbors.append(nr * 10 + nc)
        return neighbors

    def compute_probability_grid(self, search_grid):
        prob = np.zeros((10,10))
        for size in self.ship_sizes:
            for r in range(10):
                for c in range(10 - size + 1):
                    indices = [r*10 + c + i for i in range(size)]
                    if all(search_grid[i] == 'U' for i in indices):
                        for i in indices:
                            prob.flat[i] += 1
            for c in range(10):
                for r in range(10 - size + 1):
                    indices = [(r + i)*10 + c for i in range(size)]
                    if all(search_grid[i] == 'U' for i in indices):
                        for i in indices:
                            prob.flat[i] += 1
        total = prob.sum()
        return prob.flatten()/total if total > 0 else prob.flatten()

    def choose_action(self, search_grid):
        unk = [i for i, v in enumerate(search_grid) if v == 'U']
        if not unk:
            return None

        hits = [i for i, v in enumerate(search_grid) if v == 'H']
        if len(hits) >= 2:
            hits.sort()
            delta = abs(hits[1] - hits[0])
            if delta == 1 or delta == 10:
                direction = delta
                options = []
                min_hit = min(hits)
                max_hit = max(hits)

                for d in [1, -1]:
                    next_idx = max_hit + d * direction if d == 1 else min_hit + d * direction
                    if 0 <= next_idx < 100 and search_grid[next_idx] == 'U':
                        options.append(next_idx)
                if options:
                    self._decay_epsilon()
                    return random.choice(options)

        for h in hits:
            for n in self.get_neighbors(h):
                if search_grid[n] == 'U' and n not in self.target_queue:
                    self.target_queue.append(n)
        if self.target_queue:
            self._decay_epsilon()
            return self.target_queue.pop(0)

        probs = self.compute_probability_grid(search_grid)
        p_unk = [probs[i] for i in unk]
        tot = sum(p_unk)
        if tot > 0:
            self._decay_epsilon()
            return int(np.random.choice(unk, p=[p / tot for p in p_unk]))
        else:
            if random.random() < self.epsilon:
                return random.choice(unk)
            else:
                state = self.state_from_grid(search_grid)
                qv = self.q_table[state]
                maxq = max(qv[i] for i in unk)
                best = [i for i in unk if qv[i] == maxq]
                return random.choice(best)

    def _decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)

    def update_q(self, prev_grid, action, reward, next_grid):
        s = self.state_from_grid(prev_grid)
        ns = self.state_from_grid(next_grid)
        best_next = np.max(self.q_table[ns])
        old = self.q_table[s][action]
        self.q_table[s][action] = old + self.alpha * (reward + self.gamma * best_next - old)

    def learn_from_logs(self):
        """Ayrı ayrı game_*.json dosyalarından öğrenme yapar"""
        if not self.user_dir.exists():
            return

        # Kullanıcının tüm oyun dosyalarını bul
        game_files = list(self.user_dir.glob("game_*.json"))
        if not game_files:
            print(f"{self.user_dir} dizininde oyun dosyası bulunamadı")
            return

        for game_file in game_files:
            try:
                with open(game_file, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)

                # Sadece bu kullanıcının verilerini işle
                if game_data.get('user_id') != self.user_id:
                    continue

                self._process_game_data(game_data)

            except Exception as e:
                print(f"{game_file} işlenirken hata: {e}")

        self.save()
        print(f"Q-table güncellendi (İşlenen oyun sayısı: {len(game_files)})")

        def _process_game_data(self, game_data):
            """Tek bir oyun verisini işler"""
            grid = ['U'] * 100
            for move in game_data.get('moves', []):
                if move.get('player') != 1:  # Sadece AI hamleleri
                    continue

                idx = move['cell']['row'] * 10 + move['cell']['col']
                prev_grid = grid.copy()
                result = move.get('result')

                # Grid ve ödülü güncelle
                if result in ('hit', 'sunk'):
                    grid[idx] = 'H'
                    reward = 3 if result == 'sunk' else 1
                else:
                    grid[idx] = 'M'
                    reward = -0.1

                # Q-tablosunu güncelle
                self.update_q(prev_grid, idx, reward, grid)

                # Gemi batırıldıysa ek ödül
                if result == 'sunk':
                    self._reward_sunken_ship(prev_grid, grid, move)

        def _reward_sunken_ship(self, prev_grid, grid, move):
            """Batırılan gemi için ek ödül verir"""
            ship_size = move.get('ship_size', 0)
            for _ in range(ship_size):
                self.update_q(prev_grid, idx, 5, grid)

    def plot_qtable_heatmap(self, search_grid, save_path="plot_qtable_heatmap.png"):
        # Önce Q-tablosunu güncelle
        self.learn_from_logs()

        # Mevcut state'i al
        current_state = self.state_from_grid(search_grid)

        # Bu state için Q değerlerini al
        if current_state not in self.q_table:
            print(f"Uyarı: Current state Q-table'da bulunamadı!")
            q_values = np.zeros(100)
        else:
            q_values = self.q_table[current_state]

        # Heatmap oluştur
        heat = np.array(q_values).reshape((10, 10))

        plt.figure(figsize=(10, 8))
        plt.imshow(heat, origin='upper', interpolation='nearest', cmap='viridis')
        plt.colorbar(label="Q-Value")

        # Oyun durumunu üstüne çiz
        for i in range(10):
            for j in range(10):
                cell_state = search_grid[i * 10 + j]
                if cell_state == 'H':
                    plt.scatter(j, i, color='red', s=100, marker='x')
                elif cell_state == 'M':
                    plt.scatter(j, i, color='blue', s=100, marker='o')

        plt.title(f"Q-Table Heatmap (Epsilon: {self.epsilon:.2f})")
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"Heatmap güncellendi ve kaydedildi: {save_path}")


    def print_qtable_stats(self):
        print("\nQ-Table İstatistikleri:")
        print(f"Toplam state sayısı: {len(self.q_table)}")
        if self.q_table:
            sample_state = next(iter(self.q_table))
            print(f"Örnek state: {sample_state}")
            print(f"Örnek Q değerleri: {self.q_table[sample_state]}")
        print(f"Epsilon değeri: {self.epsilon}")

    def plot_aggregated_qtable(self, save_path="plot_qtable_heatmap.png"):
        """Önceki heatmap'i silip yeni bir tane oluşturur."""
        import os
        import numpy as np
        import matplotlib.pyplot as plt

        # Eski dosyayı sil
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
                print(f"Eski heatmap silindi: {save_path}")
            except Exception as e:
                print(f"Dosya silinemedi: {e}")

        # Q-table'ı güncelle
        self.learn_from_logs()

        if not self.q_table:
            print("Uyarı: Q-table boş! Önce oyun verisi gerekiyor.")
            return

        # Tüm Q değerlerinin ortalamasını hesapla
        q_values = np.mean(list(self.q_table.values()), axis=0)  # Düzeltme burada
        heatmap_data = q_values.reshape((10, 10))

        # Heatmap oluştur
        plt.figure(figsize=(10, 8))
        heatmap = plt.imshow(
            heatmap_data,  # Düzeltilmiş veri
            cmap="viridis",
            interpolation="nearest",
            origin="upper"
        )
        plt.colorbar(heatmap, label="Q Değeri")
        plt.title(f"Güncel Q-Table Heatmap (Kullanıcı: {self.user_id})")

        # Eksen etiketleri
        plt.xticks(range(10))
        plt.yticks(range(10))

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"Yeni heatmap oluşturuldu: {save_path}")