# tttests.py: This contains tic-tac-toe tests I wanted to pull from the original file, which was getting a bit long.

def see_needed_branches(my_board, moves_so_far, depth = 1):
    '''this notes if the current board has a branch/action setting listed in ttt.txt'''
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
                for x in all_sums_from_board(my_board):
                    if board_sum(my_board) != x:
                        skip = True
            if skip:
                continue
            (temp_val, temp_board) = check_dupe_trees(temp_board)
            print("Tree status of", temp_board, board_sum(temp_board),
                "is", temp_board, "from", my_board, board_sum(my_board))
            if tree_move_status[temp_board] < 0:
                continue
            if temp_val > -1:
                if temp_board[temp_val]:
                    print("Uh oh overwrote position", temp_val, "with status", temp_board,
                        "value", temp_board[temp_val], "on", temp_board, "from", my_board,
                        "moves so far", moves_so_far)
                    quick_board(my_board)
                    sys.exit(tree_move_status)
                temp_board[temp_val] = 2
                temp_moves_2 = list(temp_moves)
                temp_moves_2.append(temp_val)
                see_needed_branches(temp_board, temp_moves_2, depth + 1)
            else:
                print("Need entry for", board_sum(temp_board))
                quick_board(my_board)
                print("Moves so far", moves_so_far)
            #print("End of", move_try, "depth=", depth)

def check_all_needed_branches():
    '''checks all branches where you start, or where opponent starts, center, side or corner'''
    see_needed_branches([0] * 9, []) # you
    see_needed_branches([0, 0, 0, 0, 2, 0, 0, 0, 0], []) # opponent center
    see_needed_branches([2, 0, 0, 0, 0, 0, 0, 0, 0], []) # opponent corner
    see_needed_branches([0, 2, 0, 0, 0, 0, 0, 0, 0], []) # opponent side

def see_poss_parents(a_num):
    '''given a board, finds ttt.txt's numbers to see what parents there might be of current board
    this was formerly used when building the ttt.txt list of plays, etc.'''
    base_board = board_of(a_num)
    got_one = False
    for x in tree_move_dict:
        if x == a_num:
            continue
        can_retro = True
        var_board = board_of(x)
        for y in range(0, 9):
            if base_board[y] == var_board[y] or var_board[y] == 0:
                continue
            can_retro = False
        if can_retro:
            print(x, "may be below", a_num)
            print(var_board, base_board)
            quick_board(board_of(x))
            quick_board(board_of(a_num))
            got_one = True
    if not got_one:
        print("No parents for", a_num)

def show_all_rotations(initial_board_num):
    '''gives a detailed view of all rotated boards, given an initial board sum'''
    initial_board = board_of(initial_board_num)
    for my_orient in orientations:
        temp_board = [0] * 9
        for x in range(0, 9):
            temp_board[x] = initial_board[my_orient[x]]
        quick_board(temp_board)
        print(temp_board, board_sum(temp_board))

def test_rotations(bail = True):
    '''this tests a very specific and simple rotation case so we know the arithmetic is right'''
    rotations = [ 166, 174, 190, 918, 414, 6966, 3078, 8910 ]
    for x in rotations:
        this_rotation = board_of(x)
        (where_to_move, my_tree_num) = check_dupe_trees(this_rotation)
        print()
        print(x, this_rotation, where_to_move, my_tree_num)
        quick_board(this_rotation)
        print("to")
        this_rotation[where_to_move] = 2
        quick_board(this_rotation)
    if bail:
        sys.exit()

