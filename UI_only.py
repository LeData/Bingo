import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ObjectProperty, NumericProperty

from ALPGames.Bingo import GameLazy
import numpy as np
from functools import partial
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep


kivy.require('1.0.9')

class MainWindow(Screen):
    pass

class BoardWindow(Screen):
    pass

class Windows(ScreenManager):
    pass

class BingoSquare(Button):

    def __init__(self, mark_fct, **kwargs):
        self.mark_fct = mark_fct
        self.font_size = '40sp'
        super().__init__(**kwargs)

    def on_press(self):
        self.mark_fct()
        self.font_size = '10sp'
        self.halign= 'left'
        self.valign= 'bottom'
        self.background_color =(1, 0.5, 0.24, 1)

class CheckWin(Button):

    def __init__(self, check_fct, **kwargs):
        self.check_fct = check_fct
        self.font_size = '40sp'
        super().__init__(**kwargs)

    def on_press(self):
        won = self.check_fct()
        if won:
            self.text = 'WON THE GAME!'
        else:
            self.disabled = True
            self.text = "FALSE ALARM"


class Drawn(Label):
    def update(self, value):
        self.text = f"{value}"


class Sheet(GridLayout):

    def __init__(self, sheet):
        self.sheet = sheet
        size = self.sheet.n
        kwargs = {"cols": size}
        super().__init__(**kwargs)

        self.board = {pos: BingoSquare(text=f'{self.sheet.board[pos]}', mark_fct = partial(self.sheet.mark,pos))
                      for pos, val in np.ndenumerate(self.sheet.board)}
        for box in self.board.values():
            self.add_widget(box)

class PlayerView(GameLazy, ConnectionListener):

    def __init__(self, name, opponents):
        GameLazy.__init__(self,name, opponents=opponents)
        self.Connect()
        self.connected = False

    def listen(self):
        connection.Pump()
        self.Pump()

    def o_claim_win(self):
        connection.send({"action": "claim_win", "player": "me"})

    def Network_startgame(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'startgame'}
        """
        self.running = True
        self.playerid = data["playerid"]
        self.gameid = data["gameid"]

    def Network_connected(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'connected'}
        """
        print("connected to the server")
        self.connected = True

    def Network_error(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'error'}
        """
        print("error:", data['error'][1])

    def Network_disconnected(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'disconnected'}
        """
        print("disconnected from the server")


class BingoApp(PlayerView, App):

    def __init__(self, name, players = ["Joe"]):
        PlayerView.__init__(self, name, opponents=players)
        App.__init__(self)

    def build(self):
        top_banner = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, .1))
        self.drawn = Drawn(text="O_O", font_size="40sp", size_hint=(0.15, 1))
        top_banner.add_widget(self.drawn)
        claim_fct = self.player.o_claim_win
        top_banner.add_widget(CheckWin(text='BINGO !',
                                     check_fct = claim_fct))

        self.title = 'Bingo with Saul Goodman'
        title = Label(text=self.title, size_hint=(1, .2))

        g = Sheet(sheet = self.player.sheets[0])

        playZone = BoxLayout(orientation="vertical")
        playZone.add_widget(title)
        playZone.add_widget(top_banner)
        playZone.add_widget(g)

        self.window = playZone
        Clock.schedule_interval(self.play_round, 3)

        return self.window

    def play_round(self, instance):
        self.new_round()
        self.drawn.update(self.GM.drawn_numbers[-1])


if __name__ in ("__main__", "__android__"):
    BingoApp('me').run()

"""
Copyright (c) 2012, Sylvain Alborini
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""