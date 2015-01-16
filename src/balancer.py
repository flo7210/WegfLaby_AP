from serial import Serial

class Balancer:
    """An Python interface class to the balancer."""

    def __init__(self, serial, width = 580, height = 580, padding = 25):
        """Initialize a new instance of the Balancer class."""

        self.serial = serial
        self.width = width
        self.height = height
        self.padding = padding

    def to_touchscreen_coord(self, maze_coord, maze):
        """Return the corresponding touchscreen coordinates to the given maze coordinates."""

        (x, y) = maze_coord

        width = self.width - 2 * self.padding
        height = self.height - 2 * self.padding

        t = x * width / maze.width - width / (2 * maze.width) + self.padding
        u = y * height / maze.height - height / (2 * maze.height) + self.padding

        return (t, u)
