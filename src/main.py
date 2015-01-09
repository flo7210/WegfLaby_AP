from __builtin__ import *
from maze import Maze
from serial import Serial
import time

def run(path, maze):
    ser = Serial(0)
    skippables = get_skippables(path);

    for i in range(len(path)):
        if path[i] in skippables: continue
        time.sleep(1)

        # Send command `[x-coord],[y-coord]`
        (t, u) = touchscreen_coord(path[i], maze)
        input = str(t).zfill(3) + ',' + str(u).zfill(3)

        ser.write(input)
        print(input)

        # Get response `=[id]`
        response = ser.read(2)
        print(response)
        print

        if response[1] == '2':
            print('Something went wrong.');
            break;

        print(maze.print_path(path[:i+1], path[-1:]))
        print

    ser.close()

def get_skippables(path):
    """Return a list of vertices in the given path that can be skipped."""

    skippables = []
    anchor = path[0]

    for i in range(2, len(path)):
        (x, y) = path[i]

        if x == anchor[0] or y == anchor[1]:
            skippables.append(path[i - 1])
        else:
            anchor = path[i - 1]

    return skippables

def touchscreen_coord(maze_coord, maze):
    """Return the corresponding touchscreen coordinates to the given maze coordinates."""

    (x, y) = maze_coord;
    touchscreen_width = touchscreen_height = 530;

    t = x * touchscreen_width / maze.width - touchscreen_width / (2 * maze.width) + 25
    u = y * touchscreen_height / maze.height - touchscreen_height / (2 * maze.height) + 25

    return (t, u)

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

if __name__ == "__main__":
    m = detect_maze();
    path = m.bfs((1, 3), (7, 3))

    print(m)
    print

    run(path, m)