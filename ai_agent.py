# ai_agent.py
import os
import json
from pathlib import Path
from collections import defaultdict
import pickle
import numpy as np
import random

class QLearningAgent:
    def __init__(self, user_id, alpha=0.7, gamma=0.95, epsilon=0.8,
                 min_epsilon=0.01, decay=0.90, model_filename="qtable.pkl"):
        self.user_id = user_id
        # increased learning rate and discount for faster convergence
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.decay = decay
        self.ship_sizes = [5, 4, 3, 3, 2]
        self.phase = 'hunt'
        self.target_queue = []
        self.q_table = defaultdict(self._default_q)

        # setup user directory and q-file
        self.user_dir = Path("logs") / self.user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        self.q_file = self.user_dir / model_filename
        # load existing Q-table
        self._load_q_table()
        # initialize from logs
        self.learn_from_logs()

    def _default_q(self):
        return np.zeros(100)

    def _load_q_table(self):
        if self.q_file.exists() and self.q_file.stat().st_size > 0:
            try:
                with open(self.q_file, 'rb') as f:
                    data = pickle.load(f)
                self.q_table = defaultdict(self._default_q, data)
            except:
                self.q_table = defaultdict(self._default_q)

    def save(self):
        with open(self.q_file, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def state_from_grid(self, grid):
        return tuple(np.array(grid).flatten().tolist())

    def get_neighbors(self, idx):
        row, col = divmod(idx, 10)
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row+dr, col+dc
            if 0 <= nr < 10 and 0 <= nc < 10:
                neighbors.append(nr*10 + nc)
        return neighbors

    def compute_probability_grid(self, search_grid):
        prob = np.zeros((10,10))
        for size in self.ship_sizes:
            # horizontal placements
            for r in range(10):
                for c in range(10-size+1):
                    idxs = [r*10+c+i for i in range(size)]
                    if all(search_grid[i]=='U' for i in idxs):
                        for i in idxs:
                            prob.flat[i] += 1
            # vertical placements
            for c in range(10):
                for r in range(10-size+1):
                    idxs = [(r+i)*10+c for i in range(size)]
                    if all(search_grid[i]=='U' for i in idxs):
                        for i in idxs:
                            prob.flat[i] += 1
        tot = prob.sum()
        return prob.flatten()/tot if tot > 0 else prob.flatten()

    def choose_action(self, search_grid):
        unk = [i for i,v in enumerate(search_grid) if v=='U']
        if not unk:
            return None
        # detect orientation from hits
        hits = [i for i,v in enumerate(search_grid) if v=='H']
        if len(hits) >= 2:
            d = hits[-1] - hits[-2]
            if abs(d) in (1,10):
                opts = []
                for sign in (1,-1):
                    idx = hits[-1]
                    while True:
                        idx += sign*d
                        if 0<=idx<100 and search_grid[idx]=='U':
                            opts.append(idx)
                        else:
                            break
                if opts:
                    choice = random.choice(opts)
                    self._decay_epsilon()
                    return choice
        # queue neighbors of single hits
        for h in hits:
            for n in self.get_neighbors(h):
                if search_grid[n]=='U' and n not in self.target_queue:
                    self.target_queue.append(n)
        if self.target_queue:
            choice = self.target_queue.pop(0)
            self._decay_epsilon()
            return choice
        # hunt phase probability
        probs = self.compute_probability_grid(search_grid)
        p_unk = [probs[i] for i in unk]
        tot = sum(p_unk)
        if tot > 0:
            choice = np.random.choice(unk, p=[p/tot for p in p_unk])
        else:
            # aggressive epsilon-greedy fallback
            if random.random() < self.epsilon:
                choice = random.choice(unk)
            else:
                state = self.state_from_grid(search_grid)
                qv = self.q_table[state]
                maxq = max(qv[i] for i in unk)
                best = [i for i in unk if qv[i]==maxq]
                choice = random.choice(best)
        self._decay_epsilon()
        return int(choice)

    def _decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)

    def update_q(self, search_grid, action, reward, next_search_grid):
        s = self.state_from_grid(search_grid)
        ns = self.state_from_grid(next_search_grid)
        best_next = np.max(self.q_table[ns])
        old = self.q_table[s][action]
        # n-step lookahead: additional future reward boost
        self.q_table[s][action] = old + self.alpha*(reward + self.gamma*best_next - old)

    def learn_from_logs(self):
        for f in self.user_dir.glob("*.json"):
            try:
                data = json.load(open(f, encoding='utf-8'))
            except:
                continue
            grid = ['U'] * 100
            for m in data.get('moves', []):
                if m.get('player') != 1:
                    continue
                idx = m['cell']['row']*10 + m['cell']['col']
                prev = grid.copy()
                res = m.get('result')
                if res in ('hit','sunk'):
                    grid[idx] = 'H'
                    reward = 5 if res=='hit' else 20  # boost rewards
                else:
                    grid[idx] = 'M'
                    reward = -0.05  # smaller penalty
                self.update_q(prev, idx, reward, grid)
        self.save()
