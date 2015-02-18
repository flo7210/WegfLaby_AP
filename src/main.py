from maze import Maze
from balancer import Balancer
from serial import Serial

def to_touchscreen_coord(maze, balancer, v):
    """Return the corresponding touchscreen coordinates to the given vertex in the maze."""

    width = balancer.width
    height = balancer.height

    t = v[0] * width / maze.width - width / (2 * maze.width)
    u = v[1] * height / maze.height - height / (2 * maze.height)

    return (t, u)

def to_vertex(maze, balancer, coord):
    """Return the corresponding vertex in the maze to the given touchscreen coordinates."""

    vertex_width = balancer.width / maze.width
    vertex_height = balancer.height / maze.height

    x = coord[0] / vertex_width + 1
    y = coord[1] / vertex_height + 1

    return (x, y)

def run(path, maze):
    with Balancer(Serial(0)) as balancer:
        def balance_handler(destination, response, destination_reached):
            (balanced, t, u) = response

            if destination_reached:
                # We are balanced and in the right place
                print(maze.print_path(path[:balance_handler.counter + 1], path[-1:]))
                print
                
                # Get next command and skip over skippables
                if balance_handler.counter + 1 >= len(path): return

                skippables = maze.get_skippables(path)
                while True:
                    balance_handler.counter += 1
                    if balance_handler.counter not in skippables: break

                # Add new command
                (t_new, u_new) = to_touchscreen_coord(maze, balancer, path[balance_handler.counter])
                balancer.add_command(t_new, u_new)
            else:
                # If we're not in the right place, run old command again
                (t_new, u_new) = destination
                balancer.add_command(t_new, u_new)

        # Add first command
        balance_handler.counter = -1
        balance_handler((0, 0), (True, 0, 0), True)

        # Start listening
        balancer.balance_handler = balance_handler
        balancer.start_listening()

def is_done(vertex, maze, dualmaze):
    for neighbor in maze.get_neighbors(vertex):
        if maze.has_edge(neighbor, vertex) == dualmaze.has_edge(neighbor, vertex):
            return False

    return True

def detect_walls(anchor, maze, dualmaze):
    neighbors_stack = [n for n in maze.get_neighbors(anchor[0], anchor[1]) if not is_done(n, maze, dualmaze)]

    with Balancer(Serial(0)) as balancer:
        def balance_handler(destination, response, destination_reached):
            (_, t, u) = response
            v_destination = to_vertex(maze, balancer, destination)

            if destination_reached or (v_destination != anchor and to_vertex(maze, balancer, (t, u)) == v_destination):
                # We are balanced and in the right place
                balance_handler.failcounter = 0

                if v_destination != anchor:
                    # Neighbor is reachable, add to maze
                    maze.add_edge(anchor, v_destination)

                print maze.print_path([v_destination], neighbors_stack)
                print

                if len(neighbors_stack) == 0:
                    return

                # Process neighbors stack
                neighbor = neighbors_stack.pop()
                (t_new, u_new) = to_touchscreen_coord(maze, balancer, neighbor)
                balancer.add_command(t_new, u_new)

                if neighbor != anchor:
                    # Return to anchor before moving to next neighbor
                    neighbors_stack.append(anchor)
            else:
                # We are not at the destination
                if balance_handler.failcounter < 1 or v_destination == anchor:
                    balancer.add_command(destination[0], destination[1])

                    if to_vertex(maze, balancer, (t, u)) == anchor:
                        balance_handler.failcounter += 1
                else:
                    # There is a wall between anchor and destination, add to dualmaze
                    dualmaze.add_edge(anchor, v_destination)

                    (t_new, u_new) = to_touchscreen_coord(maze, balancer, anchor)
                    balancer.add_command(t_new, u_new)

        balance_handler.failcounter = 0

        (t, u) = to_touchscreen_coord(maze, balancer, anchor)
        balancer.add_command(t, u)

        balancer.balance_handler = balance_handler
        balancer.start_listening()

def detect_maze(start, width = 7, height = 5):
    maze = Maze(width, height)
    dualmaze = Maze(width, height)

    last_vertex = start
    stack = [start]

    while len(stack) > 0:
        vertex = stack.pop()

        run(maze.bfs(last_vertex, vertex), maze)
        detect_walls(vertex, maze, dualmaze)

        print maze.print_path([], [vertex])
        print

        # Fill stack
        stack.extend([v for v in maze.get_reachables(vertex[0], vertex[1]) if not is_done(v, maze, dualmaze)])
        last_vertex = vertex

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

if __name__ == "__main__":
    m = detect_maze((1, 3))
    # path = m.bfs((1, 3), (7, 3))

    # run(path, m)
