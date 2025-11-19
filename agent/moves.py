# moves.py
#
# Move generation for Tablut (Ashton rules, simplified):
# - Pieces move like a rook: any number of empty squares orthogonally.
# - Cannot move through or onto: castle (throne) or camps.
# - Exception (handled implicitly): black can move OUT of camps,
#   because the starting square is occupied by the piece, not traversed.


import string


def is_my_piece(cell, player_color):
    if player_color == "WHITE":
        # white soldiers + king belong to white side
        return cell == "WHITE" or cell == "KING"
    else:
        return cell == "BLACK"


def get_legal_moves(board, player_color):
    """
    Generates all legal-looking moves for player_color based on:
    - sliding rook-like moves
    - blocking by pieces, castle, and camps
    NOTE: captures are NOT handled here; only movement legality.
    """

    moves = []
    size = len(board)

    # column labels A..I (for 9x9), row labels 1..9
    valid_columns = list(string.ascii_uppercase[:size])
    valid_rows = list(range(1, size + 1))

    def coord_to_pos(r, c):
        # r, c are 0-based indices; output like "A1", "E5", etc.
        return f"{valid_columns[c]}{valid_rows[r]}"

    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if not is_my_piece(cell, player_color):
                continue

            start_pos = coord_to_pos(r, c)
            piece = cell

            # Four orthogonal directions
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dr, dc in directions:
                nr = r + dr
                nc = c + dc

                # slide while inside board
                while 0 <= nr < size and 0 <= nc < size:
                    # cannot pass through castle or camps
                    if is_block_square(nr, nc, piece):
                        break

                    # cannot move onto occupied squares
                    if board[nr][nc] != "EMPTY":
                        break

                    # At this point, (nr, nc) is an empty, non-blocking square:
                    to_pos = coord_to_pos(nr, nc)
                    moves.append({
                        "from": start_pos,
                        "to": to_pos,
                        "turn": player_color
                    })

                    # continue sliding further
                    nr += dr
                    nc += dc

    return moves


# --------------------------------------------------------------------
# Geometry helpers: castle & camps for 9x9 Ashton Tablut
# (0-based indices: row 0–8, col 0–8)
# --------------------------------------------------------------------

def is_castle(r, c, size):
    # center square: E5 -> (4, 4) on 0-based 9x9
    center = size // 2
    return r == center and c == center


def is_camp(r, c, size):
    """
    Approximate camp coordinates for Ashton Tablut on 9x9.
    We use a conservative set: if we treat a normal cell as camp by mistake,
    we only lose some legal options, but we never generate illegal moves.
    """

    # Using coordinates in (row, col), 0-based
    camps = set()

    # Top camps: D1, E1, F1, E2  -> (0,3), (0,4), (0,5), (1,4)
    camps.update([(0, 3), (0, 4), (0, 5), (1, 4)])
    # Bottom camps: D9, E9, F9, E8 -> (8,3), (8,4), (8,5), (7,4)
    camps.update([(8, 3), (8, 4), (8, 5), (7, 4)])
    # Left camps: A4, A5, A6, B5 -> (3,0), (4,0), (5,0), (4,1)
    camps.update([(3, 0), (4, 0), (5, 0), (4, 1)])
    # Right camps: I4, I5, I6, H5 -> (3,8), (4,8), (5,8), (4,7)
    camps.update([(3, 8), (4, 8), (5, 8), (4, 7)])

    return (r, c) in camps


def is_block_square(r, c, piece):
    """
    Squares that cannot be crossed or ended on:
    - castle (throne)
    - camps
    For simplicity, we treat them as blocking for everyone
    except when a piece is *starting* there.
    """
    size = 9  # fixed for this competition

    # The square containing the piece itself is allowed as a start,
    # but we only call this function on target squares (nr, nc),
    # so we don't need to special-case that here.

    if is_castle(r, c, size):
        # only the king starts here; no one should move onto or through it
        return True

    if is_camp(r, c, size):
        # camps are forbidden to enter or cross for our agent
        return True

    return False
