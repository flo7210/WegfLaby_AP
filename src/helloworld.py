from __builtin__ import *
from maze import *
import serial
import time

def run_on(path, maze):
    ser = serial.Serial(0)

    for (x, y) in path:
        time.sleep(1)

        (t, u) = touchscreen_coord((x, y), maze);
        input = str(t).zfill(3) + ',' + str(u).zfill(3)

        ser.write(input)
        print(input)

        response = ser.read(2)
        print(response)

    ser.close()

def touchscreen_coord(maze_coord, maze):
    (x, y) = maze_coord;
    touchscreen_width = touchscreen_height = 530;

    t = x * touchscreen_width / maze.width - touchscreen_width / (2 * maze.width) + 25
    u = y * touchscreen_height / maze.height - touchscreen_height / (2 * maze.height) + 25

    return (t, u)


print('Hello World')

m = Maze(7, 5)
m.add_path([(1, 3), (1, 2), (1, 1), (2, 1), (1, 1), 
            (1, 2), (2, 2), (2, 3), (3, 3), (3, 2), 
            (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
            (7, 2)])
m.add_path([(5, 1), (5, 2), (6, 2), (6, 3), (5, 3)])
m.add_path([(4, 1), (4, 2), (4, 3), (4, 4), (3, 4),
            (4, 4), (4, 5), (5, 5), (4, 5), (3, 5), 
            (2, 5), (1, 5), (1, 4), (2, 4)])
m.add_path([(4, 4), (5, 4), (6, 4), (6, 5), (7, 5),
            (7, 4), (7, 3)])

path = m.bfs((1, 3), (7, 3))

print(m)
print(m.__repr__(path))

run_on(path, m)