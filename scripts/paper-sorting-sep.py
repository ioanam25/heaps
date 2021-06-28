#!/usr/bin/python3
"""Experimental script comparing performance of pairing heap and smooth heap
in 'sorting mode': n inserts followed by n delete-min operations.
Input lists are randomly generated separable permutations of variable length.
Results are stored as .csv files in ../data folder and plots of results in ../plots"""

import random
import matplotlib.pyplot as plt
import copy
import math
import csv
import os, sys, inspect
# ensuring imports work
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from node import Node
from pairing_heap import PairingHeap

COUNT_TYPE_BOTH = 0
COUNT_TYPE_LINKS = -1
COUNT_TYPE_COMPS = -2
MAXSIZE = 18
NUMBER_TESTS = 20  # number of tests to run
TEST_SIZES = [j for j in range(MAXSIZE)]
LIST_LEN = 10000  # number of elements in test list
TEST_SIZE = 10000  # number of elements in test list
STEP_SIZE = 100
INCREMENT_LOC = 0.005
INCREMENT_SUBSEQS = 100
TYPES = {0: "Pairing", 12: "Smooth", 24: "Slim", 25: "Pairing Lazy", 26: "Splay Tree"}
MAX_TYPE_KEY = max(TYPES.keys())
COLOURS = {0: 'xkcd:fire engine red', 12: 'xkcd:sea green', 24: 'xkcd:electric blue', 25: 'xkcd:mauve',
           26: 'xkcd:tangerine'}
SHADE_COLOURS = {0: 'xkcd:fire engine red', 12: 'xkcd:sea green', 24: 'xkcd:electric blue', 25: 'xkcd:mauve',
                 26: 'xkcd:tangerine'}


def isSorted(list0):
	return all(list0[i] < list0[i + 1] for i in range(len(list0) - 1))


def plot_avg_counts(avgCounts):
	# colours from https://xkcd.com/color/rgb/
	MARKERS_COMP = {0: "o", 12: "^", 24: "p", 25: "s", 26: "v"}  # https://matplotlib.org/3.1.1/api/markers_api.html
	MARKERS_LINK = {0: "o", 12: "D", 24: "X", 25: "*", 26: "P"}

	plt.figure('avg number of operations by heap type')
	for k in TYPES.keys():
		print(k)
		avgComps = [acounts[k] for acounts in avgCounts[0]]
		maxComps = [acounts[k] for acounts in avgCounts[2]]
		minComps = [acounts[k] for acounts in avgCounts[4]]
		plt.plot([2**p for p in range(4, MAXSIZE)], avgComps[3:MAXSIZE-1], color=COLOURS[k], linestyle="-", marker=MARKERS_COMP[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " comparisons")
		plt.fill_between([2**p for p in range(4, MAXSIZE)], minComps[3:MAXSIZE-1], maxComps[3:MAXSIZE-1], color=SHADE_COLOURS[k], alpha=.3)
		avgLinks = [acounts[k] for acounts in avgCounts[1]]
		maxLinks = [acounts[k] for acounts in avgCounts[3]]
		minLinks = [acounts[k] for acounts in avgCounts[5]]
		plt.plot([2**p for p in range(4, MAXSIZE)], avgLinks[3:MAXSIZE-1], color=COLOURS[k], linestyle="--", marker=MARKERS_LINK[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " links")
		plt.fill_between([2**p for p in range(4, MAXSIZE)], minLinks[3:MAXSIZE-1], maxLinks[3:MAXSIZE-1], color=SHADE_COLOURS[k], alpha=.3)

	plt.xlabel('Input size', fontsize=39)
	#plt.ylabel('Avg. number of operations / size', fontsize=39)
	plt.xticks(fontsize=30)
	plt.yticks(fontsize=30)
	#plt.rc('legend', fontsize=39)  # using a size in points
	#plt.legend()
	plt.grid(True)
	figure = plt.gcf()  # get current figure
	figure.set_size_inches(16, 18)  # set figure's size manually to full screen
	plt.savefig(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\paper-sorting-sep-lazy.svg", bbox_inches='tight')  # bbox_inches removes extra white spaces
	plt.legend(loc='best')
	plt.show()

def plot_pointer_updates(avgCounts):
	# colours from https://xkcd.com/color/rgb/
	MARKERS_POINTERS = {0: "o", 12: "^", 24: "p", 25: "s", 26: "v"}

	plt.figure('avg number of pointer updates by heap type')
	for k in TYPES.keys():
		print(k)
		avgPointers = [acounts[k] for acounts in avgCounts[0]]
		maxPointers = [acounts[k] for acounts in avgCounts[1]]
		minPointers = [acounts[k] for acounts in avgCounts[2]]
		plt.plot([2**p for p in range(4, MAXSIZE)], avgPointers[3:MAXSIZE-1], color=COLOURS[k],
				 linestyle="-", marker=MARKERS_POINTERS[k], markerfacecolor=COLOURS[k], markersize=9,
				 markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " pointer updates")
		plt.fill_between([2**p for p in range(4, MAXSIZE)], minPointers[3:MAXSIZE-1], maxPointers[3:MAXSIZE-1],
						 color=SHADE_COLOURS[k], alpha=.3)

	plt.xlabel('Input size', fontsize=39)
	plt.ylabel('Avg. number of pointer updates / size', fontsize=39)
	plt.xticks(fontsize=30)
	plt.yticks(fontsize=30)
	#plt.rc('legend', fontsize=39)  # using a size in points
	plt.legend()
	plt.grid(True)
	figure = plt.gcf()  # get current figure
	figure.set_size_inches(16, 18)  # set figure's size manually to full screen
	plt.savefig(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\pointer-updates-sorting-sep.svg", bbox_inches='tight')  # bbox_inches removes extra white spaces
	plt.legend(loc='best')
	plt.show()


def export_results(params, results, countType, heapTypes, filename="sorting-sep-lazy"):
	#  exports results of simulation as separate .csv files, one for links and one for comparisons, into ../data directory
	#  each row contains randomness parameter value; plus one column containing the number of operations for each heap type
	if countType == COUNT_TYPE_BOTH:
		with open(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-comps.csv', 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
			csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
			for i in range(len(results[0])):
				row = [params[i]] + [results[0][i][k] for k in TYPES.keys()]
				csvwriter.writerow(row)
		with open(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-links.csv', 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
			csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
			for i in range(len(results[1])):
				row = [params[i]] + [results[1][i][k] for k in TYPES.keys()]
				csvwriter.writerow(row)
	else:
		fn = r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-links.csv' if countType == COUNT_TYPE_LINKS else r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-comps.csv'
		with open(fn, 'w', newline='') as csvfile:
			csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
			csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
			for i in range(len(results)):
				row = [params[i]] + [results[i][k] for k in TYPES.keys()]
				csvwriter.writerow(row)


def separablePermutation(n):
	assert (n & (n - 1) == 0) and n != 0 and n > 1, "n must be a power of two > 1"  # bit magic

	def generateSepPermutation(l, r):
		flip = random.random() >= 0.5
		if r - l == 1:
			if flip == 0:
				return [r, l]
			else:
				return [l, r]
		else:
			m = math.floor((l + r) / 2)
			if flip == 0:
				return generateSepPermutation(m + 1, r) + generateSepPermutation(l, m)
			else:
				return generateSepPermutation(l, m) + generateSepPermutation(m + 1, r)

	return generateSepPermutation(0, n - 1)


if __name__ == "__main__":
	testOutputCount = []
	avgLinksPerSize = []
	avgCompsPerSize = []
	avgPointersPerSize = []
	maxLinksPerSize = []
	maxCompsPerSize = []
	maxPointersPerSize = []
	minLinksPerSize = []
	minCompsPerSize = []
	minPointersPerSize = []
	sortedInput = []

	# ----------separable permutation---------------------
	# parameter: length (must be power of two)
	params = [2**p for p in range(1, MAXSIZE)]

	for x in params:
		sortedInput = [k for k in range(x)]

		avgCountsLinks = [0 for _ in range(MAX_TYPE_KEY + 1)]
		avgCountsComps = [0 for _ in range(MAX_TYPE_KEY + 1)]
		avgCountsPointers = [0 for _ in range(MAX_TYPE_KEY + 1)]
		maxCountsLinks = [0 for _ in range(MAX_TYPE_KEY + 1)]
		maxCountsComps: list[int] = [0 for _ in range(MAX_TYPE_KEY + 1)]
		maxCountsPointers = [0 for _ in range(MAX_TYPE_KEY + 1)]
		minCountsLinks = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]
		minCountsComps = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]
		minCountsPointers = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]

		for zz in range(NUMBER_TESTS):
			testInput = separablePermutation(x)
			testInput[0] = -1
			for heapType in TYPES.keys():
				linkCount = 0
				compCount = 0
				testOutput = []
				heap = PairingHeap(heapType, COUNT_TYPE_BOTH)
				heap.make_heap()
				for element in testInput:
					node = Node(element)
					(cc, lc) = heap.insert(node)
				for i in range(len(testInput)):
					(minNode, cc, lc) = heap.delete_min()
					testOutput += [minNode.key]
					compCount += cc
					linkCount += lc

				pointers = heap.pointer_updates()
				if isSorted(testOutput):  # sanity check
					#divide by size for visualization

					avgCountsLinks[heapType] += (linkCount / x) / NUMBER_TESTS
					avgCountsComps[heapType] += (compCount / x) / NUMBER_TESTS
					avgCountsPointers[heapType] += (pointers / x) / NUMBER_TESTS
					maxCountsLinks[heapType] = max(maxCountsLinks[heapType], linkCount / x)
					maxCountsComps[heapType] = max(maxCountsComps[heapType], compCount / x)
					maxCountsPointers[heapType] = max(maxCountsPointers[heapType], pointers / x)
					minCountsLinks[heapType] = min(minCountsLinks[heapType], linkCount / x)
					minCountsComps[heapType] = min(minCountsComps[heapType], compCount / x)
					minCountsPointers[heapType] = min(minCountsPointers[heapType], pointers / x)
				else:
					raise Exception("Invalid result for {}".format(TYPES[heapType]))
				print("[{}: {}, {}/{}] \t Links: {} \t Comps: {}".format(
					TYPES[heapType], x, zz+1, NUMBER_TESTS, linkCount, compCount))
		for heapType in TYPES.keys():
			print("[{}: {}, avg] \t Links: {} \t Comps: {}".format(TYPES[heapType], x, avgCountsLinks[heapType], avgCountsComps[heapType]))
		avgLinksPerSize += [avgCountsLinks]
		avgCompsPerSize += [avgCountsComps]
		avgPointersPerSize += [avgCountsPointers]
		maxLinksPerSize += [maxCountsLinks]
		maxCompsPerSize += [maxCountsComps]
		maxPointersPerSize += [maxCountsPointers]
		minLinksPerSize += [minCountsLinks]
		minCompsPerSize += [minCountsComps]
		minPointersPerSize += [minCountsPointers]

	plot_avg_counts([avgCompsPerSize, avgLinksPerSize, maxCompsPerSize, maxLinksPerSize, minCompsPerSize, minLinksPerSize])
	plot_pointer_updates([avgPointersPerSize, maxPointersPerSize, minPointersPerSize])
	export_results(params, [avgCompsPerSize, avgLinksPerSize], COUNT_TYPE_BOTH, TYPES, "pointer-updates-sorting-sep")

