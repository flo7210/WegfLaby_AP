class Maze:
    """A representation of a maze as a rectangular graph."""

    def __init__(self, width, height):
        """Initializes a new instance of the Maze class with given width and height."""

        self.width = width
        self.height = height
        self._reachable = dict()

        # Initialize self._reachable
        for x in xrange(1, width + 1):
            for y in xrange(1, height + 1):
                self._reachable[(x, y)] = set()

    def has_vertex(self, x, y):
        """Returns whether the given vertex coordinates is on the graph or not."""

        return min(x, y) > 0 and x <= self.width and y <= self.height

    def get_neighbors(self, x, y):
        """Returns the neighbors of the vertex given by x and y on the rectangle."""

        if not self.has_vertex(x, y): return []
        neighbors = [(x + 1, y), (x, y - 1), (x, y + 1), (x - 1, y)]
        return [(x, y) for (x, y) in neighbors if self.has_vertex(x, y)]

    def get_reachable_neighbors(self, x, y):
        """Returns a set of reachable neighbors of the given vertex in the maze."""

        return self._reachable[(x, y)]
    
    def add_edge(self, v1, v2):
        """Adds an edge between vertices v1 and v2 to indicate that they are reachable."""

        (x1, y1) = v1
        (x2, y2) = v2

        if not self.has_vertex(x1, y1) or not self.has_vertex(x2, y2): return
        if v1 not in self.get_neighbors(x2, y2): return

        self._reachable[v1].add(v2)
        self._reachable[v2].add(v1)

    def add_path(self, path):
        """Adds edges along the given path."""

        for i in range(1, len(path)):
            self.add_edge(path[i], path[i - 1])

    def bfs(self, start, end):
        """Performs a breadth-first search and returns an optimal path from start to end."""

        queue = [start]
        parent = dict()

        # Initialize parent dictionary
        for v in iter(self._reachable): parent[v] = None
        parent[start] = start

        while len(queue) > 0:
            (x, y) = queue.pop(0)
            if (x, y) == end: break

            for v in self.get_reachable_neighbors(x, y):
                if parent[v] is not None: 
                    # Vertex v already visited
                    continue
                parent[v] = (x, y)
                queue.append(v)

        # Reconstruct path
        path = [end]
        vertex = end

        while parent[vertex] != vertex:
            if parent[vertex] is None: return []
            path.append(parent[vertex])
            vertex = parent[vertex]

        path.reverse()
        return path
    
    def __repr__(self):
        """Returns a string that represents the current maze."""

        result = ''

        for y in xrange(1, self.height + 1):
            for x in xrange(1, self.width + 1):
                # Draw top line
                if (x, y - 1) in self.get_reachable_neighbors(x, y):
                    result += '+  '
                else: result += '+--'

            result += '+\n'

            for x in xrange(1, self.width + 1):
                # Draw horizontal passage
                if (x - 1, y) in self.get_reachable_neighbors(x, y):
                    result += '   '
                else: result += '|  '

            result += '|\n'

            if y == self.height:
                for x in xrange(1, self.width + 1):
                    # Draw bottom line
                    result += '+--'

        return result + '+'