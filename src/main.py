from maze import Maze
from balancer import Balancer
from serial import Serial

def to_touchscreen_coord(maze, balancer, v):
    """Return the corresponding touchscreen coordinates to the given vertex in the maze."""

    width = balancer.width - balancer.padding * 2
    height = balancer.height - balancer.padding * 2

    t = balancer.padding + v[0] * width / maze.width - width / (2 * maze.width)
    u = balancer.padding + v[1] * height / maze.height - height / (2 * maze.height)

    return (t, u)

def to_vertex(maze, balancer, coord):
    """Return the corresponding vertex in the maze to the given touchscreen coordinates."""

    vertex_width = balancer.width / maze.width
    vertex_height = balancer.height / maze.height

    x = coord[0] / vertex_width + 1
    y = coord[1] / vertex_height + 1

    return (x, y)

def run(path, maze):
    if len(path) == 0: return

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
    for neighbor in maze.get_neighbors(*vertex):
        if maze.has_edge(neighbor, vertex) == dualmaze.has_edge(neighbor, vertex):
            return False

    return True

def detect_walls(anchor, maze, dualmaze):
    neighbors_stack = [n for n in maze.get_neighbors(*anchor) if not is_done(n, maze, dualmaze)]

    with Balancer(Serial(0)) as balancer:
        def balance_handler(destination, response, destination_reached):
            (_, t, u) = response
            v_destination = to_vertex(maze, balancer, destination)

            if destination_reached:
                # We are balanced and in the right place
                balance_handler.failcounter = 0

                if v_destination != anchor:
                    # Neighbor is reachable, add to maze
                    maze.add_edge(anchor, v_destination)

                print maze.print_path([v_destination], neighbors_stack)
                print

                if len(neighbors_stack) == 0:
                    balance_handler.last_vertex = v_destination
                    return

                if v_destination != anchor:
                    # Return to anchor before moving to next neighbor
                    balancer.add_command(*to_touchscreen_coord(maze, balancer, anchor))
                else:
                    # Process neighbors stack
                    neighbor = neighbors_stack.pop()
                    balancer.add_command(*to_touchscreen_coord(maze, balancer, neighbor))

            else:
                # We are not at the destination
                if balance_handler.failcounter < 1 or v_destination == anchor:
                    balancer.add_command(*destination)

                    if to_vertex(maze, balancer, (t, u)) == anchor:
                        balance_handler.failcounter += 1
                else:
                    # There is a wall between anchor and destination, add to dualmaze
                    dualmaze.add_edge(anchor, v_destination)

                    (t_new, u_new) = to_touchscreen_coord(maze, balancer, anchor)
                    balancer.add_command(t_new, u_new, True)

        balance_handler.failcounter = 0
        balance_handler.last_vertex = anchor

        (t, u) = to_touchscreen_coord(maze, balancer, anchor)
        balancer.add_command(t, u)

        balancer.balance_handler = balance_handler
        balancer.start_listening()

        return balance_handler.last_vertex

def detect_maze(start, width, height):
    maze = Maze(width, height)
    dualmaze = Maze(width, height)

    last_vertex = start
    stack = [start]

    while len(stack) > 0:
        vertex = stack.pop()
        if is_done(vertex, maze, dualmaze): continue

        if vertex != last_vertex: run(maze.bfs(last_vertex, vertex), maze)
        last_vertex = detect_walls(vertex, maze, dualmaze)

        # Fill stack; avoid unnecessary paths
        stack.extend([v for v in maze.get_reachables(*vertex) if v != last_vertex and not is_done(v, maze, dualmaze)])
        if vertex != last_vertex: stack.append(last_vertex)

    return maze

if __name__ == "__main__":
    m = Maze(1, 1)

    answer = ''
    while answer.upper() not in ['A', 'B']:
        answer = raw_input('Detect new maze (A) or read existing .maze file (B)? ')

    if answer.upper() == 'A':
        width = int(raw_input('Width: '))
        height = int(raw_input('Height: '))

        # Find nearest vertex to begin with
        with Balancer(Serial(0)) as balancer:
            def balance_handler(destination, response, destination_reached):
                (_, t, u) = response

                # Do this the first time only
                if balance_handler.position == (-1, -1):
                    balance_handler.position = (t, u)
                    balancer.add_command(t, u, True)

            balance_handler.position = (-1, -1)

            balancer.add_command(290, 290)
            balancer.balance_handler = balance_handler
            balancer.start_listening()

            start = to_vertex(Maze(width, height), balancer, balance_handler.position)
            m = detect_maze(start, width, height)
            print('Maze detected!')

        name = raw_input('File name (w/o extension): ')
        with open(name + '.maze', 'w') as f:
            f.write(repr(m))
        print ('String representation saved.')

    elif answer.upper() == 'B':
        name = raw_input('File name (w/o extension): ')
        with open(name + '.maze', 'r') as f:
            s = f.read()
            m.parse(s)

        start = raw_input('Starting point (input format is "x,y"): ')
        finish = raw_input('Finish (input format is "x,y"): ')

        s = start.partition(',')
        f = finish.partition(',')

        a = (int(s[0]), int(s[2]))
        b = (int(f[0]), int(f[2]))

        print('Please place the ball near ' + repr(a))

        path = m.bfs(a, b)
        run(path, m)
