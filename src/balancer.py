class Balancer:
    """This class is the bridge between the balancer and Python."""

    def __init__(self, serial, width = 580, height = 580):
        """Initialize a new instance of the Balancer class."""

        self.response_handler = None
        self.balance_handler = None
        self.destination_reached = lambda dest, coord: self.distance(dest, coord) < 15
        self.serial = serial
        self.width = width
        self.height = height

        self.command_queue = []
            
    def start_listening(self):
        """Start listening for responses and handle them."""

        while len(self.command_queue) > 0:
            # Get command
            (t, u, force_reset) = self.command_queue.pop(0)
            self._send_command(t, u, force_reset)

            while True:
                response = self._read_response()
                if response is None: continue

                (balanced, tNew, uNew) = response

                # Fire handlers
                if balanced and self.balance_handler is not None:
                    self.balance_handler((t, u), response, self.destination_reached((t, u), (tNew, uNew)))
                
                if self.response_handler is not None:
                    self.response_handler((t, u), response)

                # Break loop if ball is balanced
                if balanced: break

    def add_command(self, t, u, force_reset = False):
        """Add a command to the command queue."""

        self.command_queue.append((t, u, force_reset))
    
    def distance(self, coord1, coord2):
        """Calculate the Chebyshev distance between the given coordinates."""

        (t1, u1) = coord1
        (t2, u2) = coord2
        return max(abs(t1 - t2), abs(u1 - u2))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.serial.close();

    def _send_command(self, t, u, force_reset = False):
        """Send a command to direct the ball to the given touchscreen coordinates."""

        sign = '.'
        if force_reset: sign = '!'

        self.serial.write(sign + str(t).zfill(3) + ',' + str(u).zfill(3))

    def _read_response(self):
        """Read a response from the balancer."""

        response = self.serial.read(8)
        if response[0] == '#':
            print response
            return None

        balanced = response[0] == '='
        t = int(response[1:4])
        u = int(response[-3:])

        return (balanced, t, u)