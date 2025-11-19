def evaluate(board, player_color):
    """
    Stronger evaluation for Tablut.
    Works for both WHITE (king side) and BLACK (attackers).
    """

    # ----------------------------------------------------------------------
    # Basic counts
    # ----------------------------------------------------------------------
    white_count = 0
    black_count = 0
    king_pos = None

    for r in range(9):
        for c in range(9):
            cell = board[r][c]
            if cell == "WHITE":
                white_count += 1
            elif cell == "BLACK":
                black_count += 1
            elif cell == "KING":
                king_pos = (r, c)

    # score starts at piece difference (scaled)
    score = (white_count - black_count) * 2

    # ----------------------------------------------------------------------
    # King-related evaluation
    # ----------------------------------------------------------------------
    if king_pos is not None:
        kr, kc = king_pos

        # 1. Distance to nearest escape tile (corners)
        escapes = [(0,0), (0,8), (8,0), (8,8)]
        min_escape = min(abs(kr-er) + abs(kc-ec) for (er,ec) in escapes)

        # Closer to escape is good for WHITE, bad for BLACK
        if player_color == "WHITE":
            score += (10 - min_escape) * 5
        else:
            score -= (10 - min_escape) * 5

        # 2. King mobility (available legal moves)
        mobility = king_mobility(board, king_pos)
        if player_color == "WHITE":
            score += mobility * 4
        else:
            score -= mobility * 4

    else:
        # king missing → game is already lost
        if player_color == "WHITE":
            return -99999
        else:
            return 99999

    # ----------------------------------------------------------------------
    # Attacker advantage if surrounding king
    # (encirclement bonus)
    # ----------------------------------------------------------------------
    encircle = king_surrounded_level(board, king_pos)
    if player_color == "BLACK":
        score += encircle * 6
    else:
        score -= encircle * 6

    return score

def king_mobility(board, king_pos):
    r, c = king_pos
    moves = 0

    # up
    rr = r - 1
    while rr >= 0 and board[rr][c] == "EMPTY":
        moves += 1
        rr -= 1

    # down
    rr = r + 1
    while rr < 9 and board[rr][c] == "EMPTY":
        moves += 1
        rr += 1

    # left
    cc = c - 1
    while cc >= 0 and board[r][cc] == "EMPTY":
        moves += 1
        cc -= 1

    # right
    cc = c + 1
    while cc < 9 and board[r][cc] == "EMPTY":
        moves += 1
        cc += 1

    return moves

def king_surrounded_level(board, king_pos):
    r, c = king_pos
    threats = 0

    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    for dr, dc in dirs:
        rr = r + dr
        cc = c + dc
        if 0 <= rr < 9 and 0 <= cc < 9:
            if board[rr][cc] == "BLACK":
                threats += 1

    return threats
