import random
from re import search


class Ship:
    def __init__(self, size):
        self.row = random.randrange(0,9)
        self.col = random.randrange(0,9)
        self.size = size
        self.orientation = random.choice(["v","h"])
        self.indexes = self.compute_indexes()

    def compute_indexes(self):
        start_index = self.row *10 + self.col
        if self.orientation == "h":
            return[start_index + i for i in range(self.size)]
        elif self.orientation == "v":
            return[start_index + i * 10 for i in range(self.size)]

class Player:
    def __init__(self):
        self.ships = []
        self.search = ["U" for i in range(100)] # "U" for "Unknown"
        self.place_ships(sizes = [5,4,3,3,2])
        list_of_lists = [ship.indexes for ship in self.ships]
        self.indexes = [index for sublist in list_of_lists for index in sublist]


    def place_ships(self, sizes):
        for size in sizes:
            placed = False
            while not placed:
                #create a new ship
                ship = Ship(size)
                #check if placement is possible
                possible = True
                for i in ship.indexes:
                    #indexes must be below 100
                    if i >= 100:
                        possible = False
                        break
                    # ships cannot behave like "snake" in the "snake game"
                    new_row = i // 10
                    new_col = i % 10
                    if new_row != ship.row and new_col != ship.col:
                        possible = False
                        break

                    # ships cannot intersect
                    for other_ship in self.ships:
                        if i in other_ship.indexes:
                            possible = False
                            break
                # place the ship
                if possible:
                    self.ships.append(ship)
                    placed = True

    def show_ships(self):
        indexes = ["-" if i not in self.indexes else "X" for i in range(100)]
        for row in range(10):
            print(" ".join(indexes[(row-1)*10:row*10]))

            player = Player()
            player.show_ships()
            print(player.ships)
            print(player.indexes)


class Game:
    def __init__(self, human1, human2):
        self.human1 = human1
        self.human2 = human2
        self.player1 = Player()
        self.player2 = Player()
        self.player1_turn = True
        self.computer_turn = True if not self.human1 else False
        self.over = False
        self.result = None

    def make_move(self, i):
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1
        hit = False

        # set miss "M" or hit "H"
        if i in opponent.indexes:
            player.search[i] = "H"
            hit=True

            # check if ship is sunk ("S")
            for ship in opponent.ships:
                sunk = True
                for i in ship.indexes:
                    if player.search[i] == "U":
                        sunk = False
                        break
                if sunk:
                    for i in ship.indexes:
                        player.search[i] = "S"

        else:
            player.search[i] = "M"


        #check if game over
        game_over = True
        for i in opponent.indexes:
            if player.search[i] == "U":
                game_over = False
        self.over = game_over
        self.result = 1 if self.player1_turn else 2


        # change the active team
        if not hit:
            self.player1_turn = not self.player1_turn


        # switch between human and computer turns
            if (self.human1 and not self.human2) or (not self.human1 and self.human2):
                self.computer_turn = not self.computer_turn

    def random_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        if len(unknown) >0:
            random_index = random.choice(unknown)
            self.make_move(random_index)







