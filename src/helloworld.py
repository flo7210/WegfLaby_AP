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

n = Maze(5, 4)
n.add_path([(1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (5, 2), (5, 3), (5, 4),
            (4, 4), (3, 4), (2, 4), (1, 4),
            (1, 3), (1, 2), (1, 1)])

print(m)
print(m.bfs((1, 2), (5, 3)))
print('')
print(n)
print(n.bfs((1, 2), (5, 3)))