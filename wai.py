#
# wai.py: Walking Around It
#
# the extra game for WII
#

import sys
import numpy
import re

whose_move = [ ' ', 'X', 'O' ]
move_type = [ 'block', 'win' ]

EMPTY_PLAYER = 0
X_PLAYER = 1
Y_PLAYER = 2

played_before = False

def to_num(my_tuple):
    return ''.join([str(a) for a in my_tuple])

def is_two_match(the_board, the_move, three_squares):
    freq = [0, 0, 0]
    for x in range(0, 3):
        this_square = the_board[three_squares[x][0]][three_squares[x][1]][three_squares[x][2]]
        freq[this_square] += 1
        if this_square == 0:
            open_square = three_squares[x]
    if freq[0] == 1 and freq[the_move] == 2:
        return open_square
    return None

def possible_wins(the_board, the_move, look_for_win):
    potential_wins = []
    for w in wins:
        temp = is_two_match(the_board, the_move, w)
        if temp:
            potential_wins.append(''.join([str(j) for j in temp]))
    return potential_wins

def print_board(the_board):
    for z in range (2, -1, -1):
        for y in range (2, -1, -1):
            print("{}|{}|{}".format(whose_move[the_board[0][y][z]], whose_move[the_board[1][y][z]], whose_move[the_board[2][y][z]]))
            if y != 0:
                print("-+-+-")
        if z != 0:
            print()

def check_win(the_board, the_move):
    for j in wins:
        in_a_row = 0
        for x in range(0, 3):
            in_a_row += the_board[j[x][0]][j[x][1]][j[x][2]] == the_move
        if in_a_row == 3:
            return j
    return 0

def possible_forks(this_board, this_move):
    poss = []
    for c in coords:
        if this_board[c] != 0:
            continue
        this_board[c] = this_move
        wins_this_square = 0
        for w in wins:
            if c not in w:
                continue
            temp = is_two_match(this_board, this_move, w)
            wins_this_square += (temp != None)
        if wins_this_square > 1:
            poss.append(c)
        this_board[c] = 0
    return poss

def play_a_game():
    my_board = numpy.zeros((3, 3, 3), dtype=numpy.int8)
    current_move = X_PLAYER
    move_list = []
    global played_before
    if played_before:
        print("You look at things again. Maybe there's a way to make a draw, or maybe there's a way to prove there's no draw.")
    else:
        print("Three-by-three-by-three tic-tac-toe. Someone showed it to you when you got bored of the two-dimensional version. It was interesting for a while. Someone always seemed to win. But it was usually the first player. It didn't take long to figure the forced win. But you wondered, would there be a way to get no wins? Even if you played badly?")
        played_before = True
    print_board(my_board)
    while 1:
        potential_blocks = possible_wins(my_board, 3 - current_move, False)
        potential_wins = possible_wins(my_board, current_move, True)
        potential_forks = possible_forks(my_board, current_move)

        if len(potential_blocks) > 0:
            print("Need to block at {}".format(', '.join(potential_blocks)))

        if len(potential_wins) > 0:
            print("Potential win{} at {}".format('s' if len(potential_wins) > 1 else '', ', '.join(potential_wins)))

        if len(potential_forks) > 0:
            print("Winning forks at {}".format(', '.join([to_num(x) for x in potential_forks])))

        x = input("Where will {} move (000 through 222, for horizontal/vertical/up)?".format(whose_move[current_move])).strip().lower()

        if x[0] == '':
            print_board(my_board)
            continue
        if x.startswith('quit'):
            print("You put your little thought experiment down.")
            sys.exit()
        elif x[0] == 'q':
            print("Note: the game requires you to type out QUIT so you don't quit by accident. Ctrl-c also works.")
            continue

        if x[0] == 'm':
            if len(move_list) == 0:
                print("No moves yet.")
                continue
            print("Moves so far, in order:")
            print("    " + ', '.join([str(x) for x in move_list]))

        if x[0] == 'u':
            if len(move_list) == 0:
                print("Nothing to undo.")
                continue
            temp = move_list.pop()
            my_board[temp // 100][(temp // 10) % 10][temp % 10] = 0
            print_board(my_board)
            continue

        if re.search("^[012]{3}$", x):
            coord = []
            for y in x:
                coord.append(int(y))
            if my_board[coord[0]][coord[1]][coord[2]] != 0:
                print("Already a piece there.")
                continue
            my_board[coord[0]][coord[1]][coord[2]] = current_move
            print_board(my_board)
            temp = check_win(my_board, current_move)
            if temp:
                print("{} has a winner at {}.".format(whose_move[current_move], temp))
                return
            current_move = 3 - current_move
            move_list.append(100 * coord[0] + 10 * coord[1] + coord[2])

coords = []

for a in range (0, 3):
    for b in range (0, 3):
        for c in range (0, 3):
            coords.append((a, b, c))

wins = [ ((0, 0, 0), (0, 0, 1), (0, 0, 2)),
((0, 1, 0), (0, 1, 1), (0, 1, 2)),
((0, 2, 0), (0, 2, 1), (0, 2, 2)),
((1, 0, 0), (1, 0, 1), (1, 0, 2)),
((1, 1, 0), (1, 1, 1), (1, 1, 2)),
((1, 2, 0), (1, 2, 1), (1, 2, 2)),
((2, 0, 0), (2, 0, 1), (2, 0, 2)),
((2, 1, 0), (2, 1, 1), (2, 1, 2)),
((2, 2, 0), (2, 2, 1), (2, 2, 2)),
((0, 0, 2), (0, 1, 1), (0, 2, 0)),
((1, 0, 2), (1, 1, 1), (1, 2, 0)),
((2, 0, 2), (2, 1, 1), (2, 2, 0)),
((0, 0, 0), (0, 1, 0), (0, 2, 0)),
((0, 0, 1), (0, 1, 1), (0, 2, 1)),
((0, 0, 2), (0, 1, 2), (0, 2, 2)),
((1, 0, 0), (1, 1, 0), (1, 2, 0)),
((1, 0, 1), (1, 1, 1), (1, 2, 1)),
((1, 0, 2), (1, 1, 2), (1, 2, 2)),
((2, 0, 0), (2, 1, 0), (2, 2, 0)),
((2, 0, 1), (2, 1, 1), (2, 2, 1)),
((2, 0, 2), (2, 1, 2), (2, 2, 2)),
((0, 0, 0), (0, 1, 1), (0, 2, 2)),
((1, 0, 0), (1, 1, 1), (1, 2, 2)),
((2, 0, 0), (2, 1, 1), (2, 2, 2)),
((0, 2, 2), (1, 1, 1), (2, 0, 0)),
((0, 2, 0), (1, 1, 0), (2, 0, 0)),
((0, 2, 1), (1, 1, 1), (2, 0, 1)),
((0, 2, 2), (1, 1, 2), (2, 0, 2)),
((0, 2, 0), (1, 1, 1), (2, 0, 2)),
((0, 0, 2), (1, 0, 1), (2, 0, 0)),
((0, 1, 2), (1, 1, 1), (2, 1, 0)),
((0, 2, 2), (1, 2, 1), (2, 2, 0)),
((0, 0, 0), (1, 0, 0), (2, 0, 0)),
((0, 0, 1), (1, 0, 1), (2, 0, 1)),
((0, 0, 2), (1, 0, 2), (2, 0, 2)),
((0, 1, 0), (1, 1, 0), (2, 1, 0)),
((0, 1, 1), (1, 1, 1), (2, 1, 1)),
((0, 1, 2), (1, 1, 2), (2, 1, 2)),
((0, 2, 0), (1, 2, 0), (2, 2, 0)),
((0, 2, 1), (1, 2, 1), (2, 2, 1)),
((0, 2, 2), (1, 2, 2), (2, 2, 2)),
((0, 0, 0), (1, 0, 1), (2, 0, 2)),
((0, 1, 0), (1, 1, 1), (2, 1, 2)),
((0, 2, 0), (1, 2, 1), (2, 2, 2)),
((0, 0, 2), (1, 1, 1), (2, 2, 0)),
((0, 0, 0), (1, 1, 0), (2, 2, 0)),
((0, 0, 1), (1, 1, 1), (2, 2, 1)),
((0, 0, 2), (1, 1, 2), (2, 2, 2)),
((0, 0, 0), (1, 1, 1), (2, 2, 2))
]

while 1:
    play_a_game()


