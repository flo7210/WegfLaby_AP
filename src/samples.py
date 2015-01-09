from __builtin__ import *
from maze import Maze
import main

print("The maze:")
m = Maze(7, 5)
m.add_path([(1, 3), (1, 2), (1, 1), (2, 1), (1, 1), (1, 2), (2, 2), (2, 3), 
            (3, 3), (3, 2), (3, 1), 
            (4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (5, 1), (5, 2), (6, 2), 
            (6, 3), (5, 3), 
            (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (4, 4), (4, 5), (5, 5), 
            (4, 5), (3, 5), (2, 5), (1, 5), (1, 4), (2, 4),
            (4, 4), (5, 4), (6, 4), (6, 5), (7, 5), (7, 4), (7, 3)])
print(m)
print

print("Calculate shortest route:")
path = m.bfs((1, 3), (7, 3))
print(m.print_path(path))
print

print("Get skippables:")
skippables = main.get_skippables(path)
print(m.print_path([], skippables))
print