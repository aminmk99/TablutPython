import random
import string
import time

# Optional global timeout variable (set from main.py with -timeout)
TIME_LIMIT_SECONDS = 60


def get_next_move(state, player_color):
    """
    Given the current game state (as a Python dict) and the player's color (WHITE or BLACK),
    choose a move and return it as a dict with 'from', 'to', and 'turn' fields.
    """

    # Start timer (for debugging or later time control)
    start_time = time.time()

    # Board structure depends on the server implementation
    # Usually it’s an 9x9 matrix under state['board']
    board = state.get("board", [])

    # All valid cells are typically named like A1, A2, ..., I9
    valid_columns = list(string.ascii_uppercase[:len(board)])
    valid_rows = list(range(1, len(board) + 1))

    # Collect all coordinates with your pieces
    my_pieces = []
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if (player_color == "WHITE" and cell == "WHITE") or \
               (player_color == "BLACK" and cell == "BLACK"):
                my_pieces.append((r, c))

    # Fallback: no pieces found
    if not my_pieces:
        return {"from": "A1", "to": "A1", "turn": player_color}

    # Pick a random piece and move direction (rudimentary!)
    piece = random.choice(my_pieces)

    # Convert indices to cell names (e.g., (0,0) -> A1)
    def coord_to_pos(r, c):
        return f"{valid_columns[c]}{valid_rows[r]}"

    # Try to move randomly within board bounds
    move_found = False
    max_attempts = 50
    for _ in range(max_attempts):
        direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        new_r, new_c = piece
        if direction == "UP":
            new_r -= 1
        elif direction == "DOWN":
            new_r += 1
        elif direction == "LEFT":
            new_c -= 1
        elif direction == "RIGHT":
            new_c += 1

        # Check within bounds
        if 0 <= new_r < len(board) and 0 <= new_c < len(board):
            if board[new_r][new_c] == "EMPTY":  # assuming EMPTY means free cell
                move_found = True
                break

    # Default move (if no legal move found)
    if not move_found:
        return {"from": "A1", "to": "A1", "turn": player_color}

    from_pos = coord_to_pos(piece[0], piece[1])
    to_pos = coord_to_pos(new_r, new_c)

    print(f"[DEBUG] Selected move: {from_pos} → {to_pos}")

    return {"from": from_pos, "to": to_pos, "turn": player_color}
