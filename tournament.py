# tournament.py
from engine import Game
from ai_agent import QLearningAgent
from matplotlib import pyplot as plt
import pygame

user_id = "ai_agent"  # AI için kullanıcı ID
agent = QLearningAgent(user_id=user_id)
agent.learn_from_logs()

n_games = 100
n_shots = []
n_wins1 = 0
n_wins2 = 0

for i in range(n_games):
    game = Game(human1=False, human2=False, username="ai_agent")
    action = agent.choose_action(game.current_search)

    while not game.over:
        if game.player1_turn:
            grid = game.player2 # AI'nın görebildiği grid
            action = agent.choose_action(grid)
            game.make_move(action)
        else:
            game.basic_ai()

    n_shots.append(game.n_shots)
    if game.result == 1:
        n_wins1 += 1
    elif game.result == 2:
        n_wins2 += 1

# Oyunlardan sonra öğrenme
agent.learn_from_logs()

# Sonuçları çiz
print(f"AI Wins: {n_wins1}, BasicAI Wins: {n_wins2}")
values = [n_shots.count(i) for i in range(17, 200)]
plt.bar(range(17, 200), values)
plt.xlabel("Total Shots")
plt.ylabel("Number of Games")
plt.title("Shot Count Distribution per Game")
plt.show()
