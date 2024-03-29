'''wii.py: Walking Into It, IFComp entry for 2021
The overall idea is that you meet a kid who wants to win at tic-tac-toe
But they don't want obvious mistakes e.g. overlooking an easy block
So you must play badly ... but not too badly!
'''

# pylint: disable=too-many-branches, too-many-statements

from __future__ import print_function
import textwrap
import random
import sys
from collections import defaultdict
import os
import re
from random import choice

# local imports
import gametests
import mt
import wic
import wiaux

# for debugging only
# import traceback

data_file = "wii.txt"

tree_move_dict = defaultdict(int)
tree_move_status = defaultdict(int)
tree_text = defaultdict(int)
inverse = defaultdict(int)
cell_idx = defaultdict(int)

win_msg_from_file = defaultdict(lambda: defaultdict(str))

# these could/should be sent to a text_arrays dictionary later
text_arrays = defaultdict(list)
win_verify = defaultdict(str)

on_off = [ 'off', 'on' ]
play_ary = [ '-', 'X', 'O' ]
MY_COLOR = 1
KID_COLOR = 2

NO_MOVE = -1

# constants are listed in order of descending difficulty for the ghost
CENTER = 1
CORNER = 2
SIDE = 3

END_OF_GAME = -1
NONE_FIRST = 0
PLAYER_FIRST = 1
KID_FIRST = 2

# x-or-o differences
X_FIRST = 0
O_FIRST = 1
X_PLAYER = 2
O_PLAYER = 3
total_display_types = 4

turn_option_descriptions = [ 'X goes first', 'O goes first', 'Player is X', 'Player is O' ]
square_placement_descriptions = [
'upper left', 'upper side', 'upper right',
'left side', 'center', 'right side',
'lower left', 'lower side', 'lower right'
]

locations = [ CORNER, SIDE, CORNER, SIDE, CENTER, SIDE, CORNER, SIDE, CORNER ]
location_types = [ CORNER, SIDE, CENTER ]
colors = [ PLAYER_FIRST, KID_FIRST ]

win_triads = [ [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6] ]

debug = False
check_needed = False
descriptions_not_ascii = False
term_width = 5000

# logging variables
log_output = False
log_file = "wii-logfile.log"

#testing variables
fixed_first_move = False
fixed_index = 0

CONTINUE_PLAYING = 0
BOARD_FULL_DRAW = -1
YOU_WON = 1 # should never happen but just in case
KID_WON = 2

intro_array = []

def input_stub(my_text):
    temp = str(input(my_text))
    return temp.lower().strip()

def crude_process(my_raw):
    try:
        my_raw = my_raw.decode()
    except:
        pass
    return my_raw.lower()

def python_2_checkoffs():
    # pylint: disable=redefined-builtin,undefined-variable,global-statement
    ''' python 3 can detect terminal size. python 2 can't.
    But we need to give a default term_width to call functions.
    We make it ridiculously large, because text-wrapping isn't critical.'''
    try:
        global input
        input = raw_input
    except:
        pass

    try:
        global term_width
        term_width = os.get_terminal_size().columns
    except:
        temp = input("Since you seem to be using Python 2, "
            "I want to ask you for your preferred terminal width.\n\n"
            "This only affects text-wrapping for paragraphs of text, "
            "so you can just ignore this question if you'd like.\n\n")
        if temp.isdigit():
            term_width = int(temp)

def old_python_3_check():
    version_tuple = sys.version_info
    print("Checking version: {}.{}".format(version_tuple[0], version_tuple[1]))
    if version_tuple[0] == 3 and version_tuple[1] < 9:
        print("You may be using an old version of Python, which may cause some small odd text discrepancies.")
        print("\nYou may wish to update to 3.9 or the latest version.\n")
        print("(hit enter to continue or ctrl-c to exit and download the latest Python)")
        _find_getch()

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
        global term_width # pylint: disable=global-statement
        try:
            term_width = os.get_terminal_size().columns
        except:
            pass
    if carriage_returns & CR_BEFORE:
        print()
    text = text.replace("\\n", "\n")
    for temp in text.rstrip().split("\n"):
        if not temp:
            print()
        for x in textwrap.wrap(kludge_convert(temp), term_width):
            print(x)
    if carriage_returns & CR_AFTER:
        print()

def kludge_convert(my_string):
    '''this adds 1 to any number that has a + before it'''
    new_line = re.sub(r'\+([0-9]+)',
        lambda x: str(int(x.group(1))+my_games.starting_number), my_string)
    return new_line.replace("$KID", kids_name)

def my_text_wrap_array(text_array, carriage_returns = CR_AFTER, extra_carriage_return = False):
    '''wraps an array of text strings, with carriage returns as specified'''
    if carriage_returns == CR_AFTER and extra_carriage_return:
        print()
    for line in text_array:
        line_mod = line
        if '+' in line or '$' in line:
            line_mod = kludge_convert(line)
        my_text_wrap(line_mod, carriage_returns)
    if carriage_returns == CR_BEFORE and extra_carriage_return:
        print()

def log_cr():
    '''cheap stub to decide whether to output a string'''
    return "\n" if log_output else ""

def show_introductory_text():
    '''this gets basic options from the player, allowing you to skip the full introduction'''
    if os.path.exists("debug-skip-intro.txt"):
        if os.stat("debug-skip-intro.txt").st_size:
            print("debug-skip-intro.txt exists and is not blank, so I am skipping the intro. "
            "This is probably just for testing.")
            return
        print("debug-skip-intro.txt exists, but it is blank, so I am not skipping the intro.")
    count = 0
    print("First, this game can give short descriptions instead of displaying minimal ASCII art.",
        "The ASCII art may cause problems for screen readers.")
    global descriptions_not_ascii # pylint: disable=global-statement
    while 1:
        print("Would you prefer descriptions instead of ASCII art",
            "(F forces descriptions for screen readers)? Y/N/F")
        raw = _find_getch()
        if raw == b'\xe0':
            _find_getch() # Can this semi-duplicated code be pulled into a _find_getch_extended?
        raw = crude_process(raw)
        if raw == 'y':
            descriptions_not_ascii = True
        elif raw == 'f':
            descriptions_not_ascii = 2
        elif raw == 'n':
            descriptions_not_ascii = False
        else:
            continue
        break
    print("Note this setting isn't fixed. It can be toggled by typing R.")
    my_text_wrap("If you've read the introduction before, you can "
        "(S)how the remaining introductory text without pauses ({} chunks left) or "
        "(F)ast-forward to ignore the remaining text. "
        "You can also push any key to read the next bit, starting now.".format(
            len(text_arrays["intro"])), carriage_returns = CR_NONE)
    wait_for_pause = True
    while count < len(text_arrays["intro"]):
        if wait_for_pause:
            raw = _find_getch()
            if raw == b'\xe0':
                _find_getch()
                continue
            if raw == b'\x03':
                print("Bailing.")
                sys.exit()
            raw = crude_process(raw)
            if raw == 's':
                wait_for_pause = False
            elif raw == 'f':
                print("  (Skipping the rest of your conversation with {}...)".format(kids_name))
                return
        my_text_wrap(text_arrays["intro"][count])
        count += 1
    if not wait_for_pause:
        print()

def dump_text(my_idx, resize = True):
    '''given an array of text read from wii.txt, we print it out with appropriate line spacing'''
    if resize:
        global term_width # pylint: disable=global-statement
        try:
            term_width = os.get_terminal_size().columns
        except:
            pass
    my_text_wrap_array(text_arrays[my_idx])

class GameTracker:
    '''this is the main class that keeps track of how the kid won'''
    # pylint: disable=too-many-instance-attributes
    my_move = PLAYER_FIRST
    board = []
    moves = []
    cell_idx = defaultdict(int)
    win_logs = defaultdict(lambda: defaultdict(list))
    win_msg = defaultdict(lambda: defaultdict(str))
    blocks_this_game = 0
    victories = 0
    fork_position = 0
    played_correctly = 0
    current_mover = current_first = NONE_FIRST
    first_square_type = 0
    show_moves = False
    display_type = X_FIRST
    brief_question = False
    show_numbers = True
    grid_display = True
    starting_number = 1
    quit_in_a_row = 0
    textcolors = [wic.texts[1], wic.texts[1], wic.texts[1], wic.sidewalks[0]]

    def __init__(self, complete_restart = True):
        self.init_wins()
        self.win_msg = win_msg_from_file
        if complete_restart:
            show_introductory_text()
        self.victories = 0
        self.clear_and_restart_game()

    def init_wins(self):
        '''make sure we have tracked all possible win states'''
        for x in location_types:
            for y in colors:
                self.win_logs[y][x] = []

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
            sys.exit("Hooray! {} is happy to have beaten you in all possible ways. This should not be shown, but it is.".format(kids_name))
        if not need_kid_first:
            print("Since {} has won starting in the corner, center and sides, you go first.".format(kids_name))
            return PLAYER_FIRST
        if not need_you_first:
            print("Since {} has won all three ways with you first, {} starts.".format(kids_name, kids_name))
            return KID_FIRST
        while 1:
            if not self.current_first:
                who_now = ''
            else:
                who_now = ", (enter) = keep going " + \
                    ('first' if self.current_first == 1 else 'second')
            input_str = "A new game. Who moves first? 1 = you, 2 = {}{}.{}".format(kids_name, who_now, log_cr())
            who_moves = input_stub(input_str)
            if not who_moves:
                if self.current_first:
                    return self.current_first
                continue
            if who_moves[0] == '1':
                return PLAYER_FIRST
            if who_moves[0] == '2':
                return KID_FIRST

    def kid_start_square(self):
        '''pick a square the kid can start on that might help you lose a different sort of game'''
        picks_list = [x for x in self.win_logs[KID_FIRST] if not self.win_logs[KID_FIRST][x]]
        self.first_square_type = random.choice(picks_list)
        try:
            if fixed_first_move and self.first_square_type != CENTER:
                temp = 0
                for x in range(0, 9):
                    if locations[x] == self.first_square_type and temp == fixed_index:
                        return x
                    temp += 1
                print("WARNING: bad randomizer to find the fixed first move. This should never happen.")
            return random.choice([x for x in range(0,9) if locations[x] == self.first_square_type])
        except:
            print("Uh-oh, I couldn't find a way for {} to get started.".format(kids_name))
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
            print("Somehow, you won, but you should not have: let me know the moves.", self.moves)
            return True
        if game_result == BOARD_FULL_DRAW:
            print("It's a stalemate. Time to start over and play again.")
            return True
        print("{} won!".format(kids_name))
        if not self.played_correctly:
            print('But {} looks {} unhappy. "No fair! Too easy! I\'m not a baby!"'.format(
                kids_name, 'really' if self.fork_position else 'slightly'))
            return True
        if self.win_logs[self.current_first][self.first_square_type]:
            if self.current_first == MY_COLOR:
                my_text_wrap(win_verify["first-already-second"])
            else:
                my_text_wrap(win_verify["first-already-first"])
            unfound_rotation = False
            for x in self.win_logs[self.current_first][self.first_square_type]:
                if not is_rotated(x, self.fork_position):
                    unfound_rotation = True
            if unfound_rotation:
                if debug:
                    d_print("DEBUG MESSAGE: You found an alternate solution that"
                        "will go into the list for this game-start.")
                self.win_logs[self.current_first][self.first_square_type].append(self.fork_position)
            return True
        for x in self.win_logs[self.current_first]:
            for y in self.win_logs[self.current_first][x]:
                if not is_rotated(y, self.fork_position):
                    continue
                if y == self.fork_position:
                    my_text_wrap(win_verify["exact-position-before"])
                else:
                    my_text_wrap(win_verify["rotation-before"])
                if self.current_first == PLAYER_FIRST and self.first_square_type == CORNER and \
                    x == SIDE and not self.win_logs[self.current_first][CORNER]:
                    # This is hard coded. We can generalize, but that'd require extra testing.
                    if len(self.win_logs[PLAYER_FIRST][SIDE]) > 1:
                        my_text_wrap(win_verify["shift-one-side-win"])
                    else:
                        my_text_wrap(win_verify["shift-side-to-corner"])
                    self.win_logs[PLAYER_FIRST][CORNER].append(self.fork_position)
                    self.win_logs[PLAYER_FIRST][SIDE].remove(y)
                return True
        my_text_wrap(self.win_msg[self.current_first][self.first_square_type])
        self.win_logs[self.current_first][self.first_square_type].append(self.fork_position)
        my_text_wrap(text_arrays["win_progress"][self.victories] + "\n")
        self.victories += 1
        if self.victories == len(text_arrays["win_progress"]):
            temp = self.conditional_log_bail(False)
            if temp == END_OF_GAME:
                global my_games
                my_games = GameTracker(complete_restart = False)
        return True

    def print_all_sums(self):
        '''print sum and all rotated sums'''
        for this_sum in all_sums_from_board(self.board):
            print(this_sum)

    def left_specific_player_first(self, this_player):
        '''this determines whether there are any losses to achieve with this_player first'''
        for x in self.win_logs[this_player]:
            if not self.win_logs[this_player][x]:
                return True
        return False

    def print_wins_so_far(self):
        '''prints all valid wins so far, with special formatting
        if you did nothing meaningful yet or, or cleared X-goes-first'''
        if not self.victories:
            print("{} hasn't notched any impressive wins yet. Keep trying. You'll lose right!".format(kids_name))
            return
        print("So far, you have let {} win {} unique ways, total.".format(kids_name, self.victories))
        place = [ 'in the center', 'in the corner', 'on the side' ]
        for x in self.win_logs:
            you_them = 'you' if x == PLAYER_FIRST else kids_name
            if not self.left_specific_player_first(x):
                print("  You've lost to {} all three ways (corner, side, center)".format(kids_name),
                    "with {} going first.".format(you_them))
                continue
            for y in self.win_logs[x]:
                if self.win_logs[x][y]:
                    print("  You managed to lose with {} going first {}.".format(
                        you_them, place[y - 1]))

    def describe_squares(self, who_moves):
        player_string = 'You' if who_moves == MY_COLOR else kids_name
        temp_ary = [square_placement_descriptions[x] for x in range(0, 9) if self.board[x] == who_moves]
        if len(temp_ary) == 0:
            print("No squares for {}.".format(player_string))
        else:
            print("{} took {}.".format(player_string, ', '.join(temp_ary)))

    def show_board(self, this_board = None):
        '''simply shows the board based on the display options you have set'''
        if not this_board:
            this_board = self.board
        if self.show_moves:
            if len(self.moves) > 0:
                print("Moves:", mt.list_nums(self.moves))
            else:
                print("Nobody has moved yet.")
        elif descriptions_not_ascii:
            if len(self.moves) == 0:
                print("Nobody has moved yet.")
            else:
                self.describe_squares(1)
                self.describe_squares(2)
            return
        row_string = ''
        for y in range(0, 9):
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
            if self.show_numbers:
                row_string += self.textcolors[0] + (' ' if y in self.cell_idx else str(y + self.starting_number))
            row_string += self.textcolors[raw_idx] + play_ary[raw_idx]
            if y % 3 == 2:
                print(self.textcolors[3] + row_string + wic.RESET_ALL)
                row_string = ""
                if self.grid_display and y != 8:
                    print(self.textcolors[3] + self.textcolors[0] + ("--+--+--" if self.show_numbers else "-+-+-") + wic.RESET_ALL)
            else:
                row_string += self.textcolors[0] + '|' if self.grid_display else ' '

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
        the last resort is data from wii'''
        d_print("Finding move for: {}".format(board_sum(self.board)))
        if len(self.moves) == 0:
            return self.kid_start_square()
        blocking_moves = find_blocking_move(self.board, KID_COLOR)
        winning_moves = find_winning_move(self.board, KID_COLOR)
        forking_move_noblocks = self.find_forking_move(self.board, KID_COLOR, is_also_block = False)
        forking_move_blocks = self.find_forking_move(self.board, KID_COLOR, is_also_block = True)
        ranch = []
        if len(winning_moves):
            print(kludge_convert(text_arrays["winning_move_act"][self.victories]))
            ranch = list(winning_moves)
        elif len(blocking_moves):
            if len(blocking_moves) > 1:
                print("Uh oh. {} should never be in a lost position.".format(kids_name))
            if len(forking_move_blocks) > 0:
                print("\"I see that.\" {} shifts and giggles slightly.".format(kids_name))
            else:
                print("{} nods, seeing your threat.".format(kids_name))
            ranch = list(blocking_moves)
        elif len(forking_move_blocks) > 0:
            print("\"I see that.\" {} shifts and giggles slightly.".format(kids_name))
            ranch = forking_move_blocks
        elif len(forking_move_noblocks) > 0:
            print("{}'s eyes grow wide for a second or two.".format(kids_name))
            ranch = forking_move_noblocks
        if ranch:
            return random.choice(ranch)
        (where_to_move, my_tree_num) = check_dupe_trees(self.board)
        if my_tree_num not in tree_move_dict and my_tree_num != -1:
            sys.exit("Need my_tree_num for {}.".format(my_tree_num))
        d_print("Choosing from move branches: {}".format(my_tree_num))
        print(tree_text[my_tree_num])
        return where_to_move

    def kid_move(self): # pylint: disable=missing-function-docstring
        temp = self.kid_pick_square()
        self.place_move(temp)

    def input_text(self):
        '''tells what the text prompt should be'''
        if self.brief_question:
            return "Which square?"
        if descriptions_not_ascii:
            return "Which square? {} is upper left, {} is upper side, to {} which is lower right.".\
                format(self.starting_number, 1 + self.starting_number, 8 + self.starting_number)
        return "Which square? ({}-{}, {}=UL, {}=UR, {}=DL, {}=DR, ENTER for board, ? for help)".\
            format(self.starting_number, 8 + self.starting_number, self.starting_number,
                   2 + self.starting_number, 6 + self.starting_number, 8 + self.starting_number)

    def player_move(self):
        '''this is the main engine that sees how the player is trying to move'''
        global descriptions_not_ascii # pylint: disable=global-statement
        while 1:
            my_move = input_stub(self.input_text() + log_cr())
            if log_output:
                print("<LOGGING PURPOSES ONLY> YOUR COMMAND = {}".format(my_move))
            if my_move == '':
                self.show_board()
                continue
            m0 = my_move[0] # pylint:disable=invalid-name
            mx = my_move[1:] if len(my_move) > 1 else '' # pylint:disable=invalid-name
            if m0 == 'q':
                self.quit_in_a_row += 1
                if my_move != 'quit' and self.quit_in_a_row == 1:
                    print("To make sure you don't quit accidentally, I'll request a full QUIT, or another q.")
                    continue
                self.conditional_log_bail(True)
            self.quit_in_a_row = 0
            if m0 == 'a':
                dump_text("about")
                continue
            if m0 == 'b':
                self.brief_question = not self.brief_question
                print("Brief text prompts are now", on_off[self.brief_question])
                continue
            if re.search('^c[0-9]+$', my_move):
                if descriptions_not_ascii == 2:
                    print("Text color is turned off for screen readers.")
                    continue
                if len(my_move) > 5:
                    print("You can only define 4 color numbers.")
                    continue
                temp_colors = [int(x) for x in my_move[1:]]
                temp_background = temp_colors[3] if len(temp_colors) == 4 else wic.sidewalks.index(self.textcolors[3])
                if temp_colors[:3].count(temp_background) > 0:
                    print("None of the X's, O's and lines can be the same color as the sidewalk. Fix digit {}.".format(temp_colors.index(temp_background)))
                    continue
                for x in range(0, len(temp_colors)):
                    if x == 3:
                        self.textcolors[x] = wic.sidewalks[temp_colors[x]]
                    else:
                        self.textcolors[x] = wic.texts[temp_colors[x]]
                if len(self.moves) == 0:
                    print("New colors will show up once a move is made. c1110 resets to default.")
                else:
                    print("Changing colors.")
                    self.show_board()
                continue
            if m0 == 'c':
                dump_text("credits")
                continue
            if m0 == 'd':
                if mx == '':
                    self.display_type = (self.display_type + 1) % total_display_types
                elif mx.isdigit():
                    if int(mx) > total_display_types or int(mx) < 1:
                        print("You need to change to display type 1 through {}.".format(
                            total_display_types))
                        continue
                    self.display_type = int(mx) - 1
                else:
                    print("The display type argument can be blank (cycling) or 1-{}.".format(
                        total_display_types))
                    continue
                print("Changed display type:", turn_option_descriptions[self.display_type])
                continue
            if m0 in ('l', 's', 'w'):
                self.print_wins_so_far()
                continue
            if m0 == 'g':
                self.grid_display = not self.grid_display
                print("Grid is now", on_off[self.grid_display])
                continue
            if m0 in ('h', 'm'):
                self.show_moves = not self.show_moves
                self.show_board()
                continue
            if m0 == 'i':
                dump_text('meta')
                continue
            if m0 == 'n':
                self.show_numbers = not self.show_numbers
                print("Showing numbers is now", on_off[self.show_numbers])
                continue
            if m0 == 'o':
                print("The board {} starts at one in the upper-left.".format(
                    'already' if self.starting_number == 1 else 'now'))
                print("Z changes the board back to zero in the upper left.")
                self.starting_number = 1
                self.show_board()
                continue
            if m0 == 'r':
                if descriptions_not_ascii == 2:
                    print("Text descriptions are locked in.",
                        "You'll need to restart if you wish to toggle to ASCII.")
                    continue
                descriptions_not_ascii = not descriptions_not_ascii
                print("Descriptions instead of ASCII art are now {}.". \
                    format(mt.on_off(descriptions_not_ascii)))
                continue
            if m0 == 't':
                dump_text('options')
                continue
            if m0 == '?':
                dump_text("basichelp")
                continue
            if my_move == 'xyzzy':
                self.xyzzy()
                continue
            if m0 in ('x', 'e'):
                dump_text("examine")
                continue
            if m0 == 'z':
                print("The board {} starts at zero in the upper-left.".format(
                    'already' if self.starting_number == 0 else 'now'))
                print("O changes the board back to one in the upper left.")
                self.starting_number = 0
                self.show_board()
                continue
            if m0 == '#':
                self.starting_number = 1 - self.starting_number
                print("The board now starts at {} in the upper-left.".format(
                    ['zero', 'one'][self.starting_number]))
                self.show_board()
            # debug-only commands here
            if my_move == 'pa' and debug:
                self.print_all_sums()
            try:
                x = int(my_move)
            except:
                print("Unknown command {}. Type ? to see a list.".format(m0.upper()))
                continue
            x -= self.starting_number
            if x < 0 or x >= len(self.board):
                print("You need a number from from {} to {}.".format(
                    self.starting_number, 8 + self.starting_number))
                continue
            if self.board[x] != 0:
                print("Something is already on square {}.".format(x + self.starting_number))
                continue
            before_moves = len(find_blocking_move(self.board, MY_COLOR))
            self.place_move(x)
            if before_moves:
                after_moves = len(find_blocking_move(self.board, MY_COLOR))
                self.played_correctly = before_moves - after_moves
            return

    def conditional_log_bail(self, force_bail):
        print(kludge_convert(text_arrays["quitmsg"][self.victories]))
        if log_output:
            print("\n\nThanks for logging your play-through! The file is at {}.".format(log_file))
        if force_bail == False:
            got_xyzzy = os.path.exists('wai.py')
            print("You've completed the game, and there are no huge hidden secrets{}.".format('' if got_xyzzy else ', though typing XYZZY at any time would open a different sort of Tic-Tac-Toe'))
            while(1):
                x = input("(R)ESTART{} or (Q)UIT?".format(', XYZZY for a post-comp sequel, ' if got_xyzzy else '')).strip().lower()
                if x == 'r' or x == 'restart':
                    return END_OF_GAME
                if x == 'q' or x == 'quit' or x == '':
                    break
        else:
            input("Press <ENTER> to exit the game. Note this will close the terminal if you double-clicked on the wii.py file.")
        sys.exit()

    def place_move(self, square):
        '''place a move, for you or the kid'''
        self.board[square] = self.current_mover
        if len(self.moves) == 0:
            self.first_square_type = locations[square]
        self.moves.append(square)
        self.cell_idx[square] = len(self.moves)
        if descriptions_not_ascii and self.current_mover == KID_COLOR:
            print("{} takes the {}.".format(kids_name, square_placement_descriptions[square]))
            print("Here is the new board status:")
        if descriptions_not_ascii and len(self.moves) != 9 and self.current_mover == MY_COLOR:
            return
        self.show_board()

    def xyzzy(self):
        if os.path.exists("wai.py") or os.path.exists("reasoning.txt"):
            print("You already considered a 3-d version of Tic-Tac-Toe and created wai.py and reasoning.txt. If either is somehow corrupted, erase both and try again.")
            return
        wiaux.rot13_process(wiaux.rot13_string_convert("wai.py"))
        wiaux.rot13_process(wiaux.rot13_string_convert("reasoning.txt"))

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
        return self.current_mover

def other_color(move_color): # pylint: disable=missing-function-docstring
    return (MY_COLOR + KID_COLOR - move_color) if move_color else 0

def usage(): # pylint: disable=missing-function-docstring
    my_text_wrap_array(text_arrays["usage"], carriage_returns = CR_NONE)
    sys.exit()

def d_print(x): # pylint: disable=missing-function-docstring
    if debug:
        print(x)

def base_3_of(my_number):
    '''renders a number into a base 3 array'''
    ary = []
    for _ in range(0, 9):
        ary.append(my_number % 3)
        my_number = my_number // 3
    ary.reverse()
    return ''.join([str(x) for x in ary])

def quick_board(board):
    '''very quick board, no boundaries or numbers'''
    row_string = ''
    for x in range(0, 9):
        row_string += board[play_ary[x]]
        if x % 3 == 2:
            print(row_string)
            row_string = ""

def nonzeros_3(x):
    ''' counts number of blank squares in a board, or sum'''
    return base_3_of(int(x)).count('0')

# Begin finding moves: while these could be in a class,
# there are times we may wish to use a different board than self.board

def find_clear_moves(board, to_move_color, look_for_win):
    '''returns an array of sensible moves to achieve a win/avoid a loss'''
    this_triple = defaultdict(int)
    blanks = defaultdict(int)
    two_of_color = to_move_color if look_for_win else other_color(to_move_color)
    for my_win_triad in win_triads:
        this_triple = [0, 0, 0]
        blank_square = NO_MOVE
        for square in my_win_triad:
            if board[square]:
                this_triple[board[square]] += 1
            else:
                blank_square = square
        if this_triple[two_of_color] == 2 and blank_square != NO_MOVE:
            blanks[blank_square] += 1
    return blanks

def find_winning_move(board, to_move_color): # pylint: disable=missing-function-docstring
    return find_clear_moves(board, to_move_color, look_for_win = True)

def find_blocking_move(board, to_move_color): # pylint: disable=missing-function-docstring
    return find_clear_moves(board, to_move_color, look_for_win = False)

#################################end finding moves

def board_sum(board, my_rot = range(0, 9)):
    ''' convert board array to number, base 3 '''
    mult = 1
    my_sum = 0
    for y in range(0, 9):
        my_sum += board[my_rot[y]] * mult
        mult *= 3
    return my_sum

def board_of(a_num):
    ''' convert number to board, base 3 '''
    temp = []
    for _ in range(0, 9):
        temp.append(a_num % 3)
        a_num //= 3
    return temp

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
    sum_board = board_of(a_sum)
    #print(sum_board, a_board)
    for x in orientations:
        can_match = True
        new_ary = [sum_board[x[y]] for y in range(0, 9)]
        #print(sum_board, "goes to", new_ary, "via", x, a_board)
        for y in range(0, 9):
            if a_board[y] != new_ary[y]:
                can_match = False
        if can_match:
            return inverse_matrix_of(x)
    sys.exit("Could not rotate {} onto {}.".format(a_sum, a_board))

def check_dupe_trees(board):
    '''checks for rotation duplicates in data read from wii.txt'''
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

def read_game_stuff(bail = False):
    '''this reads in kid move data and game text from wii.txt'''
    text_macro = defaultdict(str)
    global kids_name
    with open(data_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                break
            if line.startswith("names"):
                name_array = re.sub("^.*\t", "", line.strip()).split(',')
                kids_name = choice(name_array)
                continue
            if line.startswith("txtary\t"):
                ary = line.strip().split("\t")
                text_arrays[ary[1]].append(ary[2].strip().replace("\\n", "\r\n"))
                continue
            if line.startswith("winver\t"):
                ary = line.strip().split("\t")
                win_verify[ary[1]] = ary[2].strip().replace("\\n", "\r\n")
                continue
            if line.startswith("msg-type"):
                ary = line.split("\t")
                win_msg_from_file[int(ary[1])][int(ary[2])] = ary[3]
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
            try:
                ary2 = [int(x) for x in ary[0].split(",")]
            except:
                print("Uh oh. Bad line in {} {} {}".format(data_file, line_count, line.strip()))
            for ia2 in ary2:
                for x in all_rotations_of_sums(ia2):
                    if x in tree_move_dict:
                        print(ia2, "duplicates earlier", x)
                        bail = True
                tree_move_dict[ia2] = int(ary[1])
                tree_move_status[ia2] = int(ary[2])
                tree_text[ia2] = ary[3]
                if debug:
                    print("Adding", ia2, "to tree.")
            if debug:
                sys.exit("Oh no! Had trouble parsing line {}: {}".format(line_count, line))
    if bail:
        sys.exit("Fix {} before playing.".format(data_file))

def in_pos_file(my_board_num):
    '''see if a board number is in wii.txt'''
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
    return all_sums_from_board(board_of(my_board_sum))

def is_rotated(x, y):
    '''simply checks if two board sum values are rotational equivalents'''
    return y in all_rotations_of_sums(x)

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
old_python_3_check()
read_game_stuff()
cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in ('d', 'v'):
        debug = True
    elif arg == 'c':
        check_needed = True
    elif arg == 't':
        gametests.test_rotations()
    elif arg == 'l':
        log_output = True
    elif arg[:3] == 'fix':
        fixed_first_move = True
        try:
            temp = int(arg[3:])
            if fixed_index > 3 or fixed_index < 0:
                print("The fixed index for starting with corner or edge squares must be from 0 to 3.")
            else:
                fixed_index = temp
        except:
            pass
    elif arg[:2] == 'l=':
        log_output = True
        log_file = arg[2:]
    elif arg[0] == 'a':
        gametests.show_all_rotations(int(arg[1:]))
        sys.exit()
    else:
        usage()
    cmd_count += 1

if log_output:
    try:
        f = open(log_file, "a") # pylint: disable=consider-using-with
        f.close()
        print("Note: carriage returns will appear after each user input prompt to flush STDOUT "+ \
            "so the actual question appears. This shouldn't happen in non-logging mode.")
        sys.stdout = mt.Logger(log_file)
        print("Output will go to log file {}.".format(log_file))
    except:
        print("* " * 50)
        print("Could not open log file candidate {}. ".format(log_file) +
            "Logging disabled. Please check to make sure it is a valid path and not a directory.")
        log_output = False

# put (other) tests below here

if check_needed:
    gametests.check_all_needed_branches()

# put tests above here

python_2_checkoffs()

while 1:
    my_games = GameTracker()

    print(1)
    while my_games.next_move() != END_OF_GAME:
        pass
    print(2)
