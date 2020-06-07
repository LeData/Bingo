from random import choice, sample
from collections import defaultdict
import numpy as np


class BingoSheet:

    def __init__(self, n=5):
        self.n = n
        self.size = n * n
        self.board = np.zeros(3 * self.size).reshape(self.n, -1)
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


class DrawingMachine:

    def __init__(self, n_max=75):
        self.n_max = n_max
        self.draws = list(np.random.choice(n_max, n_max, replace=False))
        self.round = 0

    def draw(self):
        output = None
        if self.round < self.n_max:
            output = self.draws[self.round]
            self.round += 1
        return output


class PlayerBoard:

    def __init__(self, player_name, intermediary):
        """
        :param player_name: name of the player
        """
        self.name = player_name
        self.broadcast_channel = intermediary
        self.broadcast_channel.add_player(self)
        self.sheet = BingoSheet()

    def play_round(self, number):
        match = self.sheet.add_number(number)
        message = f"YAY! got it." if match else f"Ohhhh :( I don't have {number}"
        self.broadcast("react", text=message)
        self.check_win()
        return match

    def check_win(self):
        has_won = self.sheet.check_win()
        self.broadcast("win", result=has_won)
        return has_won


    def count_matches(self):
        hits = self.sheet.marked.astype(int).sum().sum()
        return hits

    def reset(self):
        self.sheet.reset()

    def broadcast(self, func_name, **kwargs):
        """
        Sends a message to the intermediary, so they relay the corresponding action to the desires players
        :param player: individual player or 'all'
        :param func_name: type of message / action to take
        :param kwargs: list of kwargs that the message / action requires
        :return:
        """
        order = {
            'source': self.name,
            'action': func_name,
            **kwargs
        }
        self.broadcast_channel.collect(order=order)


class TableTop:

    def __init__(self, win_vp, intermediary):
        self.broadcast_chanel = intermediary
        self.broadcast_chanel.add_master(self)
        self.started = False
        self.players = []
        self.n_players = len(self.players)
        self.win_VP = win_vp
        self.VP = [None] * self.win_VP
        self.engine = DrawingMachine()

    def add_player(self, player_name):
        self.players.append(player_name)
        self.n_players = len(self.players)

    def allocate_point(self, player):
        for i, point in enumerate(self.VP):
            if point is None:
                if player in self.players:
                    self.VP[i] = player
                    print(f"Saul Goodman: Congratulations to {player} for winning round {i+1} on {len(self.VP)}.")
                else:
                    print(f"Saul Goodman: {player}, did you forget to pay the registration fee?")
                continue
        remaining_games = [i for i,winner in enumerate(self.VP) if winner is None]
        if len(remaining_games) == 0:
            print("Saul Goodman: The game is finished. Thanks to all the participants")
        #self.broadcast('all', 'game-over',)
        # TODO: broadcast/update scores on screens

    def play_round(self):
        round_number = self.engine.draw()
        self.broadcast('all', 'round', number=round_number)
        return self

    def record_win(self, player, result):
        if result:
            self.allocate_point(player)
            self.broadcast('all', 'reset')
            self.reset()
        return self

    def reset(self):
        self.engine = DrawingMachine()

    def broadcast(self, player, func_name, **kwargs):
        """
        Sends a message to the intermediary, so they relay the corresponding action to the desires players
        :param player: individual player or 'all'
        :param func_name: type of message / action to take
        :param kwargs: list of kwargs that the message / action requires
        :return:
        """
        order = {
            'target': player,
            'action': func_name,
            **kwargs
        }
        self.broadcast_chanel.distribute(order)


class Intermediary:

    def __init__(self):
        self.master_actions = {
            'win': self.pass_win,
            'react': self.pass_msg
        }
        self.player_actions = {
            'reset': self.pass_reset,
            'round': self.pass_round
        }
        self.targets = []
        self.master = None

    def add_player(self, player):
        self.targets.append(player)

    def add_master(self, master):
        self.master = master

    def distribute(self, order):
        """
        sends message to
        :param order:
        :return:
        """
        func_name = order.pop('action')
        func = self.player_actions[func_name]
        pass_to = order.pop('target')
        #print(f"Itermediary : passing {func_name} order to {pass_to}")
        if pass_to == 'all':
            targets = self.targets
        else:
            targets = [target for target in self.targets if pass_to == target.name]
        for target in targets:
            func(target, **order)

    def collect(self, order):
        func_name = order.pop('action')
        func = self.master_actions[func_name]
        passed_from = order.pop('source')
        #print(f"Itermediary : passing {func_name} order to master from {passed_from}")
        func(passed_from, **order)

    @staticmethod
    def pass_round(target, **kwargs):
        target.play_round(**kwargs)

    @staticmethod
    def pass_reset(target, *args, **kwargs):
        target.reset(*args, **kwargs)

    def pass_win(self, source, **kwargs):
        self.master.record_win(source, **kwargs)

    @staticmethod
    def pass_msg(source, **kwargs):
        speaker =source
        msg = kwargs["text"]
        print(f"{speaker}: {msg}")
