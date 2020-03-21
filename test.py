import pure_game as pg

BG = pg.TableTop(2)

for name in ['Tom', 'Lulu', 'Dany', 'Rayan']:
    print(f'Giving {name} a sheet')
    BG.add_player(pg.PlayerBoard(name))
    print(BG.players[-1].sheet.board)

def play_test_round(ob):
    ob.play_round()
    for player in ob.players:
        print(player.name, player.sheet.marked.astype(int).sum().sum())