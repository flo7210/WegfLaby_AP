from maze import *

print('Hello World')

m = Maze(5, 4)
m.add_edge((1, 2), (2, 2))
m.add_edge((2, 2), (2, 3))
m.add_edge((2, 3), (3, 3))
m.add_edge((3, 3), (4, 3))
m.add_edge((4, 3), (5, 3))
m.add_edge((4, 3), (4, 2))
m.add_edge((4, 2), (4, 1))
m.add_edge((2, 4), (2, 3))

print(m)