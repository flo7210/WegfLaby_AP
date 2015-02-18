from maze import Maze
from balancer import Balancer
from serial import Serial

with Balancer(Serial(0)) as balancer:
	for i in range(100):
		balancer.add_command(balancer.width / 2, balancer.height / 2)

	balancer.start_listening()