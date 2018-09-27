from random import randint
import copy

# Contains two switches that are connected, used by Topology to keep track of
# which switches are connected to each other.
class Link(object):
	switch1 = None
	switch2 = None
	def __init__(self, switch1, switch2):
		super(Link, self).__init__()
		self.switch1 = switch1
		self.switch2 = switch2
