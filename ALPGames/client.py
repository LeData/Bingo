import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.progressbar import ProgressBar
from random import choice, shuffle
from glob import glob
from os.path import dirname, join, basename, sep
from kivy.core.window import Window
from collections import defaultdict

from ./pure_game import PlayerBoard
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep


kivy.require('1.0.9')
class Dice(Button):
    checked = False
    side = StringProperty('O_O')
    ##background_normal = StringProperty(join(dirname(__file__), "icons", f'{faces[0]}.png'))

    def __init__(self, dice, **kwargs):
        self.dice_pure = dice
        super(Dice, self).__init__(**kwargs)

    def on_side(self, instance, value):
        # updates the visual of the side
        self.background_normal = join(dirname(__file__), "icons", f'{value}.png')

    def roll(self):
        self.dice_pure.roll()
        self.side = self.dice_pure.side
        # TODO: add the broadcast of the result

    def on_press(self):
        if self.parent.running and not self.dice_pure.locked:
            self.roll()
        else:
            pass


class DiceLayout(GridLayout):
    """
    #TODO: continue splitting this class in dice groups
    """
    dice = NumericProperty(0)  # total number of items
    drawn = NumericProperty(0)
    faceCount = defaultdict(int)

    def __init__(self, **kwargs):
        self.size = kwargs.pop("size")
        kwargs['cols'] = self.size
        super().__init__(**kwargs)
        self.running = False

    def start_game(self, dt):
        self.reset()
        Clock.schedule_interval(self.countdown_display, 1)

    def reset(self):
        self.countdown = 2
        self.first = None
        self.left = 0
        self.elapsed = 0
        self.running = True
        self.add_widget(Button(text=''))
        for i in range(self.dice):
            btn = Dice(
                text=""
            )
            self.add_widget(btn)
            self.add_widget(Button(text=''))

    def restartGame(self):
        self.reset()
        Clock.schedule_interval(self.countdown_display, 1)

class LabelDraw(Label):
    def updatedraw(self, value):
        self.text = f"{value}"


class BingoApp(App):

    def build(self):
        self.icon = 'memoIcon.png'
        self.title = 'Bingo with Saul'
        board_pure = BoardClient()

        top_banner = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, .1))
        drawn = LabelDraw(text="Last Drawn:  0", size_hint=(0.15, 1))
        config.add_widget(drawn)
        missed = DeclareBingo()
        config.add_widget(missed)

        shield = DiceLayout(dice=1, size_hint=(1, .35))
        Clock.schedule_once(shield.start_game, 3)

        title = Label(text=self.title, size_hint=(1, .2))

        g = DiceLayout(dice=4, size_hint=(1, .35))

        playZone = BoxLayout(orientation='vertical')
        playZone.add_widget(shield)
        playZone.add_widget(title)
        playZone.add_widget(g)
        playZone.add_widget(config)

        widgetTree = FloatLayout()
        widgetTree.add_widget(
            Image(source='Jungle_Background_-_by-vectorjungle.jpg', allow_stretch=True, keep_ratio=False))
        widgetTree.add_widget(playZone)

        return widgetTree


class BoardClient(PlayerBoard, ConnectionListener):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # connect to server
        # it seems that the listener initiates a connection by itself. To confirm.
        # connection.connect()
        self.Connect()
        self.running = False

    def listen(self):
        self.Pump()
        connection.Pump()

    def broadcast(self, message):
        """

        :param message: message to send
        """
        self.Send(message)

    def broadcast_resume(self):
        self.broadcast(super().broadcast_resume())

    def broadcast_hand(self):
        self.broadcast(super().broadcast_hand())

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


if __name__ in ('__main__', '__android__'):
    BingoApp().run()

"""
Copyright (c) 2012, Sylvain Alborini
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""