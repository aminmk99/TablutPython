def evaluate(board, player_color):
    """
    Simple evaluation function.
    Returns a numeric score from the perspective of player_color.
    Higher = better for player_color.
    """

    my_count = 0
    enemy_count = 0

    for row in board:
        for cell in row:
            if cell == player_color:
                my_count += 1
            else:
                if player_color == "WHITE" and cell == "BLACK":
                    enemy_count += 1
                elif player_color == "BLACK" and cell == "WHITE":
                    enemy_count += 1

    # Very simple heuristic: piece difference
    return my_count - enemy_count
