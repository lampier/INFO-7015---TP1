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


def main():
	y = []
	max_v = -1
	for i in range( 1, len(sys.argv) ):	
		tempy = []
		for j in open( sys.argv[i], 'r' ):
			tempy.append(float(j.rstrip().split('\t')[-1]))
			if tempy[-1] > max_v:
				max_v = tempy[-1]
		y.append(copy.copy(tempy))
	plotHistogram( len(y), y, max_v, "Betweenness" )		

if __name__ == "__main__":
	main()


