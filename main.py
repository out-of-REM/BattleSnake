# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# For more info see docs.battlesnake.com

import typing
import sys
import math
import random
import copy

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
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


# distance helper function
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def get_safe_moves(game_state, maximizing):
    # TODO: Change snake depending on maximizing value
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # Store head position in variable to save code
    my_head = game_state["you"]["body"][0]  # Coordinates of your head

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
        print(f"MOVE {game_state['turn']
                      }: No safe moves detected! Moving down")
        return ["down"]

    return safe_moves


def apply_move(game_state, move, maximizing):
    new_game_state = copy.deepcopy(game_state)
    snake = new_game_state['you']  # Assuming this applies to your snake
    
    # Determine the new head position based on the move
    dx, dy = 0, 0
    if move == 'left': dx = -1
    elif move == 'right': dx = 1
    elif move == 'up': dy = -1
    elif move == 'down': dy = 1

    new_head = {'x': snake['body'][0]['x'] + dx, 'y': snake['body'][0]['y'] + dy}

    # Add the new head to the snake's body
    snake['body'].insert(0, new_head)

    # Check if the move results in eating food
    if new_head in new_game_state['board']['food']:
        new_game_state['board']['food'].remove(new_head)  # Remove eaten food
        snake['health'] = 100  # Assume replenished health (or adjust according to game rules)
    else:
        snake['body'].pop()  # Remove the tail if no food is eaten

    return new_game_state


def get_state_value(game_state):
    value = 0
    my_snake = game_state['you']
    my_head = my_snake['body'][0]
    my_length = len(my_snake['body'])

    # Base value on health - less aggressive approach but necessary for survival
    value += my_snake['health']

    # Aggressiveness factor
    aggression_multiplier = 10  # Adjust this value to tweak aggressiveness

    for snake in game_state['board']['snakes']:
        if snake['id'] != my_snake['id']:
            opponent_head = snake['body'][0]
            opponent_length = len(snake['body'])
            distance_to_opponent = abs(my_head['x'] - opponent_head['x']) + abs(my_head['y'] - opponent_head['y'])

            # Prioritize getting closer to smaller snakes
            if my_length > opponent_length:
                # Inverse of distance to make closer snakes have higher value, multiplied by aggressiveness factor
                value += (10 - distance_to_opponent) * aggression_multiplier
            
            # Penalize getting too close to bigger snakes unless you have a strategy to deal with them
            if my_length <= opponent_length:
                value -= (10 - distance_to_opponent) * aggression_multiplier

    # Consider other strategic factors, such as controlling the center of the board or escape routes

    return value

class GameStateNode():
    def __init__(self, game_state, maximizing=True, move=None):
        self.maximizing = maximizing
        self.move = move
        self.safe_moves = get_safe_moves(game_state, maximizing)
        self.value = get_state_value(game_state, maximizing)
        self.game_state = game_state

    def getChildren(self):
        for safe_move in self.safe_moves:
            new_game_state = apply_move(self.game_state, safe_move,
                                        self.maximizing)
            yield GameStateNode(new_game_state, not self.maximizing, safe_move)

    def is_terminal(game_state):
        my_snake = game_state['you']
        head = my_snake['body'][0]

        # Check for collision with walls
        board_width = game_state['board']['width']
        board_height = game_state['board']['height']
        if head['x'] < 0 or head['x'] >= board_width or head['y'] < 0 or head['y'] >= board_height:
            return True  # The snake has collided with a wall

        # Check for self-collision
        if head in my_snake['body'][1:]:
            return True  # The snake has collided with itself

        # Check for collisions with other snakes
        for snake in game_state['board']['snakes']:
            if snake['id'] != my_snake['id'] and head in snake['body']:
                return True  # The snake has collided with another snake

        # Additional terminal conditions can be checked here, e.g., winning conditions

        return False  # If none of the terminal conditions are met, the game is not in a terminal state

def minimax(game_state_node, depth):
    # print("\t"*(3-depth), game_state_node.maximizing, depth,
    #      game_state_node.value, game_state_node.move)
    children = game_state_node.getChildren()
    if (depth == 0) or (not children):
        return game_state_node.value, game_state_node.move
    if game_state_node.maximizing:
        value = float('-inf')
        best_move = None
        for child in children:
            child_value = minimax(child, depth - 1)[0]
            if child_value > value:
                value = child_value
                best_move = child.move
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for child in children:
            child_value = minimax(child, depth - 1)[0]
            if child_value < value:
                value = child_value
                best_move = child.move
        return value, best_move

def alphabeta(node, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or node.is_terminal():
        return get_state_value(node.game_state, maximizingPlayer), node.move

    if maximizingPlayer:
        value = float('-inf')
        best_move = None
        for child in node.get_children():
            child_value, _ = alphabeta(child, depth-1, alpha, beta, False)
            if child_value > value:
                value = child_value
                best_move = child.move
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cut-off
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for child in node.get_children():
            child_value, _ = alphabeta(child, depth-1, alpha, beta, True)
            if child_value < value:
                value = child_value
                best_move = child.move
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cut-off
        return value, best_move

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    safe_moves = get_safe_moves(game_state, True)

    origin = GameStateNode(game_state)
    depth = 3

    alpha = float('inf')
    beta = float('inf')
    next_move_value, next_move = alphabeta(origin,depth,alpha,beta,True)

    print(f"MOVE {game_state['turn']}: {next_move}")

    return {"move": next_move}

    # TODO: Integrate the below inaccessable code as part of get_state_value

    # Step 4 - Move towards food instead of random,
    # to regain health and survive longer
    food = game_state['board']['food']

    # Temporarily duplicating these variables as this system will be removed
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    surrounding_cells = {
        'left': {'x': my_head['x'] - 1, 'y': my_head['y']},
        'right': {'x': my_head['x'] + 1, 'y': my_head['y']},
        'up': {'x': my_head['x'], 'y': my_head['y'] + 1},
        'down': {'x': my_head['x'], 'y': my_head['y'] - 1}
    }

    food_dist = []

    for f in food:
        f_dist = distance(my_head['x'], my_head['y'], f['x'], f['y'])
        food_dist.append((f, f_dist))

    def sort_dist(t):
        return t[1]

    food_dist.sort(key=sort_dist)

    safe_dist = []

    for safe_move in safe_moves:
        sx = surrounding_cells[safe_move]['x']
        sy = surrounding_cells[safe_move]['y']
        s_dist = distance(sx, sy, food_dist[0][0]['x'], food_dist[0][0]['y'])
        safe_dist.append((safe_move, s_dist))

    safe_dist.sort(key=sort_dist)

    next_move = safe_dist[0][0]


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    port = "8000"
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '--port':
            port = sys.argv[i+1]

    run_server({"info": info, "start": start,
               "move": move, "end": end, "port": port})
