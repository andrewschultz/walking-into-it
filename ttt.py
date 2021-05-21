#
#
# tic tac toe python game
#
# where you meet a kid who wants to beat you, but not after you make obvious dumb mistakes
#

import random
import sys
import mytools as mt
from collections import defaultdict

tree_move_dict = defaultdict(int)
tree_move_status = defaultdict(int)
tree_text = defaultdict(int)
inverse = defaultdict(int)
cell_idx = defaultdict(int)

win_logs = defaultdict(lambda: defaultdict(bool))
win_msg = defaultdict(lambda: defaultdict(str))

play_ary = ['-', 'X', 'O']
my_color = 1
kid_color = 2

# constants are listed in order of descending difficulty for the ghost
CENTER = 1
CORNER = 2
SIDE = 3
PLAYER_FIRST = 1
KID_FIRST = 2

locations = [ CORNER, SIDE, CORNER, SIDE, CENTER, SIDE, CORNER, SIDE, CORNER ]
location_types = [ CORNER, SIDE, CENTER ]
colors = [ PLAYER_FIRST, KID_FIRST ]

wins = [ [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6] ]

first_mover = -2

debug = False

show_moves = False
check_needed = False

CONTINUE_PLAYING = 0
BOARD_FULL_DRAW = -1
you_won = 1 # should never happen but just in case
kid_won = 2

total_blocks = 0

def other_color(move_color):
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
        blank_square = -1
        for square in w:
            if board[square]:
                this_triple[board[square]] += 1
            else:
                blank_square = square
        if this_triple[two_of_color] == 2 and blank_square != -1:
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

def find_forking_move(board, to_move_color):
    ret_array = []
    for x in range(0, 9):
        board_temp = list(board)
        if board_temp[x]:
            continue
        board_temp[x] = to_move_color
        wins = find_winning_move(board_temp, to_move_color)
        if len(wins) >= 2:
            ret_array.append(x)
        print("fork check", x, ret_array, board_temp, wins)
    return ret_array

def wins_so_far():
    place = [ 'in the center', 'in the corner', 'on the side' ]
    finds = 0
    for x in win_logs:
        for y in win_logs[x]:
            if win_logs[x][y]:
                finds += 1
                print("You managed to lose with {} going first {}.".format('you' if y == PLAYER_FIRST else 'them', place[x-1]))
    if not finds:
        print("You haven't managed to lose any ways yet.")

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

def read_dict_tree(bail = False):
    text_macro = defaultdict(str)
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            if line.startswith("msg"):
                ary = line.split("\t")
                win_msg[int(ary[1])][int(ary[2])] = ary[3]
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
    global total_blocks
    board = [0] * 9
    moves = []
    cell_idx.clear()
    show_board(board)
    total_blocks = 0

def any_left(my_dict, my_dict_idx):
    for x in my_dict[my_dict_idx]:
        if not my_dict[my_dict_idx][x]:
            return True
    return False

def start_game():
    clear_game()
    need_you_first = any_left(win_logs, PLAYER_FIRST)
    need_kid_first = any_left(win_logs, KID_FIRST)
    if not need_kid_first and not need_you_first:
        sys.exit("Hooray! The kid is happy to have beaten you in all possible ways.")
    if not need_kid_first:
        print("Since the kid has won starting in the corner, center and sides, you go first.")
        return -1
    rand_first_move = random.choice(list(win_logs))
    if not need_you_first:
        print("Since you've won all three ways with you first, the kid chooses.")
        return rand_first_move
    while 1:
        print(first_mover)
        who_moves = input("Who moves first? 1 = you, 2 = the kid{}.".format(", (enter) = keep going {}".format('first' if first_mover == -1 else 'second') if first_mover != -2 else '')).lower().strip()
        if who_moves == '1':
            return -1
        if who_moves == '2':
            return rand_first_move
        if not who_moves:
            if first_mover == -2:
                continue
            if first_mover == -1:
                return -1
            return rand_first_move

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

# initialization stuff

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'd' or arg == 'v':
        debug = True
    elif arg == 'c':
        check_needed = True
    elif arg == 't':
        test_rotations()
    elif arg[0] == 'a':
        all_rotations(int(arg[1:]))
        exit()
    else:
        usage()
    cmd_count += 1

read_dict_tree()

if check_needed:
    check_all_needed_branches()

init_wins()

# put tests below here

while 1:
    first_mover = start_game()
    print("!", first_mover)
    if first_mover != -1:
        board[first_mover] = kid_color
        moves.append(first_mover)
        cell_idx[first_mover] = len(moves)
        show_board(board)
    while 1:
        (auto_moves_you, auto_kibitz) = find_automatic_move(board, my_color)
        if debug:
            if len(auto_moves_you) == 1:
                print("You should probably", auto_kibitz, auto_moves_you)
            elif len(auto_moves_you) == 0:
                print(auto_kibitz)
            else:
                print("You have multiple ways to win/lose:", list(auto_moves_you))
        my_move = input("Which square? (0-8, 0=UL, 2=UR, 6=DL, 8=DR)").lower().strip()
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
            wins_so_far()
            continue
        try:
            x = int(my_move)
        except:
            print("Unknown command.")
            continue
        if x < 0 or x > len(board):
            print("You need something from 0 to {}.".format(len(board)-1))
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
        if check_board(board, my_color) == my_color:
            print("You won!")
            clear_game()
            continue
        my_square = find_forking_move(board, kid_color)
        if my_square:
            board[my_square[0]] = kid_color
            moves.append(my_square[0])
            cell_idx[my_square[0]] = len(moves)
            print("...winning fork at", my_square[0], my_square)
            show_board(board)
            continue
        (auto_moves_kid, auto_kibitz) = find_automatic_move(board, kid_color)
        if len(auto_moves_kid) == 1:
            print("The kid moves quickly.")
            where_to_move = list(auto_moves_kid)[0]
            tree_num = -1
            if auto_kibitz == 'block':
                total_blocks += 1
        else:
            (where_to_move, my_tree_num) = check_dupe_trees(board)
            if my_tree_num not in tree_move_dict and my_tree_num != -1: sys.exit("Need my_tree_num for {}.".format(my_tree_num))
        if where_to_move == -1:
            print("It's a draw, so you try again.")
            break
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
        if check_board(board, my_color) == my_color:
            print("The kid won!")
            if win_logs[first_square_type][first_mover] == True:
                print("But sadly, they don't look that happy. They already beat you that way!")
            else:
                for x in win_msg: print(win_msg[x])
                print(win_msg[first_square_type][first_mover])
                win_logs[first_square_type][first_mover] = True
            break
        if len(moves) == 9:
            print("It's a stalemate.")
            break
#    except KeyboardInterrupt:
#        exit()
#    except:
#        print("Oops parser error.")