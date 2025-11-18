import string

def get_legal_moves(board, player_color):
    """
    Less-dumb move generator:
    - Pieces move orthogonally (up/down/left/right)
    - Any number of consecutive EMPTY squares
    - Stops when hitting a non-empty cell (piece, camp, castle, etc.)
    NOTE: still simplified, but MUCH closer to real Tablut.
    """

    moves = []
    size = len(board)

    # column letters A..I, row numbers 1..9 (assuming 9x9)
    valid_columns = list(string.ascii_uppercase[:size])
    valid_rows = list(range(1, size + 1))

    def coord_to_pos(r, c):
        return f"{valid_columns[c]}{valid_rows[r]}"

    # which cells belong to this player?
    def is_my_piece(cell):
        if player_color == "WHITE":
            # in many implementations the king is a separate piece
            return cell == "WHITE" or cell == "KING"
        else:  # BLACK
            return cell == "BLACK"

    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if not is_my_piece(cell):
                continue

            start_pos = coord_to_pos(r, c)

            # explore 4 directions: up, down, left, right
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                # slide while inside board and empty
                while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == "EMPTY":
                    to_pos = coord_to_pos(nr, nc)
                    moves.append({
                        "from": start_pos,
                        "to": to_pos,
                        "turn": player_color
                    })
                    # keep going further in this direction
                    nr += dr
                    nc += dc

    return moves
