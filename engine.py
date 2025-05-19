# engine.py
import random
from log_helper import create_log_data, add_move, finalize_log


class Ship:
    def __init__(self, size):
        self.size = size
        self.orientation = random.choice(["v", "h"])
        self.row = random.randrange(0, 10)
        self.col = random.randrange(0, 10)
        self.indexes = self.compute_indexes()

    def compute_indexes(self):
        if self.orientation == "h":
            if self.col + self.size > 10:
                return []
            return [self.row * 10 + self.col + i for i in range(self.size)]
        else:
            if self.row + self.size > 10:
                return []
            return [(self.row + i) * 10 + self.col for i in range(self.size)]


class Player:
    def __init__(self, human=False):
        self.human = human
        self.ships = []
        self.search = ["U"] * 100
        self.place_ships([5, 4, 3, 3, 2])
        self.indexes = [i for ship in self.ships for i in ship.indexes]

    def place_ships(self, sizes):
        for size in sizes:
            placed = False
            while not placed:
                ship = Ship(size)
                if not ship.indexes or any(i >= 100 for i in ship.indexes):
                    continue
                if ship.orientation == "h" and any(i // 10 != ship.row for i in ship.indexes):
                    continue
                if ship.orientation == "v" and any(i % 10 != ship.col for i in ship.indexes):
                    continue
                if any(i in prev for prev in [s.indexes for s in self.ships] for i in ship.indexes):
                    continue
                self.ships.append(ship)
                placed = True


class Game:
    def __init__(self, human1=False, human2=False):
        self.human1 = human1
        self.human2 = human2
        self.player1 = Player(human1)
        self.player2 = Player(human2)
        self.log = create_log_data(
            player1_ships=self.player1.ships,
            player2_ships=self.player2.ships
        )

        self.player1_turn = True
        self.computer_turn = not human1 or not human2
        self.over = False
        self.result = None
        self.n_shots = 0

    def make_move(self, index):
        if self.over:
            return
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1

        # Prevent repeat shots
        if player.search[index] != "U":
            return

        hit = index in opponent.indexes

        if hit:
            player.search[index] = "H"
            result = "hit" 
            ship_size = None
            for ship in opponent.ships:
                result = "sunk"
                for i in ship.indexes:
                    if player.search[i] == "U":
                        result = "hit"
                        ship_size = ship.size
                        break
                if result=="sunk":
                    for i in ship.indexes:
                        player.search[i] = "S"
                    ship_size = ship.size
        else:
            player.search[index] = "M"
            result = "miss"
            ship_size = None

        self.n_shots += 1
        add_move(self.log, turn=self.n_shots, player=1 if self.player1_turn else 2,
                 index=index, result=result, ship_size=ship_size)

        if all(self.player1.search[i] != "U" for i in self.player2.indexes) or \
           all(self.player2.search[i] != "U" for i in self.player1.indexes):
            self.over = True
            self.result = 1 if self.player1_turn else 2
            finalize_log(self.log, winner=self.result)
            return

        if not hit:
            self.player1_turn = not self.player1_turn
            if self.human1 != self.human2:
                self.computer_turn = not self.computer_turn

    def random_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        if unknown:
            self.make_move(random.choice(unknown))

    def basic_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        unknown_with_neighboring_hits1 = []
        unknown_with_neighboring_hits2 = []

        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u - 10 in hits or u + 10 in hits:
                unknown_with_neighboring_hits1.append(u)
            if u + 2 in hits or u - 2 in hits or u - 20 in hits or u + 20 in hits:
                unknown_with_neighboring_hits2.append(u)

        for u in unknown:
            if u in unknown_with_neighboring_hits1 and u in unknown_with_neighboring_hits2:
                self.make_move(u)
                return

        if unknown_with_neighboring_hits1:
            self.make_move(random.choice(unknown_with_neighboring_hits1))
            return

        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        if checker_board:
            self.make_move(random.choice(checker_board))
            return

        self.random_ai()
