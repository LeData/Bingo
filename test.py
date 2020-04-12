import pure_game as pg

players = ['Tom', 'Lulu', 'Dany', 'Rayan']
player_boards = {name: None for name in players}

mm = pg.Intermediary()
BG = pg.TableTop(1, mm)

for name in players:
    print(f'Giving {name} a sheet')
    player_boards[name] = pg.PlayerBoard(name, mm)
    BG.add_player(name)
    print(player_boards[name].sheet.board)

def play_test_round(master):
    master.play_round()
    for player, board in player_boards.items():
        print(player, board)