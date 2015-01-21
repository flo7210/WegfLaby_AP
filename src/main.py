from maze import Maze
from balancer import Balancer
from serial import Serial
import time
import math

def run(path, maze):
    with Balancer(Serial(0)) as balancer:
        def response_handler(destination, response):
            (balanced, t, u) = response

            if balanced and distance(destination, (t, u)) < 15:
                # We are balanced and in the right place
                print(maze.print_path(path[:response_handler.counter + 1], path[-1:]))
                print
                
                # Skip over skippables
                if response_handler.counter + 1 >= len(path): return

                skippables = maze.get_skippables(path)
                while True:
                    response_handler.counter += 1
                    if response_handler.counter not in skippables: break

                # Add new command
                (t, u) = to_touchscreen_coord(maze, balancer, path[response_handler.counter])
                print (t, u)
                print
                balancer.add_command(t, u)
            elif balanced:
                # If we're not in the right place, run old command again
                (t, u) = destination
                balancer.add_command(t, u)
        
        # Add first command
        response_handler.counter = -1
        response_handler((0, 0), (True, 0, 0))

        # Start listening
        balancer.response_handler = response_handler
        balancer.start_listening()
    
def detect_maze():
    m = Maze(7, 5)
    m.add_path([(1, 3), (1, 2), (1, 1), (2, 1), (1, 1), (1, 2), (2, 2), (2, 3), 
                (3, 3), (3, 2), (3, 1), 
                (4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (5, 1), (5, 2), (6, 2), 
                (6, 3), (5, 3), 
                (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (4, 4), (4, 5), (5, 5), 
                (4, 5), (3, 5), (2, 5), (1, 5), (1, 4), (2, 4),
                (4, 4), (5, 4), (6, 4), (6, 5), (7, 5), (7, 4), (7, 3)])

    return m

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
    m = detect_maze();
    path = m.bfs((1, 3), (7, 3))

    run(path, m)