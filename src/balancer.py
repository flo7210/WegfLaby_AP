from maze import Maze
from serial import Serial

class Balancer:
    """An Python interface class to the balancer."""

    def __init__(self, serial, response_handler, width = 580, height = 580, padding = 25):
        """Initialize a new instance of the Balancer class."""

        self.serial = serial
        self.response_handler = response_handler
        self.width = width
        self.height = height
        self.padding = padding

        self.command_queue = []
            
    def start_listening(self):
        """Start listening for responses and handle them."""

        while True:
            response = self.read_response()
            self.response_handler(self, response)

            # Break loop if ball is balanced
            if response[0]: break

        if len(self.command_queue) > 1:
            (t, u) = self.command_queue.pop(0)
            self.send_command(t, u)

    def send_command(self, t, u):
        """Send a command to direct the ball to the given touchscreen coordinates and start listening."""
        self.serial.write(str(t).zfill(3) + ',' + str(u).zfill(3))
        self.start_listening()

    def read_response(self):
        """Read a response from the balancer."""
        response = self.serial.read(8)

        balanced = response[0] == '='
        t = int(response[1:3])
        u = int(response[5:3])

        return (balanced, t, u)

    def to_touchscreen_coord(self, v, maze):
        """Return the corresponding touchscreen coordinates to the given vertex in the maze."""

        width = self.width - 2 * self.padding
        height = self.height - 2 * self.padding

        t = v[0] * width / maze.width - width / (2 * maze.width) + self.padding
        u = v[1] * height / maze.height - height / (2 * maze.height) + self.padding

        return (t, u)
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.serial.close();