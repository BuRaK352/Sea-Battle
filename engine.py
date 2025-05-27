# engine.py
import random
from log_helper import create_log_data, add_move, finalize_log, set_username

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
    def __init__(self, human1=False, human2=False, username=None):
        # Kullanıcı adı verildiyse set et
        if username:
            set_username(username)
        self.human1 = human1
        self.human2 = human2
        self.player1 = Player(human1)
        self.player2 = Player(human2)
        # Log oluştur
        self.log = create_log_data(
            player1_ships=self.player1.ships,
            player2_ships=self.player2.ships
        )
        self.player1_turn = True
        self.computer_turn = not human1 or not human2
        self.over = False
        self.result = None
        self.n_shots = 0

    @property
    def current_search(self):
        return self.player1.search if self.player1_turn else self.player2.search

    @property
    def opponent(self):
        return self.player2 if self.player1_turn else self.player1

    def make_move(self, index):
        if self.over:
            return
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1
        # Tekrar eden vuruşu engelle
        if player.search[index] != "U":
            return
        hit = index in opponent.indexes
        if hit:
            player.search[index] = "H"
            result = "hit"
            for ship in opponent.ships:
                if index in ship.indexes:
                    if all(player.search[i] != "U" for i in ship.indexes):
                        for i in ship.indexes:
                            player.search[i] = "S"
                        result = "sunk"
                    break
        else:
            player.search[index] = "M"
            result = "miss"
        self.n_shots += 1
        add_move(self.log, turn=self.n_shots, player=1 if self.player1_turn else 2,
                 index=index, result=result, ship_size=None)
        # Oyun bitti mi?
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
        unknown = [i for i, sq in enumerate(self.current_search) if sq == "U"]
        if unknown:
            self.make_move(random.choice(unknown))

    def basic_ai(self):
        unknown = [i for i, sq in enumerate(self.current_search) if sq == "U"]
        hits = [i for i, sq in enumerate(self.current_search) if sq == "H"]
        near = [u for u in unknown if any(abs(u-h) in (1, 10) for h in hits)]
        if near:
            self.make_move(random.choice(near))
            return
        checker = [u for u in unknown if (u//10 + u%10) % 2 == 0]
        if checker:
            self.make_move(random.choice(checker))
            return
        self.random_ai()
