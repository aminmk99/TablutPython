# evaluation.py
#
# Hybrid evaluation focused on:
# - White: king escape
# - Black: king encirclement
# - Lower weight on pawn count
# - Simple, fast, and tuned for shallow search (depth 2–3)


def evaluate(board, player_color):
    """
    Returns a score from the perspective of player_color.
    Higher score = better for player_color.
    """

    size = len(board)

    # ------------------------------
    # 1. Count pieces & find the king
    # ------------------------------
    white_count = 0
    black_count = 0
    king_pos = None

    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell == "WHITE":
                white_count += 1
            elif cell == "BLACK":
                black_count += 1
            elif cell == "KING":
                king_pos = (r, c)

    # King missing => game is already lost for White
    if king_pos is None:
        return -99999 if player_color == "WHITE" else 99999

    kr, kc = king_pos
    corners = [(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)]

    # ----------------------------------------
    # 2. King already on corner? -> huge win
    # ----------------------------------------
    if (kr, kc) in corners:
        return 99999 if player_color == "WHITE" else -99999

    score = 0

    # -------------------------------------------------
    # 3. Piece difference (low weight, especially White)
    # -------------------------------------------------
    piece_diff = white_count - black_count
    if player_color == "WHITE":
        score += piece_diff * 4    # white pawns are expendable
    else:
        score += piece_diff * 6    # black benefits more from material

    # -------------------------------------------------
    # 4. King distance to nearest corner (escape pressure)
    # -------------------------------------------------
    max_dist = 2 * (size - 1)  # worst-case Manhattan distance
    d_min = min(abs(kr - er) + abs(kc - ec) for (er, ec) in corners)
    escape_proximity = max_dist - d_min  # larger = closer to escape

    ESCAPE_WEIGHT = 20
    if player_color == "WHITE":
        score += ESCAPE_WEIGHT * escape_proximity
    else:
        score -= ESCAPE_WEIGHT * escape_proximity

    # -------------------------------------------------
    # 5. Fully open escape lines (no blockers; ready NOW)
    # -------------------------------------------------
    open_lines = count_open_escape_lines(board, king_pos)
    OPEN_LINE_WEIGHT = 60
    if player_color == "WHITE":
        score += OPEN_LINE_WEIGHT * open_lines
    else:
        score -= OPEN_LINE_WEIGHT * open_lines

    # -------------------------------------------------
    # 6. King mobility (small effect)
    # -------------------------------------------------
    mobility = king_mobility(board, king_pos)
    MOBILITY_WEIGHT = 2
    if player_color == "WHITE":
        score += MOBILITY_WEIGHT * mobility
    else:
        score -= MOBILITY_WEIGHT * mobility

    # -------------------------------------------------
    # 7. Encirclement: black pieces adjacent to king
    # -------------------------------------------------
    encirclement = king_adjacent_black_count(board, king_pos)
    ENCIRCLEMENT_WEIGHT = 40
    if player_color == "BLACK":
        score += ENCIRCLEMENT_WEIGHT * encirclement
    else:
        score -= ENCIRCLEMENT_WEIGHT * encirclement

    return score


# ===========================
# Helper: open escape lines
# ===========================
def count_open_escape_lines(board, king_pos):
    """
    Counts how many directions (up/down/left/right) have a
    completely empty path from the king to the board edge.
    This means the king can escape in 1 move (if rules allow).
    """
    r, c = king_pos
    size = len(board)
    open_lines = 0

    # Up
    rr = r - 1
    while rr >= 0 and board[rr][c] == "EMPTY":
        rr -= 1
    if rr < 0:
        open_lines += 1

    # Down
    rr = r + 1
    while rr < size and board[rr][c] == "EMPTY":
        rr += 1
    if rr >= size:
        open_lines += 1

    # Left
    cc = c - 1
    while cc >= 0 and board[r][cc] == "EMPTY":
        cc -= 1
    if cc < 0:
        open_lines += 1

    # Right
    cc = c + 1
    while cc < size and board[r][cc] == "EMPTY":
        cc += 1
    if cc >= size:
        open_lines += 1

    return open_lines


# ===========================
# Helper: king mobility
# ===========================
def king_mobility(board, king_pos):
    """
    Counts how many squares the king can slide to
    in straight lines (rook moves) through EMPTY cells.
    """
    r, c = king_pos
    size = len(board)
    moves = 0

    # up
    rr = r - 1
    while rr >= 0 and board[rr][c] == "EMPTY":
        moves += 1
        rr -= 1

    # down
    rr = r + 1
    while rr < size and board[rr][c] == "EMPTY":
        moves += 1
        rr += 1

    # left
    cc = c - 1
    while cc >= 0 and board[r][cc] == "EMPTY":
        moves += 1
        cc -= 1

    # right
    cc = c + 1
    while cc < size and board[r][cc] == "EMPTY":
        moves += 1
        cc += 1

    return moves


# ======================================
# Helper: black adjacency to the king
# ======================================
def king_adjacent_black_count(board, king_pos):
    """
    Counts how many black pieces are directly up/down/left/right
    next to the king. More = better for Black, worse for White.
    """
    r, c = king_pos
    size = len(board)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    count = 0

    for dr, dc in dirs:
        rr = r + dr
        cc = c + dc
        if 0 <= rr < size and 0 <= cc < size:
            if board[rr][cc] == "BLACK":
                count += 1

    return count
