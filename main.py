# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
# For more info see docs.battlesnake.com

import typing
import sys
import math
import copy
import json
import sys

# info is called when you create your Battlesnake on play.battlesnake.com and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data


def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# helper function to get the correct snake
def get_correct_snake(game_state, maximizing):
    if maximizing:
        return game_state['you']
    else:
        for snake in game_state['board']['snakes']:
            if snake['id'] != game_state['you']['id']:
                return snake


def get_safe_moves(game_state, maximizing):
    # TODO: Change snake depending on maximizing value
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # Store head position in variable to save code
    # Coordinates of your head
    my_head = get_correct_snake(game_state, maximizing)['body'][0]

    # Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:
        is_move_safe["up"] = False

    # Step 2 - Prevent your Battlesnake from colliding with itself
    # Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    # Opponents include our snake, therefore satifying step 2.
    # Since our snake's body includes its neck,
    # this also satifies not going backwards.
    opponents = game_state['board']['snakes']

    surrounding_cells = {
        'left': {'x': my_head['x'] - 1, 'y': my_head['y']},
        'right': {'x': my_head['x'] + 1, 'y': my_head['y']},
        'up': {'x': my_head['x'], 'y': my_head['y'] + 1},
        'down': {'x': my_head['x'], 'y': my_head['y'] - 1}
    }

    for opponent in opponents:
        for direction, cell in surrounding_cells.items():
            if cell in opponent['body']:
                is_move_safe[direction] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"""MOVE {game_state['turn']} {maximizing}: No safe moves detected! Moving down""")
        return ["down"]

    return safe_moves


def apply_move(game_state, move, maximizing):
    # Create a deep copy of the game state to simulate the move without affecting the original state
    new_game_state = copy.deepcopy(game_state)
    my_snake = get_correct_snake(new_game_state, maximizing)

    # Create shorthand for snake head
    head = my_snake['head']

    if move == 'up':
        head['y'] += 1
    elif move == 'down':
        head['y'] -= 1
    elif move == 'left':
        head['x'] -= 1
    elif move == 'right':
        head['x'] += 1

    # Simulate eating food
    if head in new_game_state['board']['food']:
        # Snake grows; don't remove tail in this move
        my_snake['body'].insert(0, {"x": head["x"], "y": head["y"]})
        new_game_state['board']['food'] = [food for food in new_game_state['board']
                                           ['food'] if not (food['x'] == head['x'] and food['y'] == head['y'])]
    else:
        # Move snake forward by inserting a copy of the new head location
        my_snake['body'].insert(0, {"x": head["x"], "y": head["y"]})
        my_snake['body'].pop()

    return new_game_state


# helper function for get_state_value
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def get_state_value(game_state, move, maximizing):
    # The max/min float values are always less than/greater then
    # their respective infinities, while still being "infinity"
    # larger or smaller than any value possibly calculatable
    infinity = 0
    if maximizing:
        infinity = sys.float_info.max
    else:
        infinity = -sys.float_info.max
    value = 0
    my_current_snake = get_correct_snake(game_state, maximizing)
    my_snake = {
        "id": my_current_snake["id"],
        "body": [{"x": s["x"], "y": s["y"]} for s in my_current_snake["body"]],
        "head": {"x": my_current_snake["head"]["x"], "y": my_current_snake["head"]["y"]}
    }
    my_head = my_snake['head']

    if move == 'up':
        my_head['y'] += 1
    elif move == 'down':
        my_head['y'] -= 1
    elif move == 'left':
        my_head['x'] -= 1
    elif move == 'right':
        my_head['x'] += 1

    my_snake['body'].insert(0, {"x": my_head["x"], "y": my_head["y"]})
    if (move != None):
        my_snake['body'].pop()

    my_length = len(my_snake['body'])

    food = game_state['board']['food']

    food_dist = []

    for f in food:
        f_dist = distance(my_head['x'], my_head['y'], f['x'], f['y'])
        food_dist.append((f, f_dist))

    def sort_dist(t):
        return t[1]

    food_dist.sort(key=sort_dist)

    if not food_dist:
        value = infinity
    else:
        value = (1 / (food_dist[0][1] + 1)) * 100

    for snake in game_state['board']['snakes']:
        if snake['id'] != my_snake['id']:
            opponent_head = snake['body'][0]
            opponent_length = len(snake['body'])

            opponent_head_zone = [
                {'x': opponent_head['x'] - 1, 'y': opponent_head['y']},
                {'x': opponent_head['x'] + 1, 'y': opponent_head['y']},
                {'x': opponent_head['x'], 'y': opponent_head['y'] + 1},
                {'x': opponent_head['x'], 'y': opponent_head['y'] - 1}
            ]

            # Prioritize getting closer to smaller snakes
            if my_length > opponent_length:
                # If stepping into opponent head zone while opponent is smaller, increase value
                if my_head in opponent_head_zone:
                    value = infinity

            # Penalize getting too close to bigger snakes unless you have a strategy to deal with them
            elif my_length <= opponent_length:
                # If stepping into opponent head zone while opponent is smaller, decrease value to nothing (near-certain death awaits)
                if my_head in opponent_head_zone:
                    value = -infinity

    if maximizing:
        return value
    else:
        return -value


class GameStateNode():
    def __init__(self, game_state, value=None, maximizing=True, move=None):
        self.maximizing = maximizing
        self.move = move
        self.value = value
        self.game_state = game_state
        self.safe_moves = get_safe_moves(game_state, maximizing)

    def getChildren(self):
        children = []
        for safe_move in self.safe_moves:
            node_value = get_state_value(self.game_state, safe_move, self.maximizing)
            new_game_state = apply_move(self.game_state, safe_move, self.maximizing)
            children.append(GameStateNode(new_game_state, node_value, not self.maximizing, safe_move))
        return children

    def getLocation(self):
        snake = get_correct_snake(self.game_state, self.maximizing)
        return snake["head"]["x"], snake["head"]["y"]


def alphabeta(node, depth, alpha, beta, maximizingPlayer):
    # print("\t"*(7-depth), node.maximizing, node.getLocation(), depth, node.value, node.move)

    children = node.getChildren()

    if depth == 0 or not children:
        return node.value, node.move

    if maximizingPlayer:
        value = float('-inf')
        best_move = None
        for child in children:
            child_value, _ = alphabeta(child, depth-1, alpha, beta, False)
            child_value += node.value
            if child_value > value:
                value = child_value
                best_move = child.move
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cut-off
        # print("\t"*(7-depth), "returning: ", value, best_move)
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for child in children:
            child_value, _ = alphabeta(child, depth-1, alpha, beta, True)
            child_value += node.value
            if child_value < value:
                value = child_value
                best_move = child.move
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cut-off
        # print("\t"*(7-depth), "returning: ", value, best_move)
        return value, best_move


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    if len(game_state["board"]["snakes"]) == 1:
        return {"move": "down"}

    safe_moves = get_safe_moves(game_state, True)

    if not safe_moves:
        print(f"MOVE {game_state['turn']}: No safe moves. Moving down.")
        return {"move": "down"}

    origin = GameStateNode(game_state, value=get_state_value(game_state, None, True))
    depth = 7
    alpha = float('-inf')
    beta = float('inf')
    next_move_value, next_move = alphabeta(origin, depth, alpha, beta, True)

    print(f"MOVE {game_state['turn']}: {next_move}")

    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    port = "8000"
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '--port':
            port = sys.argv[i+1]

    run_server({"info": info, "start": start, "move": move, "end": end, "port": port})
