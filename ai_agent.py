# ai_agent.py
import os
import json
from pathlib import Path
from collections import defaultdict
import pickle
import numpy as np
import random

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
                # extend in both directions from first and last hit
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
        combined = self.user_dir / "combined_logs.json"
        entries = []
        if combined.exists():
            try:
                with open(combined, encoding='utf-8') as f:
                    entries = json.load(f)
            except Exception:
                entries = []
        for data in entries:
            grid = ['U'] * 100
            for move in data.get('moves', []):
                if move.get('player') != 1:
                    continue
                idx = move['cell']['row'] * 10 + move['cell']['col']
                prev = grid.copy()
                res = move.get('result')
                if res in ('hit', 'sunk'):
                    grid[idx] = 'H'
                    reward = 1 if res == 'hit' else 10
                else:
                    grid[idx] = 'M'
                    reward = -0.05
                self.update_q(prev, idx, reward, grid)
        self.save()
