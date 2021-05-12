import sys

from collections import defaultdict

tree_move_dict = defaultdict(int)
tree_move_status = defaultdict(int)
tree_text = defaultdict(int)
inverse = defaultdict(int)
cell_idx = defaultdict(int)

play_ary = ['-', 'X', 'O']
my_color = 1
ghost_color = 2

debug = True

show_moves = False

you_won = 1
ghost_won = 2
no_result = 0

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
            my_ary = the_rotation(y, board)
            return(my_ary[tree_move_dict[my_sum]], my_sum)
    return (tree_move_dict[my_sum], my_sum)

def verify_dict_tree(bail = False, move_to_find = 1):
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            if line.startswith("move="):
                (prefix, data) = my.cfg_to_data(line)
                move_to_find = int(data)
                continue
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
    with open("ttt.txt") as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
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
    if bail: sys.exit("Fix ttt before playing.")

def board_sum(board, my_rot = range(0, 9)):
    mult = 1
    sum = 0
    for y in range(0, 9):
        sum += board[my_rot[y]] * mult
        mult *= 3
    return sum

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
    board = [0] * 9
    moves = []
    cell_idx.clear()
    show_board(board)
    
def check_board(board, whose_turn):
    if board[2] and board[2] == board[4] == board[6]:
        print("Diagonal match UL/DR.")
        return whose_turn
    if board[0] and board[0] == board[4] == board[8]:
        print("Diagonal match UR/DL.")
        return whose_turn
    for x in range(0, 2):
        if board[3*x] and board[3*x] == board[3*x+1] == board[3*x+2]:
            print("Horizontal match row", x)
            return whose_turn
        if board[x] and board[x] == board[x+3] == board[x+6]:
            print("Vertical match row", x)
            return whose_turn
    return no_result

orientations = [
 [0,1,2,3,4,5,6,7,8],
 [0,3,6,1,4,7,2,5,8],
 [2,5,8,1,4,7,0,3,6],
 [2,1,0,5,4,3,8,7,6],
 [8,7,6,5,4,3,2,1,0],
 [8,5,2,7,4,1,6,3,0],
 [6,7,8,3,4,5,0,1,2],
 [6,3,0,7,4,1,8,5,2]
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
    #print("Inverse of", x, ary1, "is", y, ary2)
        inverse[x] = y

read_dict_tree()
clear_game()

while 1:
    if 1:
        if debug:
            for x in range(0, 9):
                if board[x] == 0:
                    board2 = list(board)
                    board2[x] = 1
                    if not check_move_trees(board2):
                        print("Define move tree for", board_sum(board2), "square", x)
        my_move = input("Which square? (0-8, 0=UL, 2=UR, 6=DL, 8=DR)").lower().strip()
        if my_move == '':
            show_board(board)
            continue
        if x == 'pa' and debug == True:
            print_all_sums()
        if x == 'm':
            show_moves = not show_moves
            show_board(board)
            continue
        if x == 'q':
            exit()
        x = int(my_move)
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
        (where_to_move, my_tree_num) = check_dupe_trees(board)
        print(where_to_move, my_tree_num)
        if where_to_move == -1:
            print("It's a draw, so you try again.")
            clear_game()
            continue
        if board[where_to_move]: sys.exit("Oops tried to move on occupied square {} for {}.".format(where_to_move, my_tree_num))
        if my_tree_num not in tree_move_dict: sys.exit("Need my_tree_num for {}.".format(my_tree_num))
        board[where_to_move] = ghost_color
        moves.append(ghost_color)
        cell_idx[ghost_color] = len(moves)
        print()
        print(tree_text[my_tree_num])
        print()
        show_board(board)
        if check_board(board, my_color) == my_color:
            print("The ghost won!")
            clear_game()
            continue
        if moves == 9:
            print("It's a stalemate.")
            clear_game()
            continue
#    except KeyboardInterrupt:
#        exit()
#    except:
#        print("Oops parser error.")