# ai_agent.py
import random
import pickle
import os
from collections import defaultdict

# Named default factory for pickling compatibility
def default_q():
    return [0.0] * 100

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, model_path="q_table.pkl"):
        """
        alpha: learning rate
        gamma: discount factor
        epsilon: exploration rate
        model_path: file to save/load Q-table
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.model_path = model_path
        # Q-table: state -> action values, use named default factory
        self.q_table = defaultdict(default_q)
        # Load existing Q-table if available and non-empty
        if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 0:
            try:
                with open(self.model_path, 'rb') as f:
                    loaded = pickle.load(f)
                # Restore to defaultdict for future additions
                self.q_table = defaultdict(default_q, loaded)
            except (EOFError, pickle.UnpicklingError):
                # File is empty or corrupted; start fresh
                self.q_table = defaultdict(default_q)

    def state_to_key(self, search_grid):
        """
        Convert the current search grid to a hashable state key.
        search_grid: list of 100 values: 'U','H','M','S'
        """
        return ''.join(search_grid)

    def basic_heuristic(self, search_grid):
        """
        Fallback heuristic from engine.basic_ai implementation.
        """
        unknown = [i for i, v in enumerate(search_grid) if v == 'U']
        hits = [i for i, v in enumerate(search_grid) if v == 'H']

        # Neighbor-based targeting
        near1 = [u for u in unknown if any(abs(u - h) in (1,10) for h in hits)]
        near2 = [u for u in unknown if any(abs(u - h) in (2,20) for h in hits)]

        # prioritize cells satisfying both distances
        for u in unknown:
            if u in near1 and u in near2:
                return u
        if near1:
            return random.choice(near1)
        # checkerboard pattern
        checker = [u for u in unknown if (u//10 + u%10) % 2 == 0]
        if checker:
            return random.choice(checker)
        # random fallback
        return random.choice(unknown) if unknown else None

    def choose_action(self, search_grid):
        """
        Choose an action based on epsilon-greedy policy.
        Falls back to heuristic if Q-values are inconclusive.
        Returns an index (0-99).
        """
        state = self.state_to_key(search_grid)
        # Exploration
        if random.random() < self.epsilon:
            return self.basic_heuristic(search_grid)
        # Exploitation
        q_values = self.q_table[state]
        unknown = [i for i, v in enumerate(search_grid) if v == 'U']
        if not unknown:
            return None
        # select highest Q among unknown
        best = max(unknown, key=lambda i: q_values[i])
        # if best Q is zero (untrained), fallback
        if q_values[best] == 0.0:
            return self.basic_heuristic(search_grid)
        return best

    def update(self, search_grid, action, reward, next_search_grid):
        """
        Q-learning update rule:
        Q(s,a) += alpha * (reward + gamma * max_a' Q(s',a') - Q(s,a))
        """
        state = self.state_to_key(search_grid)
        next_state = self.state_to_key(next_search_grid)
        q_predict = self.q_table[state][action]
        q_target = reward
        if next_search_grid.count('U') > 0:
            q_target += self.gamma * max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (q_target - q_predict)

    def save(self):
        """
        Save Q-table to disk.
        """
        with open(self.model_path, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
