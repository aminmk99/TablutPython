import string

def get_legal_moves(board, player_color):
    """
    SUPER SIMPLE MOVE GENERATOR.
    Only generates 1-step orthogonal moves if the destination is EMPTY.
    This is NOT the full Tablut rules!
    But enough to test Minimax architecture.
    """

    moves = []
    size = len(board)

    # Cell label conversion helper
    valid_columns = list(string.ascii_uppercase[:size])
    valid_rows = list(range(1, size + 1))

    def coord_to_pos(r, c):
        return f"{valid_columns[c]}{valid_rows[r]}"

    for r in range(size):
        for c in range(size):
            if board[r][c] == player_color:

                # Try Up
                if r - 1 >= 0 and board[r - 1][c] == "EMPTY":
                    moves.append({
                        "from": coord_to_pos(r, c),
                        "to": coord_to_pos(r - 1, c),
                        "turn": player_color
                    })

                # Try Down
                if r + 1 < size and board[r + 1][c] == "EMPTY":
                    moves.append({
                        "from": coord_to_pos(r, c),
                        "to": coord_to_pos(r + 1, c),
                        "turn": player_color
                    })

                # Try Left
                if c - 1 >= 0 and board[r][c - 1] == "EMPTY":
                    moves.append({
                        "from": coord_to_pos(r, c),
                        "to": coord_to_pos(r, c - 1),
                        "turn": player_color
                    })

                # Try Right
                if c + 1 < size and board[r][c + 1] == "EMPTY":
                    moves.append({
                        "from": coord_to_pos(r, c),
                        "to": coord_to_pos(r, c + 1),
                        "turn": player_color
                    })

    return moves
