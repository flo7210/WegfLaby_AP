class Maze:
    """A representation of a maze as a rectangular graph."""

    def __init__(self, width, height):
        """Initializes a new instance of the Maze class with given width and height."""

        self.width = width
        self.height = height
        self.reachable = dict()

        # Initialize self.reachable
        for x in xrange(1, width):
            for y in xrange(1, height):
                self.reachable[(x, y)] = set()

    def has_vertex(self, x, y):
        """Returns whether the given vertex coordinates is on the graph or not."""

        return min(x, y) > 0 and x <= self.width and y <= self.height

    def get_neighbors(self, x, y):
        """Returns the neighbors of the vertex given by x and y on the rectangle."""

        if not self.has_vertex(x, y): return []
        neighbors = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
        return [v for v in neighbors if self.has_vertex(v[0], v[1])]

    def get_reachable_neighbors(self, x, y):
        """Returns a list of reachable neighbors of the vertex given by x and y in the maze."""

        return [v for v in self.get_neighbors(x, y) if v in self.reachable[(x, y)]]