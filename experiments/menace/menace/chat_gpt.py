import random
import json
from collections import defaultdict


class MENACE:
    def __init__(self):
        self.matchboxes = defaultdict(lambda: defaultdict(int))
        self.reset_training_data()

    def reset_training_data(self):
        self.training_data = []

    def get_board_key(self, board):
        return tuple(board)

    def available_moves(self, board):
        return [i for i, spot in enumerate(board) if spot == " "]

    def initialize_matchbox(self, board):
        key = self.get_board_key(board)
        if key not in self.matchboxes:
            for move in self.available_moves(board):
                self.matchboxes[key][move] = 1

    def choose_move(self, board):
        key = self.get_board_key(board)
        self.initialize_matchbox(board)
        moves = list(self.matchboxes[key].items())
        total_beads = sum(count for move, count in moves)
        choice = random.randint(1, total_beads)
        for move, count in moves:
            if choice <= count:
                return move
            choice -= count

    def update_matchboxes(self, outcome):
        for board, move in self.training_data:
            key = self.get_board_key(board)
            if outcome == "win":
                self.matchboxes[key][move] += 3
            elif outcome == "lose":
                self.matchboxes[key][move] = max(1, self.matchboxes[key][move] - 1)
            elif outcome == "draw":
                self.matchboxes[key][move] += 1

    def play_game(self, opponent_move_function):
        board = [" "] * 9
        turn = "X"
        while True:
            if turn == "X":
                move = self.choose_move(board)
                board[move] = "X"
                self.training_data.append((board.copy(), move))
            else:
                move = opponent_move_function(board)
                board[move] = "O"

            winner = self.check_winner(board)
            if winner:
                outcome = "win" if winner == "X" else "lose"
                self.update_matchboxes(outcome)
                return outcome

            if " " not in board:
                self.update_matchboxes("draw")
                return "draw"

            turn = "O" if turn == "X" else "X"

    def check_winner(self, board):
        winning_combinations = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),  # Rows
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),  # Columns
            (0, 4, 8),
            (2, 4, 6),  # Diagonals
        ]
        for i, j, k in winning_combinations:
            if board[i] == board[j] == board[k] != " ":
                return board[i]
        return None

    def save_to_file(self, filename):
        with open(filename, "w") as f:
            json.dump(self.matchboxes, f)

    def load_from_file(self, filename):
        with open(filename, "r") as f:
            self.matchboxes = json.load(f)


def random_opponent_move(board):
    return random.choice([i for i, spot in enumerate(board) if spot == " "])


# Example usage:
menace = MENACE()
for _ in range(10000):  # Train MENACE by playing 10000 games
    menace.play_game(random_opponent_move)

# Save the trained matchboxes to a file
menace.save_to_file("menace.json")
