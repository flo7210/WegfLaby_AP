from maze import *
import serial
import time

def run(path, maze):
    ser = serial.Serial(0)
    i = 0

    for (x, y) in path:
        time.sleep(1)

        (t, u) = touchscreen_coord((x, y), maze);
        input = str(t).zfill(3) + ',' + str(u).zfill(3)

        ser.write(input)
        print(input)

        response = ser.read(2)
        print(response)
        print

        i += 1
        print(maze.print_path(path[:i], path[-1:]))
        print

    ser.close()

def touchscreen_coord(maze_coord, maze):
    """Returns the corresponding touchscreen coordinates to the given maze coordinates"""

    (x, y) = maze_coord;
    touchscreen_width = touchscreen_height = 530;

    t = x * touchscreen_width / maze.width - touchscreen_width / (2 * maze.width) + 25
    u = y * touchscreen_height / maze.height - touchscreen_height / (2 * maze.height) + 25

    return (t, u)

def detect_maze():
    m = Maze(7, 5)
    m.add_path([(1, 3), (1, 2), (1, 1), (2, 1), (1, 1), 
                (1, 2), (2, 2), (2, 3), (3, 3), (3, 2), 
                (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
                (7, 2), (5, 1), (5, 2), (6, 2), (6, 3), 
                (5, 3), (4, 1), (4, 2), (4, 3), (4, 4),
                (3, 4), (4, 4), (4, 5), (5, 5), (4, 5), 
                (3, 5), (2, 5), (1, 5), (1, 4), (2, 4),
                (4, 4), (5, 4), (6, 4), (6, 5), (7, 5),
                (7, 4), (7, 3)])

    return m

m = detect_maze();
path = m.bfs((1, 3), (7, 3))

print(m)
print

run(path, m)