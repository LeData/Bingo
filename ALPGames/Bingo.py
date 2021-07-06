import numpy as np


def check_tic_tac_toe(boolean_array):
    won = (boolean_array.all(axis=1).any()
           or boolean_array.all(axis=0).any()
           or np.diag(boolean_array).all()
           or np.diag(boolean_array[::-1]).all()
           )
    return won

# -----------------------------------------------------------------------------------------------------------------------
# BOTS
# -----------------------------------------------------------------------------------------------------------------------


class GameBot():
    """
    This class is here to simulate an actual GM.
    """
    def __init__(self):
        pass


class PlayerBot:
    """
    This class is here to simulate an actual player.
    """
    def __init__(self, board):
        self.board = board

    @staticmethod
    def add_number_to(number, sheet):
        if sheet.full:
            return None
        else:
            matches = sheet.board == number
            matched = matches.any().any()
            if matched:
                sheet.marked = sheet.marked | matches
            sheet.full = sheet.marked.all().all()
            return matched

    @staticmethod
    def check_win_for(sheet):
        won = (sheet.marked.all(axis=1).any()
               or sheet.marked.all(axis=0).any()
               or np.diag(sheet.marked).all()
               or np.diag(sheet.marked[::-1]).all()
               )
        return won

# -----------------------------------------------------------------------------------------------------------------------
# GAME COMPONENTS
# -----------------------------------------------------------------------------------------------------------------------


class BingoSheet:

    def __init__(self, n=5, numbers=None):
        # initiate variables
        self.n = n
        self.size = n * n
        self.board = np.zeros((self.n, self.n))
        self.marked = np.zeros((self.n, self.n), dtype=bool)
        self.full = False
        # initiate board
        self.reset(numbers)

    def mark(self, pos):
        """
        Marking a number/position as drawn. The position is relative to the top left corner of the sheet.
        :param pos: position (pair of ints)
        :return:
        """
        try:
            self.marked[pos] = True
        except IndexError:
            print("index out of bounds on bingo board")

        return self

    def reset(self, numbers):
        if numbers is None:
            number_array = np.random.choice(3 * self.size, self.size, replace=False)
        else:
            size = len(numbers)
            error_message = f"{self.size} numbers were expected to initiate the bingo sheet, {size} were passed "
            assert(size == self.size), error_message
            number_array = np.array(numbers)

        self.board = number_array.reshape(self.n, -1)
        self.marked = np.zeros((self.n, self.n), dtype=bool)


class DrawingMachine:

    def __init__(self, n_max=75, n_rounds=75):
        self.n_max = n_max
        self.n_rounds = n_rounds
        self.draws = list(np.random.choice(n_max, n_max, replace=False))
        self.round_played = 0

    def draw(self):
        output = None
        if self.round_played < len(self.draws):
            output = self.draws[self.round_played]
            self.round_played += 1
        return output

# -----------------------------------------------------------------------------------------------------------------------
# BOARDS
# -----------------------------------------------------------------------------------------------------------------------


class PlayerBoardNaked:
    """
    This class is "naked", i.e. it only contains player board states. It is used to represent the other players
    on the client side.
    """
    def __init__(self, name, n_sheets=1):
        """
        Defines all the variables of the board
        """
        self.sheets = [BingoSheet() for i in range(n_sheets)]
        self.playing = False
        self.name = name


class PlayerBoardLazy(PlayerBoardNaked):
    """
    This class is "lazy", i.e. it does not contain any game logic that the client cannot be trusted with.
    In its bare bones version, it contains variables and methods which impact directly the outer components of the game
    (other players and game board / GM)
    It is used to represent the client player on the client side.
    """

    def o_claim_win(self):
        return {"action": "bingo", "player": self.name}


class PlayerBoard(PlayerBoardLazy):
    """
    This is the full player board class, with the game logic and all methods needed to function. It is used to represent
    all players on the server side.
    """

    def s_mark(self, pos, sheet_id=0):
        """
        Actions that only impact the internal state of the board
        :return:
        """
        self.sheets[sheet_id].mark(pos)
        return self

    def i_get_new_sheet_for(self, sheet_id, numbers):
        """
        Actions that are mandated from the outside, or receive information from the outside
        :return:
        """
        self.sheets[sheet_id].reset(numbers)
        return self

    def i_get_number(self, number):
        print(f"newest_number: {number}")
        return self

    def i_end_round(self):
        self.playing = False


class GameBoardNaked:
    """
    This class is "naked", i.e. it only contains game board states. It is used to represent the exposed elements of
    game board on the client side.
    """
    def __init__(self):
        """
        Defines all the variables of the board
        """
        self.drawn_numbers = []

    @property
    def last_drawn(self):
        try:
            return self.drawn_numbers[-1]
        except IndexError:
            return 0


class GameBoard(GameBoardNaked):
    """
    This class contains all the logic of the game board, but none of the interaction logic of the game.
    """

    def __init__(self):
        """
        Defines all the variables of the board
        """
        super(GameBoard, self).__init__()
        self.machine = DrawingMachine()

    def o_draw_number(self):
        """
        Action whose result is outgoing, i.e. impacts the board or other players
        :return:
        """
        number_drawn = self.machine.draw()
        self.drawn_numbers.append(number_drawn)

    def i_confirm_win(self, sheet):
        pass

# -----------------------------------------------------------------------------------------------------------------------
# GAME
# -----------------------------------------------------------------------------------------------------------------------


class GameLazy:

    def __init__(self, player, opponents):
        self.GM = GameBoardNaked()
        self.player = PlayerBoardLazy(player)
        self.opponents = {opponent: PlayerBoardNaked(opponent) for opponent in opponents}
        self.started = False
        self.wins = []


class Game:
    """
    This class contains the game board, the player boards and all the logic between.
    """

    def __init__(self, players):
        self.GM = GameBoard()
        self.players = {player: PlayerBoard(name='Larry') for player in players}
        self.started = False
        self.wins = []

    def o_start(self):
        self.started = True

    def i_check_win(self, sheet):
        real_marked = np.isin(sheet.board, self.GM.drawn_numbers)
        board_to_check = real_marked & sheet.marked
        won = check_tic_tac_toe(board_to_check)
        print(won)
        return won

    def o_declare_winner(self, player):
        pass

    def o_give_new_card(self, player):
        pass

    def new_round(self):
        self.GM.o_draw_number()

    def s_reset(self):
        pass

