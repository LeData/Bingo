import numpy as np



class PlayerBoard:

    def __init__(self, player_name):
        """
        :param player_name: name of the player
        """
        self.name = player_name
        self.sheet = BingoSheet()

    def play_round(self, number):
        match = self.sheet.add_number(number)
        return match

    def check_win(self):
        has_won = self.sheet.check_win()
        return has_won

    def count_matches(self):
        hits = self.sheet.marked.astype(int).sum().sum()
        return hits

    def reset(self):
        self.sheet.reset()


class TableTop:

    def __init__(self):
        self.engine = DrawingMachine()

    def draw(self):
        drawn_number = self.engine.draw()
        return drawn_number

    def reset(self):
        self.engine = DrawingMachine()


class Game:

    def __init__(self, players):
        self.players = {player: PlayerBoard(player) for player in players}
        self.tt = TableTop()

    def play_round(self):
        self.tt.draw()

    def reset(self):
        for board in self.players.values():
            board.reset()
        self.tt.reset()