import random


class MENACE:
    def __init__(self, player):
        self.boxes = {}
        self.ordered_boxes = [[] for _ in range(4)]
        self.start = [8, 4, 2, 1]
        self.removesymm = True
        self.incentives = [1, 3, -1]
        self.moves = []
        self.player = player


# MENACEs
menace = {1: MENACE(1), 2: MENACE(2)}

# Initialize other variables
player = "h"
plotdata = [0]
xmin = ymin = xmax = ymax = 0

playagain = True
wins_each = [0, 0, 0]
board = [0] * 9
no_winner = True
pieces = ["", "O", "X"]
said = [""] * 10
human_turn = False
pwns = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [6, 4, 2],
]

rotations = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8],
    [0, 3, 6, 1, 4, 7, 2, 5, 8],
    [6, 3, 0, 7, 4, 1, 8, 5, 2],
    [6, 7, 8, 3, 4, 5, 0, 1, 2],
    [8, 7, 6, 5, 4, 3, 2, 1, 0],
    [8, 5, 2, 7, 4, 1, 6, 3, 0],
    [2, 5, 8, 1, 4, 7, 0, 3, 6],
    [2, 1, 0, 5, 4, 3, 8, 7, 6],
]


# Array utility functions
def arrmin(arr):
    return min(arr)


def arrmax(arr):
    return max(arr)


def array_fill(start, length, value):
    return [value] * (length - start)


def count(arr, value):
    return arr.count(value)


# Game functions
def new_game():
    global playagain, menace, board, no_winner, human_turn
    if playagain:
        menace[1].moves = []
        menace[2].moves = []
        board = [0] * 9
        no_winner = True
        play_menace()


def winner(b):
    pos = "".join(map(str, b))
    th = three(pos)
    if th != 0:
        return th
    if count(b, 0) == 0:
        return 0
    return False


def opposite_result(r):
    if r == 0:
        return 0
    return 3 - r


def check_win():
    global no_winner, human_turn
    who_wins = winner(board)
    if who_wins is not False:
        if who_wins == 0:
            say("It's a draw.")
        elif who_wins == 1:
            say("MENACE wins.")
        elif who_wins == 2:
            say(f"{whoA[player]} wins.")
        do_win(who_wins)
        human_turn = False


def do_win(who_wins):
    global no_winner, playagain
    no_winner = False
    menace_add_beads(who_wins)
    if player == "h":
        new_game()


def play_menace():
    global no_winner
    where = get_menace_move(1)
    if where == "resign":
        if count(board, 0) == 9:
            say("MENACE has run out of beads in the first box and refuses to play.")
            return
        do_win(2)
        say("MENACE resigns")
        return
    board[where] = 1
    check_win()
    if no_winner:
        play_opponent()


def play_opponent():
    global human_turn, no_winner
    if player == "h":
        human_turn = True
        return
    human_turn = False
    if player == "r":
        where = get_random_move()
    elif player == "m":
        where = get_menace_move(2)
    elif player == "p":
        where = get_perfect_move()
    if where == "resign":
        do_win(1)
        say("MENACE2 resigns")
        return
    board[where] = 2
    check_win()
    if no_winner:
        play_menace()


# Board functions
def apply_rotation(pos, rot):
    new_pos = ""
    for j in range(9):
        new_pos += pos[rot[j]]
    return new_pos


def find_all_rotations(pos):
    max_rot = []
    max_pos = ""
    for i, rot in enumerate(rotations):
        try_pos = apply_rotation(pos, rot)
        if try_pos > max_pos:
            max_pos = try_pos
            max_rot = [i]
        elif try_pos == max_pos:
            max_rot.append(i)
    return max_rot


def find_rotation(pos):
    max_rot = find_all_rotations(pos)
    return random.choice(max_rot)


def three(pos):
    for p in pwns:
        if pos[p[0]] != "0" and pos[p[0]] == pos[p[1]] == pos[p[2]]:
            return int(pos[p[0]])
    return 0


def rotation_is_max(pos):
    rots = find_all_rotations(pos)
    return rots[0] == 0


# MENACE functions
def add_box(pos, n, s):
    menace[n].ordered_boxes[s].append(pos)
    menace[n].boxes[pos] = new_box(pos, n, menace[n].start[s])


def new_box(pos, n, start):
    rots = find_all_rotations(pos)
    box = array_fill(0, 9, start)
    for i in range(9):
        if pos[i] != "0":
            box[i] = 0
    if menace[n].removesymm:
        for rot in rots[1:]:
            for j in range(9):
                rj = rotations[rot][j]
                if rj != j:
                    box[min(j, rj)] = 0
    return box


def search_moves(b, n):
    played = 10 - count(b, 0)
    move = 2 - played % 2
    other = 3 - move
    minmove = 9
    for i in range(8, -1, -1):
        if b[i] == move:
            minmove = i
    for i in range(minmove):
        if b[i] == 0:
            newboard = b[:]
            newboard[i] = move
            if n == other or n == "both":
                if winner(newboard) is False and rotation_is_max(newboard):
                    add_box("".join(map(str, newboard)), other, played // 2)
            if played < 7:
                search_moves(newboard, n)


def order_boxes(n):
    pass


def reset_menace(n):
    global playagain, plotdata, wins_each
    playagain = True
    for i in range(1, 3):
        if n == i or n == "both":
            menace[i].ordered_boxes = [[] for _ in range(4)]
            menace[i].boxes = {}
    if n == 1 or n == "both":
        plotdata = [0]
        wins_each = [0, 0, 0]
        add_box("000000000", 1, 0)
    search_moves(array_fill(0, 9, 0), n)
    for i in range(1, 3):
        if n == i or n == "both":
            order_boxes(i)
    new_game()


def box_add(pos, move, change, n):
    menace[n].boxes[pos][move] = max(0, change + menace[n].boxes[pos][move])


def menace_add_beads(result):
    for move in menace[1].moves:
        box_add(move[0], move[1], menace[1].incentives[result], 1)
    if player == "m":
        for move in menace[2].moves:
            box_add(move[0], move[1], menace[2].incentives[opposite_result(result)], 2)


def get_menace_move(n):
    if count(board, 0) == 1:
        for i in range(9):
            if board[i] == 0:
                return i
    if count(board, 0) == 9 and not menace[n].boxes:
        say("MENACE is missing boxes and refuses to play.")
        return "resign"
    pos = "".join(map(str, board))
    if pos not in menace[n].boxes:
        if n == 2:
            return "resign"
        add_box(pos, n, (10 - count(board, 0)) // 2)
    box = menace[n].boxes[pos]
    if sum(box) == 0:
        return "resign"
    total = sum(box)
    choice = random.randint(0, total - 1)
    for i in range(9):
        if box[i] > choice:
            move = i
            break
        choice -= box[i]
    menace[n].moves.append([pos, move])
    return move


def get_random_move():
    empty_positions = [i for i, x in enumerate(board) if x == 0]
    return random.choice(empty_positions)


def get_perfect_move():
    pos = "".join(map(str, board))
    boxes = menace[1].boxes
    if pos not in boxes:
        return get_random_move()
    max_beads = max(boxes[pos])
    best_moves = [i for i, x in enumerate(boxes[pos]) if x == max_beads]
    return random.choice(best_moves)


def say(message):
    print(message)


# Starting the game
reset_menace(1)
