class Maze:
    """An abstract representation of a maze as a rectangular, simple graph."""

    def __init__(self, width, height):
        """Initialize a new instance of the Maze class with given width and height."""

        self.width = width
        self.height = height
        self._reachable = dict()

        # Initialize self._reachable
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                self._reachable[(x, y)] = set()

    def has_vertex(self, x, y):
        """Return whether the given vertex coordinates is on the graph or not."""

        return min(x, y) > 0 and x <= self.width and y <= self.height

    def has_edge(self, v1, v2):
        """Return whether v1 is reachable from v2 or not."""

        return v1 in self.get_reachables(v2[0], v2[1])

    def get_neighbors(self, x, y):
        """Return the neighbors of the vertex given by x and y on the rectangle."""

        if not self.has_vertex(x, y): return []
        neighbors = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        return [(x, y) for (x, y) in neighbors if self.has_vertex(x, y)]

    def get_reachables(self, x, y):
        """Return a set of reachable neighbors of the given vertex in the maze."""

        return [v for v in self.get_neighbors(x, y) if v in self._reachable[(x, y)]]
    
    def add_edge(self, v1, v2):
        """Add an edge between vertices v1 and v2 to indicate that they are reachable."""

        (x1, y1) = v1
        (x2, y2) = v2

        if not self.has_vertex(x1, y1) or not self.has_vertex(x2, y2): return
        if v1 not in self.get_neighbors(x2, y2): return

        self._reachable[v1].add(v2)
        self._reachable[v2].add(v1)

    def add_path(self, path):
        """Add edges along the given path."""

        for i in range(1, len(path)):
            self.add_edge(path[i], path[i - 1])

    def bfs(self, start, end):
        """Perform a breadth-first search and return an optimal path from start to end."""

        queue = [start]
        parent = dict()

        # Initialize parent dictionary
        for v in iter(self._reachable): parent[v] = None
        parent[start] = start

        while len(queue) > 0:
            (x, y) = queue.pop(0)
            if (x, y) == end: break

            for v in self.get_reachables(x, y):
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

    def get_skippables(self, path):
        """Return a list of vertices in the given path that can be skipped."""

        skippables = []
        anchor = path[0]

        for i in range(2, len(path)):
            (x, y) = path[i]

            if x == anchor[0] or y == anchor[1]:
                skippables.append(i - 1)
            else:
                anchor = path[i - 1]

        return skippables

    def parse(self, string):
        """Add edges according to the given string representation of a maze."""

        lines = string.splitlines()
        width = int((len(lines[0]) - 1) / 3)
        height = int((len(lines) - 1) / 2)
        self.__init__(width, height)

        y = 1
        for i in range(1, len(lines) - 1):
            line = lines[i]

            for j in range(1, len(line) - 1):
                if line[0] == '+':
                    # Detect vertical edges
                    if j % 3 != 1 or line[j] != ' ': continue
                    x = int((j + 2) / 3)

                    self.add_edge((x, y - 1), (x, y))
                else:
                    # Detect horizontal edges
                    if j % 3 != 0 or line[j] != ' ': continue
                    x = int(j / 3)

                    self.add_edge((x, y), (x + 1, y))

            if line[0] != '+': y += 1

        return self

    def print_path(self, path, marks = []):
        """Return a string that represents the current maze with the given path."""

        result = ''

        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                # Draw top line
                if (x, y - 1) in self.get_reachables(x, y):
                    result += '+  '
                else: result += '+--'

            result += '+\n'

            for x in range(1, self.width + 1):
                # Draw horizontal passage
                if (x - 1, y) in self.get_reachables(x, y):
                    result += ' '
                else: result += '|'


                if (x, y) in path:
                    if (x, y) in path[-1:]:
                        result += '(X'
                    else: result += ' x'
                elif (x, y) in marks:
                    result += ' #'
                else: result += '  '

            result += '|\n'

            if y == self.height:
                for x in range(1, self.width + 1):
                    # Draw bottom line
                    result += '+--'

        return result + '+'

    def __repr__(self):
        """Return a string that represents the current maze."""

        return self.print_path([]);