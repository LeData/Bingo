import PodSixNet.Channel as chnl
import PodSixNet.Server as srv
import functools
from collections import defaultdict

from pure_game import TableTop
from time import sleep


def trigger_start(func):
    """
    Decorator that starts every game in the queue of the game class
    passes its start condition after the function has run
    """
    @functools.wraps(func)
    def queue_updated(self, *args, **kwargs):
        func(self, *args, **kwargs)
        for game in self.queue:
            if game.check_start():
                self._start(game)

    return queue_updated

class ClientChannel(chnl.Channel):
    def Network(self, data):
        """
        called every time a client  does a connection.send(data)
        """
        print(data)

    def Network_XXXX(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'XXXX'}
        self._server is the instance of PodSixNet.Server.Server that the instance of this class
        was initiated in.
        """
        self.gameid = data.pop('game_id')
        self._server.score_point_for( self.gameid, data)

    def Close(self):
        self._server.close(self.gameid)


class GameServer(srv.Server):
    channelClass = ClientChannel

    def __init__(self, game_class, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.game = game_class
        self.games = {}  # games that have run or are running on the server
        self.queue = {}  # open games

    def _add_new_game_to_queue(self, length=10):
        # create new game and add it to the queue
        game_id = len(self.games) + len(self.queue) + 1
        self.queue[game_id] = self.game(game_id, length)
        return game_id

    def _start(self, game):
        for i, player in enumerate(game.players):
            player.Send({"action": "startgame", "playerid": i, "gameid": game.game_id})
        self.games.append(self.queue.pop(game))

    def close(self, gameid):
        game = [a for a in self.games if a.gameid == gameid][0]
        for player in game.players:
            try:
                player.Send({"action": "close"})
            except:
                pass

    @trigger_start
    def Connected(self, player_channel, gameid=None):
        """
        TODO: rename as new_player
        gets called whenever a new client connects to the server.
        """
        game=None
        if gameid is not None:
            if gameid in self.games.keys():
                print("this game has already started")
                return self
            if gameid not in self.queue.keys():
                print("No such game to join, creating one")

        if gameid is None:
            game = self._add_new_game_to_queue(player_channel)

        print('Player {player_channel} connected to {self.queue[0].gameid}')
        self.queue[game].add_player(player_channel)
        return self


class GameManager:

    def __init__(self, gameid):
        self.gameid = gameid
        self.started = False
        # initialize VP ownership
        # initialize the player list
        self.players = []
        self.scores = defaultdict(int)

    def add_player(self, player):
        player.gameid = self.gameid
        self.players.append(player)

    def check_start(self):
        self.started = self.players >= 2
        return self.started

    def check_end(self):
        self.terminated = len(VP) >= self.len
        return self.terminated


print("STARTING SERVER ON LOCALHOST")
DateServe = DiceServer()
while True:
    DiceServer.Pump()
    sleep(0.01)
