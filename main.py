from random import randint
from topology import Topology
from link import Link
from switch import Switch
from time import localtime, strftime
import copy
import argparse
import threading
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
from algorithms import createFigure9



def args():
	parser = argparse.ArgumentParser(description='This is a program to recreate the figure 9 in the Jellyfish paper.')
	parser.add_argument( '-n', '--netSize', type=int, default=20, help='This is the size of network or the number of servers, default value of this parameter is 686.' )
	parser.add_argument( '-s', '--switchSize', type=int, default=16, help='This is the size of the switch or the number of ports on the switch, default value of this parameter is 24.' )
	parser.add_argument( '-r', '--rackHeight', type=int, default=5, help='This is the height of the rack, default value of this parameter is 5.' )
	parser.add_argument( '-i', '--it', type=int, default=1, help='This is the number of iterations (number of networks) you want to run to analyze the network properties, default value of this parameter is 1' )
	parser.add_argument( '-t', '--threads', type=int, default=5, help='This is the number of threads to run in computation, default value is set to 5' )
	parser.add_argument( '-a', '--analysis', type=bool, default=False, help='If this argument is set run the network analysis. Leave blank if you only want to run recreating figure 9' )
	parser.add_argument( '-f', '--forward', type=bool, default=False, help='If this argument is set forward all standard outputs to log.txt file' )
	return parser.parse_args()

def dijsktra( graph, startNode, visited ):
	allNodes = set(graph.link_d.keys())
	currNodes = graph.link_d[startNode]
	currHops = 1
	while set(visited.keys()).symmetric_difference(allNodes):
		nextNodes = []
		for i in currNodes:
			if i not in visited:
				visited[i] = currHops
			else:
				if currHops < visited[i]:
					visited[i] = currHops
			nextNodes += copy.copy(graph.link_d[i]) # very important to make a shallow copy of the list
		currHops += 1
		currNodes = copy.copy(nextNodes)

#def dijsktra_with_path( graph, startNode ):
#after running dijsktra get the path
def getNHopsAway( link, nextNode, index, paths, n ):
	if len(paths[index].split('*')) > n:
		return
	else:
		for i in link[nextNode]:
			if str(i) not in paths[index].split('*'):
				paths.append( paths[index] + '*' + str(i) )
				getNHopsAway( link, i, len(paths)-1, paths, n )

def getShortestPaths( graph, startNode, endNode, shortest ):
	paths = []
	paths.append(str(startNode))
	getNHopsAway( graph.link_d, startNode, 0, paths, shortest )
	result = []
	for i in paths:
		if int(i.split('*')[-1]) == endNode:
			result.append(i)
	return result

#return the dictionary key with that value
def getKey( dic, val ):
	for i in dic:
		if dic[i] == val:
			return i
	return -1

def getDiameter( graph, numThreads ):
	diameter = -1
	index = 0
	allNodes = graph.link_d.keys()
	allShortestPaths = {}
	while( index < len(allNodes) ):
		threads = []
		results = []
		for i in range( numThreads ):
			vt = { allNodes[index]: 0 }
			results.append(copy.copy(vt))
			t = threading.Thread(target=dijsktra, args=(graph, allNodes[index], results[i]))
			threads.append(t)
			t.start()
			index += 1
			if index > len(allNodes) - 1:
				break
		for i in range(len(threads)):
			threads[i].join()
			shortest = max(results[i].values()) - 1
			allShortestPaths[getKey(results[i],0)] = results[i]
			if shortest > diameter:
				diameter = shortest
	return diameter, allShortestPaths

def getAvgShortestPaths( shortestPaths ):
	visited = set()
	sumShortestPaths = 0.0
	lenShortestPaths = 0.0
	for i in shortestPaths:
		for j in shortestPaths[i]:
			if i == j:
				continue
			pair = str(min(i,j))+ '*' + str(max(i,j))
			if pair in visited:
				continue
			visited.add(pair)
			sumShortestPaths += int(shortestPaths[i][j])
			lenShortestPaths += 1
	return sumShortestPaths/lenShortestPaths

def passNode( node, paths ):
	count = 0
	for i in paths:
		if str(node) in i.split('*'):
			count += 1
	return count

def getBetweenness( node, mappings, allNodes ):
	betwc = 0.0
	for i in allNodes:
		for j in allNodes:
			if not (i == j or i == node or j == node):
				s = min(i,j)
				l = max(i,j)
				if s in mappings and l in mappings[s]:
					betwc += float(passNode( node, mappings[s][l] ))/float(len(mappings[s][l]))
	return betwc

def getNeighborsEdges( graph, n ):
	count = 0
	for i in n:
		count += len(set(n).intersection(set(graph.link_d[i])))
	return count/2 #double counted

def getTriplets( graph ):
	return_set = set()
	for i in graph:
		for j in graph[i]:
			for k in graph[j]:
				if not i == k:
					s = min(i, k)
					l = max(i, k)
					return_set.add(str(s) + '*' + str(j) + '*' + str(l)) #j is always in the middle
	return return_set

def getGlobalClusc( graph, triplets ):
	closed = 0.0
	for i in triplets:
		edge1 = int(i.split('*')[0])
		edge2 = int(i.split('*')[-1])
		if edge2 in graph[edge1]:
			closed += 1
	return closed/float(len(triplets))

def getCurrTime():
	return strftime("%a, %d %b %Y %H:%M:%S", localtime())

def makeTopology( t, netSize ):
	failed = 0
	while failed < netSize:
		if not t.connect(randint(0, netSize - 1), randint(0, netSize - 1)):
			failed = failed + 1
		else:
			failed = 0

def plotDot( x, y, output, color ):
	plt.plot( x, y, color )
	plt.xlabel( "iterations" )
	plt.ylabel( "values" )
	plt.title( output )
	plt.axis( [min(x) - 1, max(x) + 1, 0, max(y) + ((max(y)-min(y)/len(y)))] )
	plt.savefig(output +".png")
	plt.close()

## making a color map of N distinct colors
## from https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib
def get_cmap(N):
	color_norm  = colors.Normalize(vmin=0, vmax=N-1)
	scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')
    	def map_index_to_rgb_color(index):
        	return scalar_map.to_rgba(index)
    	return map_index_to_rgb_color

def plotHistogram( n, y, max_v, output ):
	plt.figure()
	cmap = get_cmap( n + 1)
	l = []
	c = []
	ticks = []
	size = round(float(max_v) / 10.0 , 2)
	offset = round(size / 2, 2)
	for i in range( 10 ):
		ticks.append(offset + (i *size))
	for i in range( n ):
		c.append(cmap(i))
		l.append("network%d" %(i+1))
	plt.hist(y, 10, histtype='bar', color=c, label=l)
	plt.legend()
	plt.xticks(ticks)
	plt.xlabel("bins")
	plt.ylabel("values")
	plt.title( output )
	plt.savefig(output + ".png")
	plt.close()

def makeFullClique( graph ):
	keys = graph.link_d.keys()
	full = {}
	for i in keys:
		for j in keys:
			if not i == j:
				if i not in full:
					full[i] = set()
				full[i].add(j)
				if j not in full:
					full[j] = set()
				full[j].add(i)
	return full


def main():
	a = args()
	if a.forward:
		sys.stdout = open( 'log.txt', 'w' )
	print("Starting JellyFish Project\nStarting time is: %s\n" %(getCurrTime()))
	print("Step 1 Recreate Figure 1: %s" %(getCurrTime()))
	# Simple methodology: keep adding random links until netSize fail consecutively,
	# then it's probably full
	print("Generating a random network: %s" %(getCurrTime()))
	topology = Topology(a.switchSize, a.rackHeight, a.netSize/a.rackHeight);
	makeTopology( topology, a.netSize/a.rackHeight )
	print("Finished generating a random network, starting k-shortest path: %s" %(getCurrTime()))
	createFigure9(topology);

	print("Finished step 1: %s\n" %(getCurrTime()))

	if a.analysis:

		print("Step 2 Analyzing random networks, generating %d random network(s): %s\n" %(a.it, getCurrTime()))
		topologies = []
		for i in range( a.it ):
			topologies.append(Topology(a.switchSize, a.rackHeight, a.netSize))
			makeTopology( topologies[i], a.netSize )

		print("Finished generating %d random networks, starting calculating global clustering coefficients of the networks: %s" %(a.it, getCurrTime()))

		## GLOBAL CLUSTERING COEFFICIENT ##
		# number of closed triangle / number of connected triplets
		global_cc = open( "global_clusc_results.txt", 'w' )
		x = []
		y = []
		for i in range( a.it ):
			print("\tStart network %d: %s" %(i + 1, getCurrTime()))
			triplets = getTriplets( topologies[i].link_d )
			gcc = getGlobalClusc( topologies[i].link_d, triplets )
			global_cc.write(str(i + 1) + "\t" + str(gcc) + "\n")
			x.append( i + 1 )
			y.append( gcc )
		global_cc.close()
		plotDot( x, y, "Global_CC", 'rs')

		print("Finished calculating global clustering coefficients, starting calculating local clustering coefficients of the networks: %s" %(getCurrTime()))
		## LOCAL CLUSTERING COEFFICIENT ##
		y = []
		min_v = 0 # always zero
		max_v = -1
		for i in range( a.it ):
			tempy = []
		 	cc = open( "local_clusc_%d_results.txt" %( i + 1 ), 'w' )
			print("\tStart network %d: %s" %(i + 1, getCurrTime()))
			for j in topologies[i].link_d.keys():
		 		totalN = len(topologies[i].link_d[j])
		 		if totalN < 2:
					cc.write( "%s\t%f\n" %(j, 0) )
					tempy.append(0)
		 		else:
					totalE = (totalN * (totalN -1 )) / 2
					local_cc = float(getNeighborsEdges(topologies[i], topologies[i].link_d[j]))/float(totalE)
					cc.write("%s\t%f\n"  %(j, local_cc))
					tempy.append(local_cc)
					if local_cc > max_v:
						max_v = local_cc
			y.append(copy.copy(tempy))
			cc.close()
		plotHistogram( a.it, y, max_v, "Local_CC" )

		print("Finished calculating local clustering coefficients, starting calculating diameters of the networks: %s" %(getCurrTime()))

		## DIAMETER ##
		shortestPaths = []
		#open a file to store diameter results
		dia = open( "diameter_results.txt", 'w' )
		x = []
		y = []
		for i in range( a.it ):
			print("\tStart network %d: %s" %(i + 1, getCurrTime()))
			[diameter, paths] = getDiameter(topologies[i], a.threads )
			shortestPaths.append(copy.copy(paths))
			dia.write( str(i + 1) + "\t" + str(diameter) + "\n" )
			x.append( i + 1 )
			y.append( diameter )
		dia.close()
		plotDot(x, y, "Diameter", 'go')


		## AVERAGE SHORTEST PATHS ##
		#open a file to store average shortest paths results
		avg = open( "avg_shortest_paths_results.txt", 'w' )
		x = []
		y = []
		print("Finished calculating network diameters, starting calculating average shortest paths: %s" %(getCurrTime()))
		for i in range(len(shortestPaths)):
			print("\tStart network %d: %s" %(i + 1, getCurrTime()))
			sp = getAvgShortestPaths( shortestPaths[i] )
			avg.write( str(i + 1) + "\t" + str(sp) + "\n" )
			x.append( i + 1 )
			y.append( sp )
		avg.close()
		plotDot(x, y, "Avg_Shortest_Paths", 'b^')

		print("Finished calculating average shortest paths, starting calculating betweeness centrality: %s" %(getCurrTime()))


		## BETWEENNESS CENTRALITY ##
		y = []
		min_v = 0 # always zero, because it is normalized
		max_v = -1
		for i in range(len(shortestPaths)):
			tempy = []
			print("\tStart network %d: %s" %(i + 1, getCurrTime()))
			#open a file to store betweeness results
			betwc = open( "betwc_%d_results.txt" %(i + 1), 'w' )
			visited = {}
			pathMappings = {}
			for j in shortestPaths[i]:
				for k in shortestPaths[i][j]:
					s = min(j,k)
					l = max(j,k)
					if not j == k and not( s in visited and l in visited[s]) and shortestPaths[i][j][k] > 1:
						if s not in pathMappings:
							pathMappings[s] = {}
						#gives all the shortest paths between j and k
						pathMappings[s][l] = getShortestPaths( topologies[i], j, k, shortestPaths[i][j][k])
						if s not in visited:
							visited[s] = set()
						visited[s].add(l)
			allBetweenness = {}
			for j in shortestPaths[i]:
				#not normalized yet, will normalized after all iterations
				allBetweenness[j] = getBetweenness( j, pathMappings, shortestPaths[i] )
			s = min(allBetweenness.values())
			l = max(allBetweenness.values())
			for j in allBetweenness:
				normalize = (allBetweenness[j] - s)/(l - s)
				if normalize > max_v:
					max_v = normalize
				tempy.append(normalize)
				betwc.write( "%d\t%f\n" %(j, normalize) )
			betwc.close()
			y.append(copy.copy(tempy))

		plotHistogram( a.it, y, max_v, "Betweenness" )

	if a.forward:
		sys.stdout.close()

if __name__ == "__main__":
	main()
