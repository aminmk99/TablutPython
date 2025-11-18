import time
from agent.moves import get_legal_moves
from agent.evaluation import evaluate

TIME_LIMIT_SECONDS = 60  # will be overwritten by main.py if -timeout provided


def minimax(board, depth, alpha, beta, maximizing_player, player_color, start_time):
    """
    Minimax with alpha-beta pruning.
    board: current board state (2D list)
    depth: remaining search depth
    maximizing_player: True/False
    player_color: "WHITE" or "BLACK" (the agent color)
    """

    # Time check (stop early)
    if time.time() - start_time > TIME_LIMIT_SECONDS - 1:
        return evaluate(board, player_color), None

    # Base case
    if depth == 0:
        return evaluate(board, player_color), None

    # Determine which color is playing at this node
    current_color = player_color if maximizing_player else (
        "BLACK" if player_color == "WHITE" else "WHITE"
    )

    # Generate moves
    moves = get_legal_moves(board, current_color)

    if not moves:
        # No moves → treat as very bad for the player whose turn it is
        return evaluate(board, player_color), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_score, _ = minimax(new_board, depth - 1,
                                    alpha, beta,
                                    False, player_color,
                                    start_time)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = float('inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_score, _ = minimax(new_board, depth - 1,
                                    alpha, beta,
                                    True, player_color,
                                    start_time)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval, best_move


def apply_move(board, move):
    """
    Applies a move to a board and returns a NEW board.
    This is a simplified version for now.
    """

    import copy
    new_board = copy.deepcopy(board)

    from_pos = move["from"]
    to_pos = move["to"]

    # Convert A1 → (row,col)
    from_r = int(from_pos[1]) - 1
    from_c = ord(from_pos[0]) - ord('A')

    to_r = int(to_pos[1]) - 1
    to_c = ord(to_pos[0]) - ord('A')

    piece = new_board[from_r][from_c]
    new_board[from_r][from_c] = "EMPTY"
    new_board[to_r][to_c] = piece

    return new_board


def get_next_move(state, player_color):
    """
    Entry point called by main.py
    """

    board = state["board"]

    start_time = time.time()

    # Depth is small for now
    depth = 2

    _, best_move = minimax(
        board,
        depth,
        alpha=float('-inf'),
        beta=float('inf'),
        maximizing_player=True,
        player_color=player_color,
        start_time=start_time
    )

    # Safety fallback
    if best_move is None:
        print("[WARNING] No minimax move found → fallback to random")
        from agent.moves import get_legal_moves
        moves = get_legal_moves(board, player_color)
        if moves:
            return moves[0]
        else:
            return {"from": "A1", "to": "A1", "turn": player_color}

    return best_move
