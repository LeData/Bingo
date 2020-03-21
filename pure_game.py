from random import choice, sample
from collections import defaultdict
import numpy as np

class BingoSheet():

    def __init__(self, n=5):
        self.n = n
        self.size = n * n
        self.board = None
        self.marked = None
        self.reset()

    def add_number(self, number):
        matches = self.board == number
        matched = matches.any().any()
        if matched:
            self.marked = self.marked | matches
        return matched

    def check_win(self):
        won = (self.marked.all(axis=1).any()
               or self.marked.all(axis=0).any()
               or np.diag(self.marked).all()
               or np.diag(self.marked[::-1]).all()
               )
        return won

    def reset(self):
        self.board = np.random.choice(3 * self.size, self.size, replace=False).reshape(self.n, -1)
        self.marked = np.zeros((self.n, self.n)).astype(bool)

class PlayerBoard():

    def __init__(self, player_name):
        """
        :param player_name: name of the player
        """
        self.name = player_name
        self.sheet = BingoSheet()
        self.actions = {
            "tick" : {"action": "print", "message" : f"{self.name} : YAY! got it."},
            "win" : {"action": "win", "message" : f"{self.name} : BINGO !!"},
            "resume": {'action': 'resume'}
            }

    def play_round(self, number):
        match = self.sheet.add_number(number)
        if match:
            self.broadcast("tick")
        has_won = self.sheet.check_win()
        if has_won:
            self.broadcast("win")
        return self

    def broadcast(self, action):
        return self.actions["action"]

    def reset(self):
        self.sheet.reset()


class DrawingMachine:

    def __init__(self, n_max=75):
        self.n_max = n_max
        self.future_draws = list(np.random.choice(n_max, n_max, replace=False))
        self.drawn = []
        self.number_drawn = 0

    def draw(self):
        self.drawn.append(self.future_draws.pop())
        output = self.drawn[-1]
        print(f"Saul Goodman: and the number is ..... {output}")
        return output


class TableTop:

    def __init__(self, win_vp, intermediary):
        self.broadcast_chanel = intermediary
        self.started = False
        self.players = []
        self.n_players = len(self.players)
        self.win_VP = win_vp
        self.VP = [None] * self.win_VP
        self.engine = DrawingMachine()

    def add_player(self, player_board):
        #TODO: remove direct link to player board here
        self.players.append(player_board)
        self.n_players = len(self.players)

    def allocate_point(self, player):
        for i, point in enumerate(self.VP):
            if point is None:
                self.VP[i] = player.name
                return self.VP
        self.broadcast_end()
        # TODO: broadcast/update scores on screens

    def play_round(self):
        round_number = self.engine.draw()
        self.broadcast('all', 'round', number=round_number)
        return self

    def check_win(self, player, result):
        if result:
            self.allocate_point(player)
            self.broadcast('all', 'reset')
            self.reset()
        return self

    def reset(self):
        self.engine = DrawingMachine()

    def broadcast(self, player, func_name, **kwargs):
        order = {
            'target': player,
            'action': func_name,
            **kwargs
        }
        self.broadcast_chanel.distribute(order)


class Intermediary():

    def __init__(self):
        self.action_dict = {
            'reset': self.pass_reset,
            'round' : self.pass_round
        }
        self.targets = []

    def distribute(self, order):
        func_name = order.pop('action')
        func = self.action_dict(func_name)
        pass_to = order.pop('target')
        if pass_to == 'all':
            targets = self.targets
        else:
            targets = [target for target in self.targets if pass_to == target.name]
        for target in targets:
            func(target, **order)

    def gather(self, order):


    def pass_round(self, target, **kwargs):
        target.play_round(*kwargs)

    def pass_reset(self, target, *args, **kwargs):
        target.reset(*args , **kwargs)

    def receive_round(self, source, **kwargs):
        order = {
            'target': source,
            **kwargs
        }
