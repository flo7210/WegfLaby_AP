from maze import Maze
from balancer import Balancer
from serial import Serial
import time
import math

def run(path, maze):
    with Balancer(Serial(0)) as balancer:        
        # Add first command
        balance_handler.counter = -1
        balance_handler((0, 0), (True, 0, 0), True)

        # Start listening
        balancer.balance_handler = balance_handler
        balancer.start_listening()
        
        # Handlers
        def balance_handler(destination, response, destination_reached):
            (balanced, t, u) = response

            if destination_reached:
                # We are balanced and in the right place
                print(maze.print_path(path[:response_handler.counter + 1], path[-1:]))
                print
                
                # Get next command and skip over skippables
                if response_handler.counter + 1 >= len(path): return

                skippables = maze.get_skippables(path)
                while True:
                    response_handler.counter += 1
                    if response_handler.counter not in skippables: break

                # Add new command
                (tNew, uNew) = to_touchscreen_coord(maze, balancer, path[response_handler.counter])
                print (tNew, uNew)
                print
                balancer.add_command(tNew, uNew)
            else:
                # If we're not in the right place, run old command again
                (tNew, uNew) = destination
                balancer.add_command(tNew, uNew)

def detect_maze():
    dualmaze = Maze(7,5)
    maze = Maze(7, 5)
    visited = []
    neighbors_stack = []

    with Balancer(Serial(0)) as balancer:
        (t, u) = to_touchscreen_coord(maze, balancer, (1, 3))
        balancer.add_command(t, u)

        balancer.balance_handler = balance_handler
        balancer.start_listening()

        # Handlers
        def balance_handler(destination, response, destination_reached):
            (balanced, t, u) = response

            if destination_reached:
                # We are balanced and in the right place
                (x, y) = to_vertex(maze, balancer, (t, u))

                if len(neighbors_stack) == 0 and (x, y) not in visited:
                    # Get neighbors
                    balance_handler.anchor = (x, y)
                    neighbors = maze.get_neighbors(x, y)
                    # but only those which are not in visited
                    neighbors_stack.extend([n for n in neighbors if n not in visited])
                    # print neighbors_stack
                
                if len(neighbors_stack) == 0:
                    return

                # Process neighbors stack
                neighbor = neighbors_stack.pop()
                (tNew, uNew) = to_touchscreen_coord(maze, balancer, neighbor)

                if neighbor != response_handler.anchor:
                    neighbors_stack.append(balance_handler.anchor)

                elif len(neighbors_stack) == 0:
                    # Visited all neighbors of response_handler.anchor
                    visited.append(balance_handler.anchor)
                    print visited

                balancer.add_command(tNew, uNew)
            else:
                # If we're not in the right place, run old command again
                (tNew, uNew) = destination
                balancer.add_command(tNew, uNew)

    return maze
    
# def detect_maze():
#     m = Maze(7, 5)
#     m.add_path([(1, 3), (1, 2), (1, 1), (2, 1), (1, 1), (1, 2), (2, 2), (2, 3), 
#                 (3, 3), (3, 2), (3, 1), 
#                 (4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (5, 1), (5, 2), (6, 2), 
#                 (6, 3), (5, 3), 
#                 (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (4, 4), (4, 5), (5, 5), 
#                 (4, 5), (3, 5), (2, 5), (1, 5), (1, 4), (2, 4),
#                 (4, 4), (5, 4), (6, 4), (6, 5), (7, 5), (7, 4), (7, 3)])

#     return m

def to_touchscreen_coord(maze, balancer, v):
    """Return the corresponding touchscreen coordinates to the given vertex in the maze."""

    width = balancer.width - 2 * balancer.padding
    height = balancer.height - 2 * balancer.padding

    t = v[0] * width / maze.width - width / (2 * maze.width) + balancer.padding
    u = v[1] * height / maze.height - height / (2 * maze.height) + balancer.padding

    return (t, u)

def to_vertex(maze, balancer, coord):
    """Return the corresponding vertex in the maze to the given touchscreen coordinates."""

    vertex_width = balancer.width / maze.width
    vertex_height = balancer.height / maze.height

    x = coord[0] / vertex_width + 1
    y = coord[1] / vertex_height + 1

    return (x, y)

def distance(coord1, coord2):
    (t1, u1) = coord1
    (t2, u2) = coord2
    return max(abs(t1 - t2), abs(u1 - u2))

if __name__ == "__main__":
    pass
    #m = detect_maze();
    #path = m.bfs((1, 3), (7, 3))

    # run(path, m)