# train_agent.py
import pygame
from engine import Game
from ai_agent import QLearningAgent
from login import login_screen
import log_helper
from pathlib import Path
import matplotlib.pyplot as plt
import json

# Initialize pygame if Game uses it
pygame.init()

def self_train(n_games=500, alpha=0.1, gamma=0.9, epsilon=0.2, save_interval=50):
    """
    Self-trains the QLearningAgent by playing AI vs BasicAI.
    Saves Q-table and training stats into the currently set user_id directory.
    Requires set_username() to have been called before running.
    """
    if log_helper.user_id is None:
        raise RuntimeError("user_id not set. Call set_username() before training.")

    agent = QLearningAgent(user_id=log_helper.user_id, alpha=alpha, gamma=gamma, epsilon=epsilon)
    # Load existing logs and Q-table
    agent.learn_from_logs()

    # Prepare stats
    wins = {"AI": 0, "BasicAI": 0}
    shots = []

    # Ensure user-specific directory exists
    user_dir = Path("logs") / log_helper.user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    for i in range(1, n_games + 1):
        game = Game(human1=False, human2=False, username=log_helper.username)
        while not game.over:
            if game.player1_turn:
                prev_grid = game.current_search.copy()
                action = agent.choose_action(game.current_search)
                if action is None:
                    break
                game.make_move(action)
                result = game.current_search[action]
                reward = 1 if result == 'H' else (5 if result == 'S' else -1)
                agent.update_q(prev_grid, action, reward, game.current_search)
            else:
                game.basic_ai()

        # Record outcome
        shots.append(game.n_shots)
        winner = "AI" if game.result == 1 else "BasicAI"
        wins[winner] += 1

        # Periodic save
        if i % save_interval == 0:
            print(f"Game {i}/{n_games} complete. Wins -> AI: {wins['AI']}, BasicAI: {wins['BasicAI']}")
            agent.save()

    # Final save
    agent.save()
    print("Training complete.")

    # Compile training stats
    stats = {
        "user": log_helper.username,
        "total_games": n_games,
        "wins": wins,
        "shots": shots,
    }
    # Save stats JSON
    stats_file = user_dir / "training_stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Training stats saved to {stats_file}")

    # Plot distribution of shots and save figure
    min_shots, max_shots = min(shots), max(shots)
    counts = [shots.count(x) for x in range(min_shots, max_shots + 1)]
    plt.figure()
    plt.bar(range(min_shots, max_shots + 1), counts)
    plt.xlabel('Shots per game')
    plt.ylabel('Number of games')
    plt.title('Training Shot Distribution')
    plot_file = user_dir / "shot_distribution.png"
    plt.savefig(plot_file)
    plt.show()
    print(f"Shot distribution plot saved to {plot_file}")

if __name__ == '__main__':
    # 1) Ask for username via login screen
    username = login_screen()
    # 2) Set username in log_helper
    log_helper.set_username(username)
    # 3) Start training
    self_train(n_games=200, alpha=0.5, gamma=0.9, epsilon=0.7)

