# train_and_evaluate.py
import pygame
import json
from engine import Game
from ai_agent import QLearningAgent
from login import login_screen
from log_helper import set_username, get_username
from pathlib import Path
import matplotlib.pyplot as plt

# Initialize pygame if needed by Game
pygame.init()

def train_and_evaluate(n_train=300, n_eval=50,
                       alpha=0.3, gamma=0.9, epsilon_start=0.9,
                       epsilon_end=0.05, decay_rate=0.98):
    """
    Train the agent with decay on epsilon, then periodically evaluate
    against basic_ai and collect metrics.
    """
    # 1) Login and set user
    username = login_screen()
    set_username(username)
    uid = get_username()  # use as directory name

    # 2) Prepare agent
    agent = QLearningAgent(user_id=uid, alpha=alpha, gamma=gamma, epsilon=epsilon_start)
    # No need for separate learn; __init__ does it

    # 3) Training loop
    train_metrics = []  # store (episode, shots, win)
    epsilon = epsilon_start
    for episode in range(1, n_train + 1):
        game = Game(human1=False, human2=False, username=uid)
        while not game.over:
            if game.player1_turn:
                prev = game.current_search.copy()
                action = agent.choose_action(game.current_search)
                game.make_move(action)
                res = game.current_search[action]
                reward = 1 if res == 'H' else (5 if res == 'S' else -0.2)
                agent.update_q(prev, action, reward, game.current_search)
            else:
                game.basic_ai()
        win = 1 if game.result == 1 else 0
        train_metrics.append((episode, game.n_shots, win))

        # decay epsilon
        epsilon = max(epsilon * decay_rate, epsilon_end)
        agent.epsilon = epsilon

        # periodic save
        if episode % 50 == 0:
            agent.save()

    agent.save()

    # 4) Evaluation loop
    eval_metrics = []
    for eval_ep in range(1, n_eval + 1):
        game = Game(human1=False, human2=False, username=uid)
        while not game.over:
            if game.player1_turn:
                action = agent.choose_action(game.current_search)
                game.make_move(action)
            else:
                game.basic_ai()
        win = 1 if game.result == 1 else 0
        eval_metrics.append((eval_ep, game.n_shots, win))

    # 5) Save metrics
    out_dir = Path("logs") / uid
    metrics = {
        "train": train_metrics,
        "eval": eval_metrics,
        "params": {"alpha": alpha, "gamma": gamma,
                   "epsilon_start": epsilon_start,
                   "epsilon_end": epsilon_end, "decay_rate": decay_rate},
    }
    with open(out_dir / "train_eval_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'train_eval_metrics.json'}")

    # 6) Plot training win rate
    wins = [w for _, _, w in train_metrics]
    avg_win = sum(wins) / len(wins)
    print(f"Training win rate: {avg_win*100:.2f}%")

    plt.figure()
    plt.plot([ep for ep, _, _ in train_metrics],
             [shots for _, shots, _ in train_metrics], label="Shots")
    plt.xlabel("Episode")
    plt.ylabel("Shots to win")
    plt.title("Training: Shots per Episode")
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot([ep for ep, _, _ in train_metrics],
             [sum(wins[:i]) / i for i in range(1, len(wins)+1)], label="Win Rate")
    plt.xlabel("Episode")
    plt.ylabel("Cumulative Win Rate")
    plt.title("Training: Win Rate Over Time")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    train_and_evaluate()
