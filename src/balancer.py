from serial import Serial

class Balancer:
    """An Python interface class to the balancer."""

    def __init__(self, serial, width = 580, height = 580, padding = 25):
        """Initialize a new instance of the Balancer class."""

        self.response_handler = None
        self.serial = serial
        self.width = width
        self.height = height
        self.padding = padding

        self.command_queue = []
            
    def start_listening(self):
        """Start listening for responses and handle them."""

        while len(self.command_queue) > 0:
            # Get command
            (t, u) = self.command_queue.pop(0)
            self.send_command(t, u)

            while True:
                response = self.read_response()

                if self.response_handler is not None:
                    self.response_handler((t, u), response)

                # Break loop if ball is balanced
                if response[0]: break

    def add_command(self, t, u):
        """Add a command to the command queue"""
        self.command_queue.append((t, u))

    def send_command(self, t, u):
        """Send a command to direct the ball to the given touchscreen coordinates and start listening."""
        self.serial.write(str(t).zfill(3) + ',' + str(u).zfill(3))

    def read_response(self):
        """Read a response from the balancer."""
        response = self.serial.read(8)

        balanced = response[0] == '='
        t = int(response[1:4])
        u = int(response[-3:])

        return (balanced, t, u)
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.serial.close();