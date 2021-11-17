#
# wai.py: Walking Around It
#

import sys
import numpy
import re

whose_move = [ ' ', 'X', 'O' ]
move_type = [ 'block', 'win' ]

EMPTY_PLAYER = 0
X_PLAYER = 1
Y_PLAYER = 2

def possible_wins(the_board, the_move, look_for_win):
    potential_wins = []
    for w in wins:
        so_far = 0
        last_blank = -1
        for x in range(0, 3):
            this_square = the_board[w[x][0]][w[x][1]][w[x][2]]
            if this_square == 0:
                last_blank = x
            elif this_square == the_move:
                so_far += 1
        if so_far == 2 and last_blank != -1:
            potential_wins.append(''.join([str(j) for j in w[x]]))
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

def play_a_game():
    my_board = numpy.zeros((3, 3, 3), dtype=numpy.int8)
    current_move = X_PLAYER
    move_list = []
    while 1:
        possible_wins(my_board, 3 - current_move, False)
        potential_wins = possible_wins(my_board, current_move, True)

        if len(potential_wins) > 0:
            print("Potential {}{} at {}".format(move_type[look_for_win], 's' if len(potential_wins) > 1 else '', ', '.join(potential_wins)))

        x = input("Where will {} move (x, y, z coordinate)?".format(whose_move[current_move])).strip().lower()

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


