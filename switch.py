from random import randint
import copy

# Represents a top-of-rack switch, which has a certain number of ports, some of
# which connect to the servers in this rack and some of which connect to the
# rest of the network
class Switch(object):
	def __init__(self, portNum, rackHeight, id):
		super(Switch, self).__init__()
		self.portNum = portNum
		self.freePortNum = portNum - rackHeight
		self.id = id
		self.connections = []
		self.forwardingTable = {};

	def connectTo(self, other):
		if len(self.connections) == self.freePortNum:
			return False
		self.connections.append(other)
		return True

	def disconnectFrom(self, other):
		self.connections.remove(other)
