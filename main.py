import socket
import json
import sys
import struct
import re
from agent.minimax import get_next_move

HOST = 'localhost'
PORTS = {
    "WHITE": 5800,
    "BLACK": 5801
}
PLAYER_NAMES = {
    "WHITE": "ReplayAgentW",
    "BLACK": "ReplayAgentB"
}


def write_message(sock, obj):
    try:
        message_str = json.dumps(obj)
        message_bytes = message_str.encode('utf-8')
        length = len(message_bytes)

        length_bytes = struct.pack('>I', length)

        sock.sendall(length_bytes)
        sock.sendall(message_bytes)

    except (socket.error, struct.error) as e:
        print(f"Error writing message: {e}")
        raise


def read_message(sock):
    try:
        length_bytes = sock.recv(4)
        if not length_bytes:
            print("Server closed connection (read length).")
            return None

        length = struct.unpack('>I', length_bytes)[0]
        message_bytes = b""
        bytes_to_read = length
        while bytes_to_read > 0:
            chunk = sock.recv(min(bytes_to_read, 4096))
            if not chunk:
                raise EOFError("Connection closed before all data was received")
            message_bytes += chunk
            bytes_to_read -= len(chunk)

        message_str = message_bytes.decode('utf-8')
        return json.loads(message_str)

    except (socket.error, struct.error, json.JSONDecodeError, EOFError) as e:
        print(f"Error reading message: {e}")
        return None


def parse_log_file(logfile_path, player_color):
    moves = []
    turn_prefix = f"Turn: {player_color[0]}"
    move_regex = re.compile(r"Turn: ([WB]) Pawn from (\w\d) to (\w\d)")
    try:
        with open(logfile_path, 'r') as f:
            for line in f:
                if turn_prefix in line:
                    match = move_regex.search(line)
                    if match:
                        turn_char, from_pos, to_pos = match.groups()

                        if turn_char == player_color[0]:
                            action = {
                                "from": from_pos,
                                "to": to_pos,
                                "turn": player_color
                            }
                            moves.append(action)
    except FileNotFoundError:
        print(f"Error: Log file not found at {logfile_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading log file: {e}")
        sys.exit(1)

    return moves


def run_client(player_color, player_name, ip_address, replay_movess):
    port = PORTS[player_color]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    replay_queue = list(replay_movess) if replay_movess else None

    try:
        print(f"Connecting to {ip_address}:{port} as {player_color} ({player_name})...")
        sock.connect((ip_address, port))
        print("Connected.")

        write_message(sock, player_name)
        print(f"Sent name: {player_name}")

        while True:
            print("Waiting for server state...")
            state = read_message(sock)
            if not state:
                print("Server closed connection.")
                break

            print("\n" + "=" * 20)
            print(f"[RECEIVED STATE as {player_color}]")
            print("=" * 20 + "\n")

            current_turn = state['turn']

            if current_turn == player_color:
                action = None

                if replay_queue:
                    print(f"Replaying move {len(replay_movess) - len(replay_queue) + 1}/{len(replay_movess)} from log...")
                    action = replay_queue.pop(0)

                if not action:
                    if replay_movess is not None:
                        print("Replay moves finished. Switching to AI.")
                        replay_movess = None

                    print("My turn. Thinking of a move...")
                    action = get_next_move(state, player_color)

                if action:
                    print("\n" + "-" * 20)
                    print(f"[SENDING ACTION as {player_color}]")
                    print(json.dumps(action, indent=2))
                    print("-" * 20 + "\n")

                    write_message(sock, action)
                else:
                    print("No legal moves found. Sending a placeholder.")
                    write_message(sock, {"from": "z0", "to": "z0", "turn": player_color})

            elif current_turn in ["WHITEWIN", "BLACKWIN", "DRAW"]:
                print(f"Game over. Result: {current_turn}")
                break

            else:
                print(f"Waiting for {current_turn}'s move...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sock.close()
        print("Connection closed.")

if __name__ == "__main__":
    import agent.minimax as minimax   # <-- ensure we can override this safely

    args = sys.argv[1:]  # everything after main.py

    logfile = None

    # ----------------------------------------------------
    # Handle -R logfile
    # ----------------------------------------------------
    if "-R" in args:
        try:
            r_index = args.index("-R")
            logfile = args.pop(r_index + 1)
            args.pop(r_index)
        except (IndexError, ValueError):
            print("Error: -R must be followed by a file path.")
            sys.exit(1)

    # ----------------------------------------------------
    # Handle -timeout <value>
    # ----------------------------------------------------
    if "-timeout" in args:
        try:
            t_index = args.index("-timeout")
            timeout_value = float(args.pop(t_index + 1))
            args.pop(t_index)
            minimax.TIME_LIMIT_SECONDS = timeout_value
            print(f"[INFO] TIME_LIMIT_SECONDS set to {timeout_value} (from -timeout flag)")
        except (IndexError, ValueError):
            print("Error: -timeout must be followed by a numeric value.")
            sys.exit(1)

    # ----------------------------------------------------
    # Basic usage check
    # ----------------------------------------------------
    if len(args) < 1 or args[0].upper() not in ["WHITE", "BLACK"]:
        print("\nUsage: python main.py <WHITE|BLACK> [timeout] [ip] [-R logfile] [-timeout sec]")
        sys.exit(1)

    # ----------------------------------------------------
    # Parse required color argument
    # ----------------------------------------------------
    color = args[0].upper()
    name = PLAYER_NAMES[color]
    ip = "localhost"

    # ----------------------------------------------------
    # NEW FEATURE: positional timeout OR IP
    # python main.py WHITE 45
    # python main.py WHITE 192.168.1.20
    # python main.py WHITE 45 192.168.1.20
    # ----------------------------------------------------
    if len(args) >= 2:
        if args[1].isdigit():   # positional timeout
            timeout_value = float(args[1])
            minimax.TIME_LIMIT_SECONDS = timeout_value
            print(f"[INFO] TIME_LIMIT_SECONDS set to {timeout_value} (positional argument)")
            if len(args) >= 3:
                ip = args[2]
                print(f"[INFO] Using custom IP: {ip}")
        else:
            ip = args[1]
            print(f"[INFO] Using custom IP: {ip}")

    # ----------------------------------------------------
    # Load replay moves if any
    # ----------------------------------------------------
    replay_moves = None
    if logfile:
        print(f"Parsing replay file '{logfile}' for {color} moves...")
        replay_moves = parse_log_file(logfile, color)
        if not replay_moves:
            print(f"Warning: No {color} moves found in {logfile}.")
        else:
            print(f"Found {len(replay_moves)} {color} moves to replay.")

    # ----------------------------------------------------
    # Start client
    # ----------------------------------------------------
    run_client(color, name, ip, replay_moves)

