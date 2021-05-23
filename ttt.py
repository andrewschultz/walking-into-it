#
#
# tic tac toe python game
#
# where you meet a kid who wants to beat you, but not after you make obvious dumb mistakes
#

import textwrap
import random
import sys
import mytools as mt
from collections import defaultdict
import os

term_width = os.get_terminal_size().columns

tree_move_dict = defaultdict(int)
tree_move_status = defaultdict(int)
tree_text = defaultdict(int)
inverse = defaultdict(int)
cell_idx = defaultdict(int)

win_logs = defaultdict(lambda: defaultdict(bool))
win_msg = defaultdict(lambda: defaultdict(str))
wins_in_order = []

victories = 0

play_ary = ['-', 'X', 'O']
my_color = 1
kid_color = 2

NO_MOVE = -1

# constants are listed in order of descending difficulty for the ghost
CENTER = 1
CORNER = 2
SIDE = 3

NONE_FIRST = 0
PLAYER_FIRST = 1
KID_FIRST = 2

initial_mover = NONE_FIRST
first_square_type = -1

# x-or-o differences
X_FIRST = 0
O_FIRST = 1
X_PLAYER = 2
O_PLAYER = 3

display_descriptions = [ 'X goes first', 'O goes first', 'Player is X', 'Player is O' ]

display_type = X_FIRST

locations = [ CORNER, SIDE, CORNER, SIDE, CENTER, SIDE, CORNER, SIDE, CORNER ]
location_types = [ CORNER, SIDE, CENTER ]
colors = [ PLAYER_FIRST, KID_FIRST ]

wins = [ [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6] ]

first_mover = -2

debug = False

show_moves = False
check_needed = False
played_correctly = True

CONTINUE_PLAYING = 0
BOARD_FULL_DRAW = -1
you_won = 1 # should never happen but just in case
kid_won = 2

blocks_this_game = 0
fork_position = 0
won_forks = []

intro_array = []

# thanks to https://stackoverflow.com/a/21659588/6395052
def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch()

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
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
    if refresh_terminal_size:
        global term_width
        term_width = os.get_terminal_size().columns
    if carriage_returns & CR_BEFORE: print()
    for x in textwrap.wrap(text, term_width):
        print(x)
    if carriage_returns & CR_AFTER: print()

def show_introductory_text():
    count = 0
    my_text_wrap("If you've read the introduction before, you can (S)how the remaining introductory text without pauses ({} chunks left) (F)ast-forward to ignore the remaining text. You can also push any key to read the next bit, starting now.".format(len(intro_array)), carriage_returns = CR_NONE)
    wait_for_pause = True
    while count < len(intro_array):
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
        my_text_wrap(intro_array[count])
        count += 1
    if not wait_for_pause:
        print()

def about():
    my_text_wrap("This was originally intended to be a 4-hour EctoComp game in 2019, but the scope was much too big. Plus I thought it was too abstract. Why bother?")
    my_text_wrap("But games like Sandcastle Master, where an adult humors a kid, so a kid has a fun time, stuck in my mind. I thought it might be nice to try.")
    my_text_wrap("And some of my favorite memories of being taught are people who helped me feel smarter than them, though looking back, I realize how clever they were to frame things as they did.")
    my_text_wrap("Also, as a chess player, I remember my fear of how bore draws might take the game over. Sometimes it felt like 'best play' might ruin chess. It ruined tic-tac-toe...or did it? I enjoyed the what-if meta-games.")
    my_text_wrap("I initially went ahead with to make sure I kept my IFComp streak alive at 11. My other game had had roadblocks, and I was happy with this once I made it about more than some silly abstract kids' game.")
    my_text_wrap("Along the way, I managed to learn about AI and minimax and that sort of thing, and I originally wrote the game without classes. So I rewrote it with classes and learned a lot.")
    my_text_wrap("So I think the game stands well on its own, if it's not especially big. Maybe you will even welcome the game as an efficient way to have fun, and if you're playing this during IFComp, hopefully it will boost you to try others.")
    my_text_wrap("My email is blurglecruncheon@gmail.com if you want to contact me about bugs, features, etc.")

def credits():
    my_text_wrap("Thanks to my testers: <nobody yet>.")
    my_text_wrap("Thanks to Clederson Cruz for the tic tac toe minimax code: https://github.com/Cledersonbc/tic-tac-toe-minimax/issues")
    my_text_wrap("Thanks to stackoverflow for helping me with so much cool coding stuff, enough so I would be confident writing a Python text adventure.")
    my_text_wrap("Thanks to people on various discord servers for general game talk: PunyInform, Adventuron, and the 6502 workshop. It helped when I was stuck with things.")
    my_text_wrap("And thanks to everyone who's been even moderately successful with a homebrew IFComp entry. It all gave me the confidence to try a project in something other than Inform or Twine.")

def show_possible_commands():
    my_text_wrap("You will usually just want to type a number from 0 to 8 inclusive, to make a move.")
    my_text_wrap("However, there are meta-commands. They only need one letter. A is a general ABOUT, and C is CREDITS.")
    my_text_wrap("You can also type D0, D1, D2, or D3 to change the display 0=you are X, 1=the kid is X, 2=X goes first, 3=X goes second.")
    my_text_wrap("M toggles whether or not you see the moves above the board.")
    my_text_wrap("L or W or S (Losses, Wins, Scores) tracks your losses, the kid's losses or the kid's wins.")
    my_text_wrap("V views possible commands.")

class game:
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

    def __init__(self):
        self.init_wins()
        self.win_msg = win_msg
        show_introductory_text()
        self.clear_and_restart_game()

    def init_wins(self):
        for x in location_types:
            for y in colors:
                self.win_logs[y][x] = False

    def clear_and_restart_game(self):
        global board
        global moves
        global blocks_this_game
        self.board = [0] * 9
        self.moves = []
        self.cell_idx.clear()
        self.blocks_this_game = 0
        self.current_first = self.current_mover = self.choose_sides()
        if self.current_first == my_color:
            self.show_board()

    def choose_sides(self):
        need_you_first = self.left_specific_player_first(PLAYER_FIRST)
        need_kid_first = self.left_specific_player_first(KID_FIRST)
        if not need_kid_first and not need_you_first:
            sys.exit("Hooray! The kid is happy to have beaten you in all possible ways. This should not be shown, but it is.")
        if not need_kid_first:
            print("Since the kid has won starting in the corner, center and sides, you go first.")
            return PLAYER_FIRST
        if not need_you_first:
            print("Since you've won all three ways with you first, the kid starts.")
            return KID_FIRST
        while 1:
            who_moves = input("A new game. Who moves first? 1 = you, 2 = the kid{}.".format(", (enter) = keep going {}".format('first' if self.current_mover == 1 else 'second') if self.current_mover != 0 else '')).lower().strip()
            if not who_moves:
                if self.current_mover:
                    return self.current_mover
                continue
            if who_moves[0] == '1':
                return PLAYER_FIRST
                break
            if who_moves[0] == '2':
                return KID_FIRST

    def kid_start_square(self):
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

    def check_board(self, board = None):
        if board == None:
            board = self.board
        if board[2] and board[2] == board[4] == board[6]:
            d_print("Diagonal match UL/DR.")
            return board[2]
        if board[0] and board[0] == board[4] == board[8]:
            d_print("Diagonal match UR/DL.")
            return board[0]
        for x in range(0, 3):
            if board[3*x] and board[3*x] == board[3*x+1] == board[3*x+2]:
                d_print("Horizontal match: row {}".format(x))
                return board[3*x]
            if board[x] and board[x] == board[x+3] == board[x+6]:
                d_print("Vertical match: row {}".format(x))
                return board[x]
        for x in range(0, 9):
            if not board[x]:
                return CONTINUE_PLAYING
        return BOARD_FULL_DRAW

    def check_game_end(self):
        game_result = self.check_board(self.board)
        if game_result == CONTINUE_PLAYING:
            return False
        if game_result == my_color:
            print("Somehow, you won, but you should not have.")
            return True
        if game_result == BOARD_FULL_DRAW:
            print("It's a stalemate. You need to play again.")
            return True
        print("The kid won!")
        if not self.played_correctly:
            print("But they don't look happy. \"No fair! I'm not a baby! You made it too easy.\"")
            return True
        if self.win_logs[self.current_first][self.first_square_type] == True:
            print("But sadly, they don't look that happy. They already beat you that way!")
            return True
        for x in self.won_forks:
            if x == self.fork_position:
                print("You're a bit surprised when the kid proclaims they already won from this exact position, so it really shouldn't count.")
                return True
            if is_rotated(x, self.fork_position):
                print("You're a bit surprised when the kid starts mentioning how this win LOOKED sort of like another one, so they're not sure if it should count. You undo the last couple moves and rotate and flip the board in your head, and yeah, you have to agree.")
                return True
        print(self.win_msg[self.current_first][self.first_square_type])
        self.win_logs[self.current_first][self.first_square_type] = True
        print(wins_in_order[self.victories])
        print()
        self.victories += 1
        if self.victories == len(wins_in_order):
            sys.exit()
        return True


    def find_calculated_move(board, kid_color):
        blocking_moves = find_blocking_move(board, kid_color)
        winning_moves = find_winning_move(board, kid_color)
        auto_moves = find_automatic_move(board, kid_color)
        forking_move = find_forking_move(board, kid_color, remove_blocks = False)
        forking_move_block = find_forking_move(board, kid_color)
        if len(winning_moves):
            return(random.choice(list(winning_moves)), "I think this wins!", "<KID WINS>")
        if len(forking_move):
            self.fork_position = board_sum(board)
            if not len(blocking_moves):
                return(random.choice(forking_move), "The kid shifts and giggles slightly.", "<KID SEES A FORK>")
            return(random.choice(forking_move_block), "\"I see that.\" The kid shifts and giggles slightly.", "<KID SEES A FORK>")
        if len(auto_moves[0]):
            if len(auto_moves[0]) > 1:
                print("OOPS! 2 auto moves in position:", mt.listnum(auto_moves[0]))
            return(random.choice(list(auto_moves[0])), '"No choice, really."', "<ONLY ONE OBVIOUS MOVE>")
        return(NO_MOVE, '', '')

    def move(self, move_color, move_square):
        if self.board[move_square]:
            print("Already occupied!")

    def all_sums(self, board, avoid_number = -1):
        for x in range(0, 8):
            yield board_sum(self.board, orientations[x])

    def print_all_sums(self):
        for z in all_sums(self.board): print(z)

    def left_specific_player_first(self, this_player):
        for x in self.win_logs[this_player]:
            if not self.win_logs[this_player][x]:
                return True
        return False

    def print_wins_so_far(self):
        if not victories:
            print("So far, the kid hasn't notched any interesting or worthwhile wins. Yet.".format(self.victories))
            return
        print("So far, you have let the kid win {} unique ways, total.".format(self.victories))
        place = [ 'in the center', 'in the corner', 'on the side' ]
        for x in win_logs:
            you_them = 'you' if x == PLAYER_FIRST else 'them'
            if not self.left_specific_player_first(x):
                print("  You let the kid beat you all three ways (corner, side, center) with {} going first.".format(you_them))
                continue
            for y in win_logs[x]:
                if win_logs[x][y]:
                    print("  You managed to lose with {} going first {}.".format(you_them, place[y - 1]))

    def show_board(self):
        if self.show_moves and len(self.moves):
            print("Moves:", mt.listnum(self.moves))
        row_string = ''
        for y in range(0, 9):
            raw_idx = self.board[y]
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
                if y != 8: print("--+--+--")
            else:
                row_string += "|"

    def kid_pick_square(self):
        if len(self.moves) == 0:
            return self.kid_start_square()
        ary = [x for x in range(0, 9) if not self.board[x]]
        blocking_moves = find_blocking_move(board, kid_color)
        winning_moves = find_winning_move(board, kid_color)
        auto_moves = find_automatic_move(board, kid_color)
        forking_move = find_forking_move(board, kid_color, remove_blocks = False)
        forking_move_block = find_forking_move(board, kid_color)
        if len(winning_moves):
            print("I think this wins!")
            return random.choice(list(winning_moves))
        if len(forking_move):
            fork_position = board_sum(board)
            if not len(blocking_moves):
                print("The kid shifts and giggles slightly.")
                return random.choice(forking_move)
            print("\"I see that.\" The kid shifts and giggles slightly.")
            return random.choice(forking_move_block)
        if len(auto_moves[0]):
            if len(auto_moves[0]) > 1:
                print("OOPS! 2 auto moves in position:", mt.listnum(auto_moves[0]))
            print("No choice, really.")
            return random.choice(list(auto_moves[0]))
        if len(blocking_moves):
            return random.choice(list(blocking_moves))
        (where_to_move, my_tree_num) = check_dupe_trees(self.board)
        if my_tree_num not in tree_move_dict and my_tree_num != -1:
            sys.exit("Need my_tree_num for {}.".format(my_tree_num))
        print(tree_text[my_tree_num])
        return where_to_move

    def kid_move(self):
        temp = self.kid_pick_square()
        self.place_move(temp)

    def player_move(self):
        while 1:
            my_move = input("Which square? (0-8, 0=UL, 2=UR, 6=DL, 8=DR)").lower().strip()
            try:
                if my_move[0] == 'd' and my_move[1:].isdigit():
                    temp = int(my_move[1:])
                    if temp >= len(display_descriptions):
                        print("Only 0 through {} is valid to change display descriptions.".format(len(display_descriptions)))
                    elif temp != self.display_type:
                        self.display_type = temp
                        print("Changed display type:", display_descriptions[self.display_type])
                        self.show_board()
                    else:
                        print("Display type was already", display_descriptions[self.display_type])
                    continue
            except:
                pass
            if my_move == '':
                self.show_board()
                continue
            m0 = my_move[0]
            if m0 == 'a':
                about()
                continue
            if m0 == 'c':
                credits()
                continue
            if my_move == 'l' or my_move == 's' or my_move == 'w':
                self.print_wins_so_far()
                continue
            if my_move == 'm':
                self.show_moves = not self.show_moves
                self.show_board(board)
                continue
            if m0 == 'q':
                sys.exit("Bye!")
            if m0 == 'v' or m0 == '?':
                show_possible_commands()
                continue
            # debug-only commands here
            if my_move == 'pa' and debug == True:
                self.print_all_sums()
            try:
                x = int(my_move)
            except:
                print("Unknown command. V or ? gives a list of commands.")
                continue
            if x < 0 or x > len(board):
                print("You need something from 0 to {}.".format(len(board) - 1))
                continue
            if self.board[x] != 0:
                print("Something is already on square", x)
                continue
            if len(self.moves) == 0:
                self.first_location = locations[x]
            before_moves = len(find_blocking_move(self.board, my_color))
            self.place_move(x)
            if before_moves:
                after_moves = len(find_blocking_move(self.board, my_color))
                self.played_correctly = before_moves - after_moves
            return

    def place_move(self, square):
        self.board[square] = self.current_mover
        if len(self.moves) == 0:
            self.first_square_type = locations[square]
        self.moves.append(square)
        self.cell_idx[square] = len(self.moves)
        self.show_board()

    def next_move(self):
        if self.check_game_end():
            self.clear_and_restart_game()
            return
        if self.current_mover == my_color:
            self.player_move()
        else:
            self.kid_move()
        self.current_mover = other_color(self.current_mover)

def other_color(move_color):
    if move_color == 0:
        return 0
    return my_color + kid_color - move_color

def usage():
    print("USAGE: d/v = debug/verbose, t = test rotations, c = check needed branches, a = all rotations of a certain #")
    sys.exit()

def init_wins():
    for x in location_types:
        for y in colors:
            win_logs[y][x] = False

def d_print(x):
    if debug:
        print(x)

def base_3_of(x):
    ary = []
    for y in range(0, 10):
        ary.append(x % 3)
        x = x // 3
    ary.reverse()
    return(''.join([str(x) for x in ary]))

def nonzeros_3(x):
    y = base_3_of(int(x))
    return y.count('0')

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

def find_forking_move(board, to_move_color, remove_blocks = True):
    ret_array = []
    if remove_blocks:
        blocks = find_blocking_move(board, to_move_color)
    for x in range(0, 9):
        board_temp = list(board)
        if board_temp[x]:
            continue
        board_temp[x] = to_move_color
        wins = find_winning_move(board_temp, to_move_color)
        if len(wins) >= 2:
            if remove_blocks and blocks and x not in blocks: continue
            ret_array.append(x)
        d_print("fork check {} {} {} {}".format(x, ret_array, board_temp, wins))
    return ret_array

def find_calculated_move(board, kid_color):
    blocking_moves = find_blocking_move(board, kid_color)
    winning_moves = find_winning_move(board, kid_color)
    auto_moves = find_automatic_move(board, kid_color)
    forking_move = find_forking_move(board, kid_color, remove_blocks = False)
    forking_move_block = find_forking_move(board, kid_color)
    if len(winning_moves):
        return(random.choice(list(winning_moves)), "I think this wins!", "<KID WINS>")
    if len(forking_move):
        fork_position = board_sum(board)
        if not len(blocking_moves):
            return(random.choice(forking_move), "The kid shifts and giggles slightly.", "<KID SEES A FORK>")
        return(random.choice(forking_move_block), "\"I see that.\" The kid shifts and giggles slightly.", "<KID SEES A FORK>")
    if len(auto_moves[0]):
        if len(auto_moves[0]) > 1:
            print("OOPS! 2 auto moves in position:", mt.listnum(auto_moves[0]))
        return(random.choice(list(auto_moves[0])), '"No choice, really."', "<ONLY ONE OBVIOUS MOVE>")
    return(NO_MOVE, '', '')

def print_wins_so_far():
    place = [ 'in the center', 'in the corner', 'on the side' ]
    if not victories:
        print("So far, you have let the kid win {} unique ways, total.".format(self.victories))
        return
    print("So far, you have let the kid win {} unique ways, total.".format(victories))
    for x in win_logs:
        you_them = 'you' if x == PLAYER_FIRST else 'them'
        if not left_specific_player_first(win_logs, x):
            print("You let the kid beat you all three ways with {} going first.".format(you_them))
            continue
        for y in win_logs[x]:
            if win_logs[x][y]:
                print("You managed to lose with {} going first {}.".format(you_them, place[y - 1]))

def board_sum(board, my_rot = range(0, 9)):
    mult = 1
    sum = 0
    for y in range(0, 9):
        sum += board[my_rot[y]] * mult
        mult *= 3
    return sum

def board_of(a_num):
    temp = []
    for y in range(0, 9):
        temp.append(a_num % 3)
        a_num //= 3
    return temp

def see_poss_parents(a_num):
    b = board_of(a_num)
    got_one = False
    for x in tree_move_dict:
        if x == a_num: continue
        can_retro = True
        c = board_of(x)
        for y in range(0, 9):
            if b[y] == c[y]: continue
            if c[y] == 0: continue
            can_retro = False
        if can_retro:
            print(x, "may be below", a_num)
            print(c, b)
            show_board(board_of(x))
            show_board(board_of(a_num))
            got_one = True
    if not got_one: print("No parents for", a_num)

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
            if board_sum(board) not in tree_move_dict:
                for z in all_sums(board):
                    if board_sum(board) != z: skip = True
            if skip: continue
            (a, b) = check_dupe_trees(temp_board)
            #print("Tree status of", temp_board, board_sum(temp_board), "is", b, "from", my_board, board_sum(my_board))
            if tree_move_status[b] < 0:
                continue
            if a > -1:
                if temp_board[a]:
                    print("Uh oh overwrote position", a, "with status", b, "value", temp_board[a], "on", temp_board, "from", board, "moves so far", moves_so_far)
                    show_board(board)
                    sys.exit(tree_move_status)
                temp_board[a] = 2
                temp_moves_2 = list(temp_moves)
                temp_moves_2.append(a)
                see_needed_branches(temp_board, temp_moves_2, depth + 1)
            else:
                print("Need entry for", board_sum(temp_board))
                show_board(board)
                print("Moves so far", moves_so_far)
            #print("End of", move_try, "depth=", depth)

def check_all_needed_branches():
    see_needed_branches(board, [])
    see_needed_branches([0, 0, 0, 0, 2, 0, 0, 0, 0], [])
    see_needed_branches([2, 0, 0, 0, 0, 0, 0, 0, 0], [])
    see_needed_branches([0, 2, 0, 0, 0, 0, 0, 0, 0], [])

def inverse_matrix_of(x):
    temp = orientations.index(x)
    return orientations[inverse[temp]]

def assign_inverse_orientations():
    global inverse
    for x in range(0, 8):
      ary1 = orientations[x]
      for y in range(0, 8):
        ary2 = orientations[y]
        matches = 0
        for z in range(0,9):
          if ary1[ary2[z]] == z: matches += 1
        if matches == 9:
            if debug:
                print("Inverse of", x, ary1, "is", y, ary2)
            inverse[x] = y

def rotation_index(a_sum, a_board):
    b2 = board_of(a_sum)
    #print(b2, a_board)
    for x in orientations:
        blank_board = []
        can_match = True
        new_ary = [b2[x[q]] for q in range(0, 9)]
        #print(b2, "goes to", new_ary, "via", x, a_board)
        for y in range(0, 9):
            if a_board[y] != new_ary[y]: can_match = False
        if can_match: return inverse_matrix_of(x)
    sys.exit("Could not rotate {} onto {}.".format(a_sum, a_board))

def check_dupe_trees(board):
    my_sum = 0
    orig_sum = board_sum(board)
    for y in all_sums(board):
        if y in tree_move_dict:
            if my_sum and y != my_sum:
                print("Warning", y, "duplicates", my_sum)
            my_sum = y
    if not my_sum:
        print("Warning no directions for", board_sum(board), base_3_of(board_sum(board)))
        print("Define one of", list(all_sums(board)))
        show_board(board)
        sys.exit()
        return (-1, -1)
    for y in all_sums(board):
        if y in tree_move_dict:
            my_ary = rotation_index(y, board)
            if tree_move_dict[my_sum] >= 0:
                return(my_ary[tree_move_dict[my_sum]], my_sum)
            else:
                return(tree_move_dict[my_sum], my_sum)
    return (tree_move_dict[my_sum], my_sum)

def verify_dict_tree(bail = False, move_to_find = 1):
    if not os.path.exists("ttt.txt"):
        sys.exit("ttt.py requires ttt.txt to read in configurations. Please check that ttt.txt is in the same folder as ttt.py before continuing.")
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            if line.startswith("move=") or line.startswith("msg"): continue
            ary = line.split("\t")
            for q in ary[0].split(','):
                if nonzeros_3(q) % 2 != move_to_find:
                    print(x, "bad", line_count)
                    bail = True
                else:
                    print(q, "ok", nonzeros_3(q))
    if bail:
        sys.exit()

def read_game_stuff(bail = False):
    text_macro = defaultdict(str)
    in_intro = False
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            if line.startswith("msg-type"):
                ary = line.split("\t")
                win_msg[int(ary[1])][int(ary[2])] = ary[3]
                continue
            if line.startswith("msg-time"):
                ary = line.split("\t")
                wins_in_order.append(ary[1].strip().replace("\\n", "\n"))
                continue
            if line.strip() == 'INTRO-START':
                in_intro = True
                continue
            if line.strip() == 'INTRO-END':
                in_intro = False
                continue
            if in_intro:
                intro_array.append(line.strip())
                continue
            if line.startswith("move="):
                (prefix, data) = mt.cfg_data_split(line)
                move_to_find = int(data)
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
            ary = line.split("\t")
            if len(ary) != 4:
                print("Bad # of tabs (need 3) at line {}.".format(line_count))
                bail = True
            if 1:
                a2 = [int(x) for x in ary[0].split(",")]
                for ia2 in a2:
                    for q in identicals(ia2):
                        if q in tree_move_dict:
                            print(ia2, "duplicates earlier", q)
                            bail = True
                    tree_move_dict[ia2] = int(ary[1])
                    tree_move_status[ia2] = int(ary[2])
                    tree_text[ia2] = ary[3]
                    if debug: print("Adding", ia2, "to tree.")
            if 0:
                sys.exit("Oh no! Had trouble parsing line {}: {}".format(line_count, line))
    if bail:
        sys.exit("Fix ttt before playing.")

def in_pos_file(x):
    for y in identicals(x):
        if y in tree_move_dict:
            return y
    return -1

def all_sums(board, avoid_number = -1):
    for x in range(0, 8):
        yield board_sum(board, orientations[x])

def identicals(x):
    temp = x
    bary = []
    for i in range(0, 9):
        bary.append(temp % 3)
        temp //= 3
    return all_sums(bary)

def is_rotated(x, y):
    return y in identicals(x)

def check_move_trees(board):
    for q in all_sums(board):
        if q not in tree_move_dict:
            continue
            print(q, "not in tree_move_dict")
        else:
            return True
            print(q, "in tree_move_dict with suggested move", tree_move_dict[q])
    return False

def print_all_sums():
    for z in all_sums(board): print(z)

def show_board(board):
    row_string = ''
    for y in range(0, 9):
        row_string += ' ' if y in cell_idx else str(y)
        raw_idx = board[y]
        if display_type == O_PLAYER:
            if raw_idx:
                raw_idx = other_color(raw_idx)
        elif display_type == X_PLAYER:
            pass
        elif display_type == X_FIRST:
            if initial_mover == KID_FIRST:
                raw_idx = other_color(raw_idx)
        elif display_type == O_FIRST:
            if initial_mover == PLAYER_FIRST:
                raw_idx = other_color(raw_idx)
        row_string += play_ary[board[y]]
        if y % 3 == 2:
            print(row_string)
            row_string = ""
            if y != 8: print("--+--+--")
        else:
            row_string += "|"

def clear_game():
    global board
    global moves
    global blocks_this_game
    board = [0] * 9
    moves = []
    cell_idx.clear()
    blocks_this_game = 0

def left_specific_player_first(my_dict, my_dict_idx):
    for x in my_dict[my_dict_idx]:
        if not my_dict[my_dict_idx][x]:
            return True
    return False

def game_setup():
    clear_game()
    need_you_first = left_specific_player_first(win_logs, PLAYER_FIRST)
    need_kid_first = left_specific_player_first(win_logs, KID_FIRST)
    if not need_kid_first and not need_you_first:
        sys.exit("Hooray! The kid is happy to have beaten you in all possible ways.")
    global initial_mover
    if not need_kid_first:
        print("Since the kid has won starting in the corner, center and sides, you go first.")
        initial_mover = PLAYER_FIRST
        return NO_MOVE
    picks_list = list([x for x in win_logs[KID_FIRST] if not win_logs[KID_FIRST][x]])
    kid_picks_index = random.choice(picks_list)
    if kid_picks_index == CENTER:
        kid_picks = 4
    elif kid_picks_index == SIDE:
        kid_picks = random.choice([1,3,5,7])
    else:
        kid_picks = random.choice([0,2,6,8])
    if not need_you_first:
        print("Since you've won all three ways with you first, the kid starts.")
        initial_mover = KID_FIRST
        return kid_picks
    while 1:
        who_moves = input("A new game. Who moves first? 1 = you, 2 = the kid{}.".format(", (enter) = keep going {}".format('first' if initial_mover == 1 else 'second') if initial_mover != 0 else '')).lower().strip()
        if who_moves == '1':
            initial_mover = PLAYER_FIRST
            return NO_MOVE
        if who_moves == '2':
            initial_mover = KID_FIRST
            break
        if not who_moves and initial_mover:
            if initial_mover == PLAYER_FIRST:
                return NO_MOVE
            return kid_picks
    return kid_picks

def start_game():
    temp = game_setup()
    global board
    global first_square_type
    if temp != NO_MOVE:
        board[temp] = kid_color
        moves.append(temp)
        cell_idx[temp] = len(moves)
        first_square_type = locations[temp]
    show_board(board)

def check_board(board, whose_turn):
    if board[2] and board[2] == board[4] == board[6]:
        d_print("Diagonal match UL/DR.")
        return whose_turn
    if board[0] and board[0] == board[4] == board[8]:
        d_print("Diagonal match UR/DL.")
        return whose_turn
    for x in range(0, 3):
        if board[3*x] and board[3*x] == board[3*x+1] == board[3*x+2]:
            d_print("Horizontal match: row {}".format(x))
            return whose_turn
        if board[x] and board[x] == board[x+3] == board[x+6]:
            d_print("Vertical match: row {}".format(x))
            return whose_turn
    for x in range(0, 9):
        if not board[x]:
            return CONTINUE_PLAYING
    return BOARD_FULL_DRAW

def all_rotations(initial_board_num):
    initial_board = board_of(initial_board_num)
    for x in orientations:
        y = [0] * 9
        for z in range(0, 9):
            y[z] = initial_board[x[z]]
        show_board(y)
        print(y, board_sum(y))

def test_rotations(bail = True):
    rotations = [ 166, 174, 190, 918, 414, 6966, 3078, 8910 ]
    for r in rotations:
        b = board_of(r)
        (where_to_move, my_tree_num) = check_dupe_trees(b)
        print()
        print(r, b, where_to_move, my_tree_num)
        show_board(b)
        print("to")
        b[where_to_move] = 2
        show_board(b)
    if bail:
        sys.exit()

def check_game_end():
    if check_board(board, my_color) == my_color:
        print("The kid won!")
        if not played_correctly:
            print("But they don't look happy. \"No fair! I'm not a baby! You made it too easy.\"")
            return True
        if win_logs[initial_mover][first_square_type] == True:
            print("But sadly, they don't look that happy. They already beat you that way!")
            return True
        for x in won_forks:
            if x == fork_position:
                print("You're a bit surprised when the kid proclaims they already won from this exact position, so it really shouldn't count.")
                return True
            if is_rotated(x, fork_position):
                print("You're a bit surprised when the kid starts mentioning how this win LOOKED sort of like another one, so they're not sure if it should count. You undo the last couple moves and rotate and flip the board in your head, and yeah, you have to agree.")
                return True
        else:
            print(win_msg[initial_mover][first_square_type])
            win_logs[initial_mover][first_square_type] = True
            global victories
            print(wins_in_order[victories])
            print()
            victories += 1
        return True
    if len(moves) == 9:
        print("It's a stalemate.")
        return True
    return False

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

board = [0,0,0,0,0,0,0,0,0]
moves = []

assign_inverse_orientations()

# initialization stuff

cmd_count = 1
use_class = True

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'd' or arg == 'v':
        debug = True
    elif arg == 'c':
        check_needed = True
    elif arg == 'cy' or arg == 'yc':
        use_class = True
    elif arg == 'cn' or arg == 'nc':
        use_class = False
    elif arg == 't':
        test_rotations()
    elif arg[0] == 'a':
        all_rotations(int(arg[1:]))
        exit()
    else:
        usage()
    cmd_count += 1

read_game_stuff()

if check_needed:
    check_all_needed_branches()

if use_class:
    my_games = game()
    while 1:
        my_games.next_move()
    sys.exit()

init_wins()

# put tests below here
# put tests above here

show_introductory_text()
start_game()

while 1:
    (auto_moves_you, auto_kibitz) = find_automatic_move(board, my_color)
    before_moves = find_blocking_move(board, my_color)
    if debug:
        if len(auto_moves_you) == 1:
            print("You should probably", auto_kibitz, auto_moves_you)
        elif len(auto_moves_you) == 0:
            print(auto_kibitz)
        else:
            print("You have multiple ways to win/lose:", list(auto_moves_you))
    my_move = input("Which square? (0-8, 0=UL, 2=UR, 6=DL, 8=DR)").lower().strip()
    try:
        if my_move[0] == 'x' and my_move[1:].isdigit():
            temp = int(my_move[1:])
            if temp >= len(display_descriptions):
                print("Only 0 through {} is valid to change display descriptions.".format(len(display_descriptions)))
            elif temp != display_type:
                print("Changed display type:", display_descriptions[display_type])
                show_board(board)
            else:
                print("Display type was already", display_descriptions[display_type])
            continue
    except:
        pass
    if debug and my_move == 'x':
        sys.exit("Bye!")
    if my_move == '':
        show_board(board)
        continue
    if my_move == 'pa' and debug == True:
        print_all_sums()
    if my_move == 'm':
        show_moves = not show_moves
        show_board(board)
        continue
    if my_move == 'q':
        exit()
    if my_move == '?':
        print_wins_so_far()
        continue
    try:
        x = int(my_move)
    except:
        print("Unknown command.")
        continue
    if x < 0 or x > len(board):
        print("You need something from 0 to {}.".format(len(board) - 1))
        continue
    if len(moves) == 0:
        first_square_type = locations[x]
    if board[x]:
        print("Something's already there!")
        continue
    board[x] = my_color
    moves.append(x)
    cell_idx[x] = len(moves)
    show_board(board)
    played_correctly = True
    if len(before_moves):
        after_moves = find_blocking_move(board, my_color)
        if len(before_moves) == len(after_moves):
            played_correctly = False
    if check_board(board, my_color) == my_color:
        print("You won! This should not have happened, but it did.")
        start_game()
        continue
    (kid_square, the_msg, debug_msg) = find_calculated_move(board, kid_color)
    if kid_square != NO_MOVE:
        print("Moving to", kid_square)
        d_print(debug_msg)
        board[kid_square] = kid_color
        moves.append(kid_square)
        cell_idx[kid_square] = len(moves)
        show_board(board)
        if check_game_end():
            start_game()
        continue
    (auto_moves_kid, auto_kibitz) = find_automatic_move(board, kid_color)
    if len(auto_moves_kid) == 1:
        print("The kid moves quickly.")
        where_to_move = list(auto_moves_kid)[0]
        tree_num = -1
        if auto_kibitz == 'block':
            blocks_this_game += 1
    else:
        (where_to_move, my_tree_num) = check_dupe_trees(board)
        if my_tree_num not in tree_move_dict and my_tree_num != -1: sys.exit("Need my_tree_num for {}.".format(my_tree_num))
    if where_to_move == NO_MOVE:
        print("It's a draw, so you try again.")
        start_game()
        continue
    did_you_fail = len(auto_moves_kid) > len(auto_moves_you)
    d_print("AI decides move: {} from tree branch {}, officially {}".format(where_to_move, my_tree_num, board_sum(board)))
    if board[where_to_move]: sys.exit("Oops tried to move on occupied square {} for {}.".format(where_to_move, my_tree_num))
    board[where_to_move] = kid_color
    moves.append(where_to_move)
    cell_idx[where_to_move] = len(moves)
    print()
    print(tree_text[my_tree_num])
    print()
    show_board(board)
    if check_game_end():
        start_game()

#    except KeyboardInterrupt:
#        exit()
#    except:
#        print("Oops parser error.")