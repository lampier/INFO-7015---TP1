import os
from collections import defaultdict
import matplotlib.pyplot as plt
import operator;

inf = 100000000;

# Find the shortest path from src to dest in topology, returns a list of the
# node #s to visit starting with src and ending with dest. src and dest should
# be the index of the nodes we want to find the path between, not the nodes
# themselves. exclude is the set of paths to exclude. Uses Dijsktra
def shortestPath(topology, src, dest, link_excludes, node_excludes):
    # Required data structures
    distances = []; # Distance for each node
    visited = []; # Whether each node has been visited
    parent = []; # Id of each node's parent in shortest path
    unvisited = set();
    current = src;

    # Init data structures
    for i in range(topology.switchNum):
        distances.append(inf);
        visited.append(False);
        parent.append(-1);
        unvisited.add(i);
    distances[src] = 0;

    while current != dest and current != -1:
        if not current in node_excludes:
            for neighbor in topology.switches[current].connections:
                if (current, neighbor.id) in link_excludes:
                    continue;
                if distances[current] + 1 < distances[neighbor.id]:
                    distances[neighbor.id] = distances[current] + 1;
                    parent[neighbor.id] = current;
        visited[current] = True;
        unvisited.remove(current);
        current = closestUnvisitedId(unvisited, distances);

    path = []
    while current != -1:
        path.append(current);
        current = parent[current];
    return path[::-1];

# Helper method for Dijsktra shortestPath
def closestUnvisitedId(unvisited, distances):
    minId = -1;
    minDist = inf;
    for nodeId in unvisited:
        if (distances[nodeId] < minDist):
            minId = nodeId;
            minDist = distances[nodeId];
    return minId;

# For this we use Yen's Algorithm https://en.wikipedia.org/wiki/Yen%27s_algorithm
def kShortestPaths(topology, src, dest, K):
    A = [];
    B = set();
    link_excludes = set();
    node_excludes = set();
    A.append(shortestPath(topology, src, dest, link_excludes, node_excludes));
    for k in range(1, K):
        for i in range(len(A[k-1])-1):
            spurNode = A[k-1][i];
            rootPath = A[k-1][0:i];
            for p in A:
                if rootPath == p[0:i] and i < len(p) - 1:
                    link_excludes.add((p[i], p[i+1]));
                    link_excludes.add((p[i+1], p[i]));
                for node in p:
                    if node != spurNode:
                        node_excludes.add(node);
            spurPath = shortestPath(topology, spurNode, dest, link_excludes, node_excludes);
            if not spurPath == []:
                B.add(tuple(rootPath + spurPath));
            link_excludes.clear();
            node_excludes.clear();
        if B == set():
           break;
        shortest = findShortest(B);
        A.append(list(shortest));
        B.remove(shortest);
    return A;

# Helper method for kShortestPaths
def findShortest(B):
    shortest = [];
    for path in B:
        if len(path) < len(shortest) or shortest == []:
            shortest = path;
    return shortest;

# Figure 9 in the Jellyfish paper evaluates the number of shortest paths each
# individual link is part of, ranking from least to most to generate the
# increasing step function.
def createFigure9(topology):
    k_8 = set();
    e_8 = set();
    e_64 = set();
    for i in range(topology.switchNum):
        # Since connections are random, having server N send data to N+1+k
        # will pick a random path to k switches, makes it easier.
        for k in range(topology.rackHeight):
            ks = kShortestPaths(topology, i, (i+k+1) % topology.switchNum, 64);
            k_8.update(maxLength(ks, 8));
            e_8.update(firstMaxEqual(ks, 8));
            e_64.update(firstMaxEqual(ks, 64));
    print "Created Sets"
    k_8m = timesInSet(k_8);
    e_8m = timesInSet(e_8);
    e_64m = timesInSet(e_64);
    print "Counted paths p1"
    k_8_points = genGraphPoints(topology, k_8m);
    e_8_points = genGraphPoints(topology, e_8m);
    e_64_points = genGraphPoints(topology, e_64m);
    plt.switch_backend('Agg')
    plt.step(k_8_points[0], k_8_points[1], label='8 Way Shortest Paths');
    plt.step(e_8_points[0], e_8_points[1], label='8 Way ECMP');
    plt.step(e_64_points[0], e_64_points[1], label='64 Way ECMP');
    plt.legend();
    plt.xlabel("Rank of Link");
    plt.ylabel("# of distinct paths link is on");
    plt.savefig( 'figure_9.png' )
    plt.close()


# THESE FUNCTIONS CONVERT THE LISTS OF PATHS TO DATA POINTS
# ---------------------------------------------------------
def genGraphPoints(topology, occur):
    ret = [[0],[0]];
    sortedDict = sorted(occur.items(), key=operator.itemgetter(1));
    # Multiply by 2 because links are bidirectional
    lastRank = (len(topology.links) * 2) - len(sortedDict);
    lastVal = 0;
    ret[0].append(lastRank);
    ret[1].append(lastVal);
    for pair in sortedDict:
        lastRank += 1;
        if pair[1] != lastVal:
            ret[0].append(lastRank);
            ret[1].append(lastVal);
            lastVal = pair[1];
    return ret;

def timesInSet(set):
    ret = defaultdict(int);
    for path in set:
        for i in range(len(path)-1):
            ret[hashPair(path[i], path[i+1])] += 1;
    return ret;

def hashPair(s1, s2):
    return str(s1) + "," + str(s2);

# THESE FUNCTIONS GENERATE PATH SETS FROM A LIST OF K SHORTEST PATHS
# ------------------------------------------------------------------
# Used to select the first max elements of an array
def maxLength(array, max):
    ret = [];
    for i in range(max):
        ret.append(tuple(array[i]));
    return ret;

# Used to select the first elements of an array equal in length,
# capped at maxNum
def firstMaxEqual(array, maxNum):
    ret = [];
    ret.append(tuple(array[0]));
    for i in range(1, maxNum):
        if len(array[i]) != len(array[i-1]):
            return ret;
        ret.append(tuple(array[i]));
    return ret;
