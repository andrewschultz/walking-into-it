'''ttt.py: tic tac toe in python
# where you meet a kid who wants to beat you, but not after you make obvious dumb mistakes'''

from __future__ import print_function
import textwrap
import random
import sys
from collections import defaultdict
import os

# local imports
import mt

# for debugging only
# import traceback

tree_move_dict = defaultdict(int)
tree_move_status = defaultdict(int)
tree_text = defaultdict(int)
inverse = defaultdict(int)
cell_idx = defaultdict(int)

win_logs = defaultdict(lambda: defaultdict(bool))
win_msg = defaultdict(lambda: defaultdict(str))

# these could/should be sent to a text_arrays dictionary later
text_arrays = defaultdict(list)

on_off = [ 'on', 'off' ]
play_ary = [ '-', 'X', 'O' ]
MY_COLOR = 1
KID_COLOR = 2

NO_MOVE = -1

# constants are listed in order of descending difficulty for the ghost
CENTER = 1
CORNER = 2
SIDE = 3

NONE_FIRST = 0
PLAYER_FIRST = 1
KID_FIRST = 2

# x-or-o differences
X_FIRST = 0
O_FIRST = 1
X_PLAYER = 2
O_PLAYER = 3

turn_option_descriptions = [ 'X goes first', 'O goes first', 'Player is X', 'Player is O' ]
square_placement_descriptions = [
'upper left', 'upper side', 'upper right',
'left side', 'center', 'right side',
'lower left', 'lower side', 'lower right'
]

locations = [ CORNER, SIDE, CORNER, SIDE, CENTER, SIDE, CORNER, SIDE, CORNER ]
location_types = [ CORNER, SIDE, CENTER ]
colors = [ PLAYER_FIRST, KID_FIRST ]

wins = [ [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6] ]

debug = False
check_needed = False
descriptions_not_ascii = False

term_width = 5000

CONTINUE_PLAYING = 0
BOARD_FULL_DRAW = -1
YOU_WON = 1 # should never happen but just in case
KID_WON = 2

intro_array = []

def python_2_checkoffs():
    # pylint: disable=redefined-builtin,undefined-variable,global-statement
    ''' python 3 can detect terminal size. python 2 can't.
    But we need to give a default term_width to call functions.
    We make it ridiculously large, because text-wrapping isn't critical.'''
    try:
        input = raw_input
    except:
        pass

    try:
        global term_width
        term_width = os.get_terminal_size().columns
    except:
        temp = input("Since you seem to be using Python 2, "
            "I want to ask you for your preferred terminal width."
            "This only affects text-wrapping for paragraphs of text, "
            "so you can just ignore this question if you'd like.")
        if temp.isdigit():
            term_width = int(temp)

# thanks to https://stackoverflow.com/a/21659588/6395052
def _find_getch():
    # pylint: disable=import-outside-toplevel,invalid-name
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        temp = msvcrt.getch()
        if temp in (b'\x03', b'\x11'):
            sys.exit("Bye!")
        return temp

    # POSIX system. Create and return a getch that manipulates the tty.
    import tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch()

CR_NONE = 0
CR_AFTER = 1
CR_BEFORE = 2
CR_BOTH = 3

def my_text_wrap(text, carriage_returns = CR_AFTER, refresh_terminal_size = False):
    '''wraps a string of text'''
    if refresh_terminal_size:
        global term_width
        try:
            term_width = os.get_terminal_size().columns
        except:
            pass
    if carriage_returns & CR_BEFORE:
        print()
    for temp in text.split("\n"):
        for x in textwrap.wrap(temp, term_width):
            print(x)
    if carriage_returns & CR_AFTER:
        print()

def my_text_wrap_array(text_array, carriage_returns = CR_AFTER, extra_carriage_return = False):
    '''wraps an array of text strings, with carriage returns as specified'''
    if carriage_returns == CR_AFTER and extra_carriage_return:
        print()
    for line in text_array:
        my_text_wrap(line, carriage_returns)
    if carriage_returns == CR_BEFORE and extra_carriage_return:
        print()

def show_introductory_text():
    '''this gets basic options from the player, allowing you to skip the full introduction'''
    if os.path.exists("debug-skip-intro.txt"):
        if os.stat("debug-skip-intro.txt").st_size:
            print("debug-skip-intro.txt exists and is not blank, so I am skipping the intro. "
            "This is probably just for testing.")
            return
        print("debug-skip-intro.txt exists, but it is blank, so I am not skipping the intro.")
    count = 0
    print("First, this game can give short descriptions instead of small ASCII art.")
    while 1:
        print("Would you like to see the descriptions instead of ASCII art? Y/N")
        raw = _find_getch().decode().lower()
        if raw == 'y':
            global descriptions_not_ascii
            descriptions_not_ascii = True
            break
        if raw == 'n':
            break
    my_text_wrap("If you've read the introduction before, you can "
        "(S)how the remaining introductory text without pauses ({} chunks left) or "
        "(F)ast-forward to ignore the remaining text. "
        "You can also push any key to read the next bit, starting now.".format(
            len(text_arrays["intro"])), carriage_returns = CR_NONE)
    wait_for_pause = True
    while count < len(text_arrays["intro"]):
        if wait_for_pause:
            raw = _find_getch()
            if raw == b'\x03':
                print("Bailing.")
                sys.exit()
            raw = raw.decode().lower()
            if raw == 's':
                wait_for_pause = False
            elif raw == 'f':
                return
        my_text_wrap(text_arrays["intro"][count])
        count += 1
    if not wait_for_pause:
        print()

def dump_text(my_idx, resize = True):
    '''given an array of text read from ttt.txt, we print it out with appropriate line spacing'''
    if resize:
        global term_width
        try:
            term_width = os.get_terminal_size().columns
        except:
            pass
    my_text_wrap_array(text_arrays[my_idx])

class GameTracker:
    '''this is the main thing that keeps track of how the kid won'''
    my_move = PLAYER_FIRST
    board = []
    moves = []
    cell_idx = defaultdict(int)
    win_logs = defaultdict(lambda: defaultdict(bool))
    win_msg = defaultdict(lambda: defaultdict(str))
    blocks_this_game = 0
    victories = 0
    fork_position = 0
    played_correctly = 0
    current_mover = NONE_FIRST
    current_first = NONE_FIRST
    won_forks = []
    first_square_type = 0
    show_moves = False
    display_type = 0
    brief_question = False
    descriptions_not_ascii = False

    def __init__(self):
        self.init_wins()
        self.win_msg = win_msg
        show_introductory_text()
        self.clear_and_restart_game()

    def init_wins(self):
        '''make sure we have tracked all possible win states'''
        for x in location_types:
            for y in colors:
                self.win_logs[y][x] = False

    def clear_and_restart_game(self):
        '''clear the board and moves data after choosing who starts'''
        self.board = [0] * 9
        self.moves = []
        self.cell_idx.clear()
        self.blocks_this_game = 0
        self.current_first = self.current_mover = self.choose_sides()
        if self.current_first == MY_COLOR:
            self.show_board()

    def choose_sides(self):
        '''user input for who goes first, unless the kid won all 3 configurations
        where one of you goes first'''
        need_you_first = self.left_specific_player_first(PLAYER_FIRST)
        need_kid_first = self.left_specific_player_first(KID_FIRST)
        if not need_kid_first and not need_you_first:
            sys.exit("Hooray! The kid is happy to have beaten you in all possible ways. "
                "This should not be shown, but it is.")
        if not need_kid_first:
            print("Since the kid has won starting in the corner, center and sides, you go first.")
            return PLAYER_FIRST
        if not need_you_first:
            print("Since the kid has won all three ways with you first, the kid starts.")
            return KID_FIRST
        while 1:
            if not self.current_first:
                who_now = ''
            else:
                who_now = ", (enter) = keep going " + \
                    'first' if self.current_first == 1 else 'second'
            who_moves = input("A new game. Who moves first? 1 = you, 2 = the kid{}.". \
                format(who_now)).lower().strip()
            if not who_moves:
                if self.current_first:
                    return self.current_first
                continue
            if who_moves[0] == '1':
                return PLAYER_FIRST
            if who_moves[0] == '2':
                return KID_FIRST

    def kid_start_square(self):
        '''pick a square the kid can start on that might help you win the game'''
        picks_list = list([x for x in self.win_logs[KID_FIRST] if not self.win_logs[KID_FIRST][x]])
        self.first_square_type = random.choice(picks_list)
        if self.first_square_type == CENTER:
            return 4
        if self.first_square_type == SIDE:
            return random.choice([1,3,5,7])
        if self.first_square_type == CORNER:
            return random.choice([0,2,6,8])
        print("Uh-oh, I couldn't find a way for the kid to get started.")
        return -1

    def check_board(self, this_board = None):
        '''check for win or draw'''
        if this_board is None:
            this_board = self.board
        if this_board[2] and this_board[2] == this_board[4] == this_board[6]:
            d_print("Diagonal match UL/DR.")
            return this_board[2]
        if this_board[0] and this_board[0] == this_board[4] == this_board[8]:
            d_print("Diagonal match UR/DL.")
            return this_board[0]
        for x in range(0, 3):
            if this_board[3*x] and this_board[3*x] == this_board[3*x+1] == this_board[3*x+2]:
                d_print("Horizontal match: row {}".format(x))
                return this_board[3*x]
            if this_board[x] and this_board[x] == this_board[x+3] == this_board[x+6]:
                d_print("Vertical match: row {}".format(x))
                return this_board[x]
        for x in range(0, 9):
            if not this_board[x]:
                return CONTINUE_PLAYING
        return BOARD_FULL_DRAW

    def check_game_result(self):
        # pylint: disable=too-many-return-statements
        '''check if the game result furthers your progress'''
        game_result = self.check_board(self.board)
        if game_result == CONTINUE_PLAYING:
            return False
        if game_result == MY_COLOR:
            print("Somehow, you won, but you should not have.")
            return True
        if game_result == BOARD_FULL_DRAW:
            print("It's a stalemate. You need to play again.")
            return True
        print("The kid won!")
        if not self.played_correctly:
            print("But they look {} unhappy. "
                "\"No fair! I'm not a baby! You made it too easy.\"".format(
                'really' if self.fork_position else 'slightly'))
            return True
        if self.win_logs[self.current_first][self.first_square_type]:
            print("But sadly, they don't look that happy. They already beat you that way!")
            return True
        for x in self.won_forks:
            if x == self.fork_position:
                print("You're a bit surprised when the kid proclaims "
                "they already won from this exact position, so it really shouldn't count.")
                return True
            if is_rotated(x, self.fork_position):
                print("You're a bit surprised when the kid starts mentioning how "
                "this win LOOKED sort of like another one, "
                "so they're not sure if it should count. "
                "You undo the last couple moves and rotate and flip the board in your head, "
                "and yeah, you have to agree.")
                return True
        self.won_forks.append(self.fork_position)
        my_text_wrap(self.win_msg[self.current_first][self.first_square_type])
        self.win_logs[self.current_first][self.first_square_type] = True
        print(text_arrays["win_progress"][self.victories])
        print()
        self.victories += 1
        if self.victories == len(text_arrays["win_progress"]):
            sys.exit()
        return True

    def move(self, move_color, move_square):
        if self.board[move_square]:
            print("Already occupied!")

    def print_all_sums(self):
        for z in all_sums_from_board(self.board):
            print(z)

    def left_specific_player_first(self, this_player):
        for x in self.win_logs[this_player]:
            if not self.win_logs[this_player][x]:
                return True
        return False

    def print_wins_so_far(self):
        if not self.victories:
            print("So far, the kid hasn't notched any interesting or worthwhile wins. Yet.".format
                (self.victories))
            return
        print("So far, you have let the kid win {} unique ways, total.".format(self.victories))
        place = [ 'in the center', 'in the corner', 'on the side' ]
        for x in win_logs:
            you_them = 'you' if x == PLAYER_FIRST else 'them'
            if not self.left_specific_player_first(x):
                print("  You let the kid beat you all three ways (corner, side, center) with "
                    "{} going first.".format(you_them))
                continue
            for y in win_logs[x]:
                if win_logs[x][y]:
                    print("  You managed to lose with {} going first {}.".format(
                        you_them, place[y - 1]))

    def show_board(self, this_board = None):
        if not this_board:
            this_board = self.board
        if self.show_moves:
            if len(self.moves):
                print("Moves:", mt.listnum(self.moves))
            else:
                print("Nobody has moved yet.")
        elif descriptions_not_ascii and not len(self.moves):
            print("Nobody has moved yet.")
        row_string = ''
        for y in range(0, 9):
            if descriptions_not_ascii:
                if this_board[y]:
                    print(square_placement_descriptions[y], 'is',
                        'yours' if this_board[y] == 1 else 'the kid\'s')
                continue
            raw_idx = this_board[y]
            if self.display_type == O_PLAYER:
                if raw_idx:
                    raw_idx = other_color(raw_idx)
            elif self.display_type == X_PLAYER:
                pass
            elif self.display_type == X_FIRST:
                if self.current_first == KID_FIRST:
                    raw_idx = other_color(raw_idx)
            elif self.display_type == O_FIRST:
                if self.current_first == PLAYER_FIRST:
                    raw_idx = other_color(raw_idx)
            row_string += ' ' if y in self.cell_idx else str(y)
            row_string += play_ary[raw_idx]
            if y % 3 == 2:
                print(row_string)
                row_string = ""
                if y != 8:
                    print("--+--+--")
            else:
                row_string += "|"

    def find_forking_move(self, board, to_move_color, is_also_block = True):
        '''this has to be in the game class, because it establishes a forking move'''
        ret_array = []
        blocks = find_blocking_move(board, to_move_color)
        for x in range(0, 9):
            board_temp = list(board)
            if board_temp[x]:
                continue
            board_temp[x] = to_move_color
            current_wins = find_winning_move(board_temp, to_move_color)
            if len(current_wins) >= 2:
                if (x in blocks) != is_also_block:
                    continue
                ret_array.append(x)
                self.fork_position = board_sum(board)
            d_print("fork check {} {} {} {}".format(x, ret_array, board_temp, current_wins))
        return ret_array

    def kid_pick_square(self):
        '''figures what square the kid pics, first looking for forced blocks, wins, and forks
        the last resort is data from ttt'''
        d_print("Finding move for: {}".format(board_sum(self.board)))
        if len(self.moves) == 0:
            return self.kid_start_square()
        blocking_moves = find_blocking_move(self.board, KID_COLOR)
        winning_moves = find_winning_move(self.board, KID_COLOR)
        auto_moves = find_automatic_move(self.board, KID_COLOR)
        forking_move_noblocks = self.find_forking_move(self.board, KID_COLOR, is_also_block = False)
        forking_move_blocks = self.find_forking_move(self.board, KID_COLOR, is_also_block = True)
        ranch = []
        if len(winning_moves):
            print("I think this wins!")
            ranch = list(winning_moves)
        elif len(blocking_moves):
            if len(blocking_moves) > 1:
                print("Uh oh. The kid should never be in a lost position.")
            if len(forking_move_blocks) > 0:
                print("\"I see that.\" The kid shifts and giggles slightly.")
            else:
                print("The kid nods. They see your threat.")
            ranch = list(blocking_moves)
        elif len(forking_move_blocks) > 0:
            print("\"I see that.\" The kid shifts and giggles slightly.")
            ranch = forking_move_blocks
        elif len(forking_move_noblocks) > 0:
            print("The kid shifts and giggles slightly.")
            ranch = forking_move_noblocks
        elif len(auto_moves[0]):
            if len(auto_moves[0]) > 1:
                print("OOPS! 2 auto moves in position:", mt.list_nums(auto_moves[0]))
            print("No choice, really.")
            ranch = list(auto_moves[0])
        if ranch:
            return random.choice(ranch)
        (where_to_move, my_tree_num) = check_dupe_trees(self.board)
        if my_tree_num not in tree_move_dict and my_tree_num != -1:
            sys.exit("Need my_tree_num for {}.".format(my_tree_num))
        d_print("Choosing from move branches: {}".format(my_tree_num))
        print(tree_text[my_tree_num])
        return where_to_move

    def kid_move(self):
        temp = self.kid_pick_square()
        self.place_move(temp)

    def input_text(self):
        if self.brief_question:
            return "Which square?"
        if descriptions_not_ascii:
            return "Which square? 0 is upper left, 1 is upper side, to 8 which is lower right."
        return "Which square? (0-8, 0=UL, 2=UR, 6=DL, 8=DR, ENTER for board, ? for help)"

    def player_move(self):
        while 1:
            my_move = input(self.input_text()).lower().strip()
            if my_move == '':
                self.show_board()
                continue
            m0 = my_move[0]
            if m0 == 'a':
                dump_text("about")
                continue
            if m0 == 'b':
                self.brief_question = not self.brief_question
                print("Brief text prompts are now", on_off[self.brief_question])
                continue
            if m0 == 'c':
                dump_text("credits")
                continue
            if m0 == 'd':
                self.display_type = (self.display_type + 1) % 4
                print("Changed display type:", turn_option_descriptions[self.display_type])
                continue
            if my_move in ('l', 's', 'w'):
                self.print_wins_so_far()
                continue
            if my_move == 'm':
                self.show_moves = not self.show_moves
                self.show_board()
                continue
            if m0 == 'q':
                sys.exit("Bye!")
            if m0 == 'r':
                global descriptions_not_ascii
                descriptions_not_ascii = not descriptions_not_ascii
                continue
            if m0 in ('v', '?'):
                dump_text("commands")
                continue
            if m0 in ('x', 'e'):
                dump_text("examine")
                continue
            # debug-only commands here
            if my_move == 'pa' and debug:
                self.print_all_sums()
            try:
                x = int(my_move)
            except:
                print("Unknown command {}. V or ? gives a list of commands.".format(m0.upper()))
                continue
            if x < 0 or x > len(self.board):
                print("You need something from 0 to {}.".format(len(self.board) - 1))
                continue
            if self.board[x] != 0:
                print("Something is already on square", x)
                continue
            before_moves = len(find_blocking_move(self.board, MY_COLOR))
            self.place_move(x)
            if before_moves:
                after_moves = len(find_blocking_move(self.board, MY_COLOR))
                self.played_correctly = before_moves - after_moves
            return

    def place_move(self, square):
        '''place a move, for you or the kid'''
        self.board[square] = self.current_mover
        if len(self.moves) == 0:
            self.first_square_type = locations[square]
        self.moves.append(square)
        self.cell_idx[square] = len(self.moves)
        self.show_board()

    def next_move(self):
        '''toggle who moves or, if the game is over, see who starts'''
        if self.check_game_result():
            self.clear_and_restart_game()
            return
        if self.current_mover == MY_COLOR:
            self.player_move()
        else:
            self.kid_move()
        self.current_mover = other_color(self.current_mover)

def other_color(move_color):
    if move_color == 0:
        return 0
    return MY_COLOR + KID_COLOR - move_color

def usage():
    print("USAGE: mostly debug")
    print("d/v = debug/verbose")
    print("t = test rotations, c = check needed branches, a = all rotations of a certain #")
    sys.exit()

def d_print(x):
    if debug:
        print(x)

def base_3_of(my_number):
    ary = []
    for _ in range(0, 10):
        ary.append(my_number % 3)
        my_number = my_number // 3
    ary.reverse()
    return ''.join([str(x) for x in ary])

def quick_board(board):
    row_string = ''
    for x in range(0, 9):
        row_string += play_ary[x]
        if x % 3 == 2:
            print(row_string)
            row_string = ""

def nonzeros_3(x):
    y = base_3_of(int(x))
    return y.count('0')

# Begin finding moves: while these could be in a class,
# there are times we may wish to use a different board than self.board

def find_clear_moves(board, to_move_color, look_for_win):
    this_triple = defaultdict(int)
    blanks = defaultdict(int)
    two_of_color = to_move_color if look_for_win else other_color(to_move_color)
    for w in wins:
        this_triple = [0, 0, 0]
        blank_square = NO_MOVE
        for square in w:
            if board[square]:
                this_triple[board[square]] += 1
            else:
                blank_square = square
        if this_triple[two_of_color] == 2 and blank_square != NO_MOVE:
            blanks[blank_square] += 1
    return blanks

def find_winning_move(board, to_move_color):
    return find_clear_moves(board, to_move_color, look_for_win = True)

def find_blocking_move(board, to_move_color):
    return find_clear_moves(board, to_move_color, look_for_win = False)

def find_automatic_move(board, to_move_color):
    temp = find_winning_move(board, to_move_color)
    if len(temp):
        return (temp, "win")
    temp = find_blocking_move(board, to_move_color)
    if len(temp):
        return (temp, "block")
    return ([], "do anything")

#################################end finding moves

def board_sum(board, my_rot = range(0, 9)):
    mult = 1
    my_sum = 0
    for y in range(0, 9):
        my_sum += board[my_rot[y]] * mult
        mult *= 3
    return my_sum

def board_of(a_num):
    temp = []
    for _ in range(0, 9):
        temp.append(a_num % 3)
        a_num //= 3
    return temp

def see_poss_parents(a_num):
    b = board_of(a_num)
    got_one = False
    for x in tree_move_dict:
        if x == a_num:
            continue
        can_retro = True
        c = board_of(x)
        for y in range(0, 9):
            if b[y] == c[y]:
                continue
            if c[y] == 0:
                continue
            can_retro = False
        if can_retro:
            print(x, "may be below", a_num)
            print(c, b)
            quick_board(board_of(x))
            quick_board(board_of(a_num))
            got_one = True
    if not got_one:
        print("No parents for", a_num)

def see_needed_branches(my_board, moves_so_far, depth = 1):
    #print("Top of function", my_board, "depth", depth, board_sum(my_board))
    for move_try in range(0, 9):
        if my_board[move_try] == 0:
            temp_board = list(my_board)
            temp_board[move_try] = 1
            temp_moves = list(moves_so_far)
            temp_moves.append(move_try)
            #print(move_try, "move", temp_board, board_sum(temp_board))
            skip = False
            if board_sum(my_board) not in tree_move_dict:
                for z in all_sums_from_board(my_board):
                    if board_sum(my_board) != z:
                        skip = True
            if skip:
                continue
            (a, b) = check_dupe_trees(temp_board)
            print("Tree status of", temp_board, board_sum(temp_board),
                "is", b, "from", my_board, board_sum(my_board))
            if tree_move_status[b] < 0:
                continue
            if a > -1:
                if temp_board[a]:
                    print("Uh oh overwrote position", a, "with status", b, "value", temp_board[a],
                        "on", temp_board, "from", my_board, "moves so far", moves_so_far)
                    quick_board(my_board)
                    sys.exit(tree_move_status)
                temp_board[a] = 2
                temp_moves_2 = list(temp_moves)
                temp_moves_2.append(a)
                see_needed_branches(temp_board, temp_moves_2, depth + 1)
            else:
                print("Need entry for", board_sum(temp_board))
                quick_board(my_board)
                print("Moves so far", moves_so_far)
            #print("End of", move_try, "depth=", depth)

def check_all_needed_branches():
    '''checks all branches where you start, or where opponent starts, center, side or corner'''
    see_needed_branches([0] * 9, [])
    see_needed_branches([0, 0, 0, 0, 2, 0, 0, 0, 0], [])
    see_needed_branches([2, 0, 0, 0, 0, 0, 0, 0, 0], [])
    see_needed_branches([0, 2, 0, 0, 0, 0, 0, 0, 0], [])

def inverse_matrix_of(x):
    '''picks the inverse from orientations'''
    temp = orientations.index(x)
    return orientations[inverse[temp]]

def assign_inverse_orientations():
    '''given the orientations, provides an array of which maps to which'''
    temp_inverse = [0] * 8
    for x in range(0, 8):
        ary1 = orientations[x]
        for y in range(0, 8):
            ary2 = orientations[y]
            matches = 0
            for z in range(0,9):
                if ary1[ary2[z]] == z:
                    matches += 1
            if matches == 9:
                if debug:
                    print("Inverse of", x, ary1, "is", y, ary2)
                temp_inverse[x] = y
    return temp_inverse

def rotation_index(a_sum, a_board):
    '''tells index of orientation that changes a sum to a board'''
    b2 = board_of(a_sum)
    #print(b2, a_board)
    for x in orientations:
        can_match = True
        new_ary = [b2[x[q]] for q in range(0, 9)]
        #print(b2, "goes to", new_ary, "via", x, a_board)
        for y in range(0, 9):
            if a_board[y] != new_ary[y]:
                can_match = False
        if can_match:
            return inverse_matrix_of(x)
    sys.exit("Could not rotate {} onto {}.".format(a_sum, a_board))

def check_dupe_trees(board):
    '''checks for rotation duplicates in data read from ttt.txt'''
    my_sum = 0
    #orig_sum = board_sum(board)
    for y in all_sums_from_board(board):
        if y in tree_move_dict:
            if my_sum and y != my_sum:
                print("Warning", y, "duplicates", my_sum)
            my_sum = y
    if not my_sum:
        print("Warning no directions for", board_sum(board), base_3_of(board_sum(board)))
        print("Define one of", list(all_sums_from_board(board)))
        quick_board(board)
        sys.exit()
        return (-1, -1)
    for y in all_sums_from_board(board):
        if y in tree_move_dict:
            my_ary = rotation_index(y, board)
            if tree_move_dict[my_sum] >= 0:
                return(my_ary[tree_move_dict[my_sum]], my_sum)
            return(tree_move_dict[my_sum], my_sum)
    return (tree_move_dict[my_sum], my_sum)

def verify_dict_tree(bail = False, move_to_find = 1):
    if not os.path.exists("ttt.txt"):
        sys.exit("ttt.py requires ttt.txt to read in configurations. "
            "Please check that ttt.txt is in the same folder as ttt.py before continuing.")
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                break
            if line.startswith("move=") or line.startswith("msg"):
                continue
            ary = line.split("\t")
            for q in ary[0].split(','):
                if nonzeros_3(q) % 2 != move_to_find:
                    print(q, "bad", line_count)
                    bail = True
                else:
                    print(q, "ok", nonzeros_3(q))
    if bail:
        sys.exit()

def read_game_stuff(bail = False):
    text_macro = defaultdict(str)
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                break
            if line.startswith("txtary\t"):
                ary = line.strip().split("\t")
                text_arrays[ary[1]].append(ary[2].strip().replace("\\n", "\r\n"))
                continue
            if line.startswith("msg-type"):
                ary = line.split("\t")
                win_msg[int(ary[1])][int(ary[2])] = ary[3]
                continue
            if line.startswith("move="):
                continue
            if "~" in line:
                ltil = line.strip().split("~")
                text_macro[ltil[0]] = ltil[1]
                continue
            for x in text_macro:
                if x in line:
                    line = line.replace(x, text_macro[x])
            if "\t" not in line:
                print("Need tabs at line {}.".format(line_count))
                bail = True
            ary = line.strip().split("\t")
            if len(ary) != 4:
                print("Bad # of tabs (need 3) at line {}.".format(line_count))
                bail = True
            if 1:
                ary2 = [int(x) for x in ary[0].split(",")]
                for ia2 in ary2:
                    for q in all_rotations_of_sums(ia2):
                        if q in tree_move_dict:
                            print(ia2, "duplicates earlier", q)
                            bail = True
                    tree_move_dict[ia2] = int(ary[1])
                    tree_move_status[ia2] = int(ary[2])
                    tree_text[ia2] = ary[3]
                    if debug:
                        print("Adding", ia2, "to tree.")
            if debug:
                sys.exit("Oh no! Had trouble parsing line {}: {}".format(line_count, line))
    if bail:
        sys.exit("Fix ttt before playing.")

def in_pos_file(my_board_num):
    '''see if a board number is in ttt.txt'''
    for x in all_rotations_of_sums(my_board_num):
        if x in tree_move_dict:
            return x
    return -1

def all_sums_from_board(board):
    '''all sums of a board and its eight rotations'''
    for x in range(0, 8):
        yield board_sum(board, orientations[x])

def all_rotations_of_sums(my_board_sum):
    '''all all_rotations_of_sum sums for a sum'''
    bary = []
    for _ in range(0, 9):
        bary.append(my_board_sum % 3)
        my_board_sum //= 3
    return all_sums_from_board(bary)

def is_rotated(x, y):
    '''simply checks if two board sum values are rotational equivalents'''
    return y in all_rotations_of_sums(x)

def show_all_rotations(initial_board_num):
    '''gives a detailed view of all rotated boards, given an initial board sum'''
    initial_board = board_of(initial_board_num)
    for my_orient in orientations:
        y = [0] * 9
        for i in range(0, 9):
            y[i] = initial_board[my_orient[i]]
        quick_board(y)
        print(y, board_sum(y))

def test_rotations(bail = True):
    rotations = [ 166, 174, 190, 918, 414, 6966, 3078, 8910 ]
    for r in rotations:
        b = board_of(r)
        (where_to_move, my_tree_num) = check_dupe_trees(b)
        print()
        print(r, b, where_to_move, my_tree_num)
        quick_board(b)
        print("to")
        b[where_to_move] = 2
        quick_board(b)
    if bail:
        sys.exit()

orientations = [
 [0,1,2,3,4,5,6,7,8],
 [6,3,0,7,4,1,8,5,2],
 [8,7,6,5,4,3,2,1,0],
 [2,5,8,1,4,7,0,3,6],
 [0,3,6,1,4,7,2,5,8],
 [2,1,0,5,4,3,8,7,6],
 [8,5,2,7,4,1,6,3,0],
 [6,7,8,3,4,5,0,1,2]
]

inverse = assign_inverse_orientations()

# initialization stuff

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in ('d', 'v'):
        debug = True
    elif arg == 'c':
        check_needed = True
    elif arg == 't':
        test_rotations()
    elif arg[0] == 'a':
        show_all_rotations(int(arg[1:]))
        sys.exit()
    else:
        usage()
    cmd_count += 1

read_game_stuff()

# put (other) tests below here

if check_needed:
    check_all_needed_branches()

# put tests above here

python_2_checkoffs()
my_games = GameTracker()

while 1:
    my_games.next_move()
sys.exit()
