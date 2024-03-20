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
        my_snake['body'].insert(0, copy.deepcopy(head))
        new_game_state['board']['food'] = [food for food in new_game_state['board']
                                           ['food'] if not (food['x'] == head['x'] and food['y'] == head['y'])]
    else:
        # Move snake forward by inserting a copy of the new head location
        my_snake['body'].insert(0, copy.deepcopy(head))
        my_snake['body'].pop()

    return new_game_state

# helper function for a_star_pathfinding
def generate_neighbors(current, game_state):
    neighbors = []
    # Up, Down, Left, Right movements
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    obstacles = []

    # Convert dictionary-based obstacles to tuple-based obstacles if not already done
    for snake in game_state['board']['snakes']:
        # Add the body parts of all snakes, including your own, to the obstacles list as tuples
        obstacles.extend([(part['x'], part['y'])
                         for part in snake['body'][:-1]])

    # Unpack the current position from a tuple
    cx, cy = current

    for dx, dy in directions:
        neighbor = (cx + dx, cy + dy)  # Generate neighbor as a tuple

        # Check if the neighbor is within the board boundaries
        if 0 <= neighbor[0] < board_width and 0 <= neighbor[1] < board_height:
            # Check if the neighbor is not an obstacle
            if neighbor not in obstacles:
                neighbors.append(neighbor)

    return neighbors

# helper function for get_state_value
def a_star_pathfinding(start, goal, game_state):
    # Heuristic function (Manhattan distance for a grid)
    def heuristic(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax-bx) + abs(ay - by)

    start = (start['x'], start['y'])
    goal = (goal['x'], goal['y'])

    # Initialize both the open and closed sets
    open_set = set([start])
    came_from = {}  # For path reconstruction

    g_score = {start: 0}  # Cost from start to the current node
    # Estimated cost from start to goal through the current node
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))

        if current == goal:
            # Reconstruct path
            total_path = [current]
            while current in came_from:
                current = came_from[current]
                total_path.append(current)
            return total_path[::-1]  # Return reversed path

        open_set.remove(current)

        # Generate neighbors (considering Battlesnake rules: no diagonal moves, avoid walls, self, and others)
        neighbors = generate_neighbors(current, game_state)

        for neighbor in neighbors:
            tentative_g_score = g_score[current] + \
                1  # Assume cost between nodes is 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                # This path is the best so far
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + \
                    heuristic(neighbor, goal)
                open_set.add(neighbor)

    return []  # If there's no path to the goal

def get_state_value(game_state, move, maximizing):
    value = 0
    my_snake = copy.deepcopy(get_correct_snake(game_state, maximizing))
    my_head = my_snake['body'][0]

    if move == 'up':
        my_head['y'] += 1
    elif move == 'down':
        my_head['y'] -= 1
    elif move == 'left':
        my_head['x'] -= 1
    elif move == 'right':
        my_head['x'] += 1

    my_snake['body'].insert(0, copy.deepcopy(my_head))
    my_snake['body'].pop()

    my_length = len(my_snake['body'])
    food_positions = game_state['board']['food']
    shortest_path_length = float('inf')

    # Base value on health - less aggressive approach but necessary for survival
    value += my_snake['health']

    for food in food_positions:
        path = a_star_pathfinding(my_head, food, game_state)
        if path:
            shortest_path_length = min(shortest_path_length, len(path))

    if shortest_path_length != float('inf'):
        value += 100 - (shortest_path_length * 10)

    # Aggressiveness factor
    aggression_multiplier = 5 # Adjust this value to tweak aggressiveness

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

    # TODO we need to implement a pathfinding algorithm, something to remember the history and penalize repeated moves or something that
    # points it in the direction of the food.
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
            node_value = get_state_value(
                self.game_state, safe_move, self.maximizing)
            new_game_state = apply_move(self.game_state,
                                        safe_move, self.maximizing)
            children.append(GameStateNode(
                new_game_state, node_value,
                not self.maximizing, safe_move))
        return children

    def getLocation(self):
        snake = get_correct_snake(self.game_state, self.maximizing)
        return snake["head"]["x"], snake["head"]["y"]

def alphabeta(node, depth, alpha, beta, maximizingPlayer):
    print("\t"*(3-depth), node.maximizing,
          node.getLocation(), depth, node.value, node.move)

    children = node.getChildren()

    if depth == 0 or not children:
        return node.value, node.move

    if maximizingPlayer:
        value = float('-inf')
        best_move = None
        for child in children:
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
        for child in children:
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
    # print(json.dumps(game_state, indent=4))

    if len(game_state["board"]["snakes"]) == 1:
        return {"move": "down"}

    safe_moves = get_safe_moves(game_state, True)

    if not safe_moves:
        print(f"MOVE {game_state['turn']}: No safe moves. Moving down.")
        return {"move": "down"}

    origin = GameStateNode(game_state)
    depth = 1

    alpha = float('-inf')
    beta = float('inf')
    next_move_value, next_move = alphabeta(
        origin, depth, alpha, beta, True)

    print(f"MOVE {game_state['turn']}: {next_move}")

    return {"move": next_move}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    port = "8000"
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '--port':
            port = sys.argv[i+1]

    run_server({"info": info, "start": start,
               "move": move, "end": end, "port": port})