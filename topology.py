from random import randint
from switch import Switch
from link import Link
import copy

# The Jellyfish paper made a few simplifying assumptions in their measurements:
# They assumed all switches had the same number of ports and all links had the
# same capacity/speed

# Topoloy is a generic collections of switches and links. It maintains a all
# the connections and makes it easy to add more. The Switches also maintain
# their individual connections to make it easier to manage
class Topology(object):
	def __init__(self, switchSize, rackHeight, switchNum):
		super(Topology, self).__init__()
		self.switchSize = switchSize
		self.rackHeight = rackHeight
		self.switchNum = switchNum
		self.switches = []
		self.links = []
		self.link_d = {}
		for i in range(switchNum):
			self.switches.append(Switch(switchSize, rackHeight, i))

	# switch1 and switch2 are indices into the switches array
	def connect(self, switch1, switch2):
		success = self.switches[switch1].connectTo(self.switches[switch2])
		if success:
			success = self.switches[switch2].connectTo(self.switches[switch1])
			self.links.append(Link(switch1, switch2))
			if switch1 not in self.link_d:
				self.link_d[switch1] = []
			self.link_d[switch1].append(switch2)
			if switch2 not in self.link_d:
				self.link_d[switch2] = []
			self.link_d[switch2].append(switch1)
		return success

	# switch1 and switch2 are indices into the switches array
	def disconnect(self, switch1, switch2):
		self.switches[switch1].disconnectFrom(self.switches[switch2])
		self.switches[switch2].disconnectFrom(self.switches[switch1])
		links.remove(Link(switch1, switch2)) # TODO verify that this works

	def printSelf(self):
		print ("Topology with size:", self.switchNum, \
			"Ports/Switch:", self.switchSize, \
			"Rack Height:", self.rackHeight)
		print ("Links:", len(self.links))

	def printEdgeList(self):
		for i in range(len(self.links)):
			print ("%d\t%d" %(self.links[i].switch1, self.links[i].switch2))


