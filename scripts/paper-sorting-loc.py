#!/usr/bin/python3
"""Experimental script comparing performance of pairing heap and smooth heap
in 'sorting mode': n inserts followed by n delete-min operations.
Input lists are randomly generated 'localised' permutations of fixed length with variable
locality parameter.
Results are stored as .csv files in ../data folder and plots of results in ../plots"""

import numpy as np
import matplotlib.pyplot as plt
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
NUMBER_TESTS = 10 # number of tests to run
INCREMENT_LOC = 0.01
TYPES = {0: "Pairing", 12: "Smooth", 24: "Slim", 25: "Pairing Lazy",
         27: "Pairing Slim", 28: "Pairing Smooth"}
MAX_TYPE_KEY = max(TYPES.keys())
COLOURS = {0: 'xkcd:fire engine red', 12: 'xkcd:sea green', 24: 'xkcd:electric blue', 25: 'xkcd:mauve',
           27: 'xkcd:tangerine', 28: 'xkcd:pink'}
SHADE_COLOURS = {0: 'xkcd:fire engine red', 12: 'xkcd:sea green', 24: 'xkcd:electric blue', 25: 'xkcd:mauve',
                 27: 'xkcd:tangerine', 28: 'xkcd:pink'}


def isSorted(list0):
    return all(list0[i] < list0[i + 1] for i in range(len(list0) - 1))


def localizedShuffleByIndex(llist, sdev):
    tuples = []
    for element in llist:
        key = np.random.normal(llist.index(element) * 1.0 / len(llist),
                               sdev)  # generate key using gaussian distribution over sorted index
        tuples += [(key, element)]  # store element with key
    sortedTuples = sorted(tuples, key=lambda x: x[0])  # sort key-element tuples by keys
    sortedList = [tup[1
                  ] for tup in sortedTuples]  # discard keys
    return sortedList


def plot_avg_counts_comps(avgCounts):
    # colours from https://xkcd.com/color/rgb/
    MARKERS_COMP = {0: "o", 12: "^", 24: "p", 25: "s", 26: "v", 27: ".", 28: ">"}  # https://matplotlib.org/3.1.1/api/markers_api.html

    plt.figure('avg number of comps by heap type')
    deviations = [fac * INCREMENT_LOC for fac in range(0, math.ceil(0.3 / INCREMENT_LOC), 1)]
    for k in TYPES.keys():
        avgComps = [acounts[k] for acounts in avgCounts[0]]
        maxComps = [acounts[k] for acounts in avgCounts[2]]
        minComps = [acounts[k] for acounts in avgCounts[4]]
        plt.plot(deviations, avgComps, color=COLOURS[k], linestyle="-", marker=MARKERS_COMP[k],
                 markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black',
                 label=TYPES[k] + " comparisons")
        plt.fill_between(deviations, minComps, maxComps, color=SHADE_COLOURS[k], alpha=.3)

    plt.xlabel('Locality parameter', fontsize=39)
    plt.ylabel('Avg. number of comps / size', fontsize=39)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.rc('legend', fontsize=39)  # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to your full screen (32x18)
    plt.savefig(r'C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\paper-sorting-loc-comps.svg',
                bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()

def plot_avg_counts_links(avgCounts):
    # colours from https://xkcd.com/color/rgb/
    MARKERS_LINK = {0: "o", 12: "D", 24: "X", 25: "*", 26: "P", 27: ".", 28: ">"}

    plt.figure('avg number of links by heap type')
    deviations = [fac * INCREMENT_LOC for fac in range(0, math.ceil(0.3 / INCREMENT_LOC), 1)]
    for k in TYPES.keys():
        avgLinks = [acounts[k] for acounts in avgCounts[1]]
        maxLinks = [acounts[k] for acounts in avgCounts[3]]
        minLinks = [acounts[k] for acounts in avgCounts[5]]
        plt.plot(deviations, avgLinks, color=COLOURS[k], linestyle="--", marker=MARKERS_LINK[k],
                 markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black',
                 label=TYPES[k] + " links")
        plt.fill_between(deviations, minLinks, maxLinks, color=SHADE_COLOURS[k], alpha=.3)

    plt.xlabel('Locality parameter', fontsize=39)
    plt.ylabel('Avg. number of links / size', fontsize=39)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.rc('legend', fontsize=39)  # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to your full screen (32x18)
    plt.savefig(r'C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\paper-sorting-loc-links.svg',
                bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()

def plot_pointer_updates(avgCounts):
    # colours from https://xkcd.com/color/rgb/
    MARKERS_POINTERS = {0: "o", 12: "^", 24: "p", 25: "s", 26: "v", 27: "*", 28: "<"}  # https://matplotlib.org/3.1.1/api/markers_api.html

    plt.figure('avg number of pointer updates by heap type')
    deviations = [fac * INCREMENT_LOC for fac in range(0, math.ceil(0.3 / INCREMENT_LOC), 1)]
    for k in TYPES.keys():
        avgPointers = [acounts[k] for acounts in avgCounts[0]]
        maxPointers = [acounts[k] for acounts in avgCounts[1]]
        minPointers = [acounts[k] for acounts in avgCounts[2]]
        plt.plot(deviations, avgPointers, color=COLOURS[k], linestyle="--", marker=MARKERS_POINTERS[k],
                 markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black',
                 label=TYPES[k] + " pointer updates")
        plt.fill_between(deviations, minPointers, maxPointers, color=SHADE_COLOURS[k], alpha=.3)

    plt.xlabel('Locality parameter', fontsize=39)
    plt.ylabel('Avg. number of pointer updates / size', fontsize=39)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.rc('legend', fontsize=39)  # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to your full screen (32x18)
    plt.savefig(r'C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\pointer-updates-sorting-loc.svg',
                bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()


def export_results(params, results, countType, heapTypes, filename="sorting-loc-lazy"):
    #  exports results of simulation as separate .csv files, one for links and one for comparisons, into ../data directory
    #  each row contains randomness parameter value; plus one column containing the number of operations for each heap type
    if countType == COUNT_TYPE_BOTH:
        with open(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-comps.csv', 'w',
                  newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
            for i in range(len(results[0])):
                row = [params[i]] + [results[0][i][k] for k in TYPES.keys()]
                csvwriter.writerow(row)
        with open(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-links.csv', 'w',
                  newline='') as csvfile:
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

    # ----------localised permutation inputs--------------
    # randomness parameter: standard deviation
    params = [fac * INCREMENT_LOC + 0.00001 for fac in range(0, math.ceil(0.3 / INCREMENT_LOC), 1)]

    for x in params:
        sortedInput = [k for k in range(10000)]
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
            testInput = localizedShuffleByIndex(sortedInput, x)
            print(len(testInput))
            print(testInput)

            for heapType in TYPES.keys():
                linkCount = 0
                compCount = 0
                testOutput = []
                heap = PairingHeap(heapType, COUNT_TYPE_BOTH)
                heap.make_heap()
                for element in testInput:
                # for element in range (1, 5):
                    node = Node(element)
                    (cc, lc) = heap.insert(node)
                for i in range(len(testInput)):
                # for i in range(1, 5):
                    (minNode, cc, lc) = heap.delete_min()
                    # print("minNode is: ", minNode.key)
                    testOutput += [minNode.key]
                    compCount += cc
                    linkCount += lc

                pointers = heap.pointer_updates()

                if isSorted(testOutput):  # sanity check
                    # divide by size for visualization

                    avgCountsLinks[heapType] += (linkCount / NUMBER_TESTS) / 10000
                    avgCountsComps[heapType] += (compCount / NUMBER_TESTS) / 10000
                    avgCountsPointers[heapType] += (pointers / NUMBER_TESTS) / 10000
                    maxCountsLinks[heapType] = max(maxCountsLinks[heapType], linkCount / 10000)
                    maxCountsComps[heapType] = max(maxCountsComps[heapType], compCount / 10000)
                    maxCountsPointers[heapType] = max(maxCountsPointers[heapType], pointers / 10000)
                    minCountsLinks[heapType] = min(minCountsLinks[heapType], linkCount / 10000)
                    minCountsComps[heapType] = min(minCountsComps[heapType], compCount / 10000)
                    minCountsPointers[heapType] = min(minCountsPointers[heapType], pointers / 10000)
                else:
                    raise Exception("Invalid result for {}".format(TYPES[heapType]))
                print("[{}: {}, {}/{}] \t Links: {} \t Comps: {}".format(
                    TYPES[heapType], x, zz + 1, NUMBER_TESTS, linkCount, compCount))  # diagnostics
        for heapType in TYPES.keys():
            print("[{}: {}, avg] \t Links: {} \t Comps: {}".format(TYPES[heapType], x, avgCountsLinks[heapType],
                                                                   avgCountsComps[heapType]))
        avgLinksPerSize += [avgCountsLinks]
        avgCompsPerSize += [avgCountsComps]
        avgPointersPerSize += [avgCountsPointers]
        maxLinksPerSize += [maxCountsLinks]
        maxCompsPerSize += [maxCountsComps]
        maxPointersPerSize += [maxCountsPointers]
        minLinksPerSize += [minCountsLinks]
        minCompsPerSize += [minCountsComps]
        minPointersPerSize += [minCountsPointers]

    plot_avg_counts_links(
        [avgCompsPerSize, avgLinksPerSize, maxCompsPerSize, maxLinksPerSize, minCompsPerSize, minLinksPerSize])
    plot_avg_counts_comps(
        [avgCompsPerSize, avgLinksPerSize, maxCompsPerSize, maxLinksPerSize, minCompsPerSize, minLinksPerSize])
    # plot_pointer_updates([avgPointersPerSize, maxPointersPerSize, minPointersPerSize])
    # export_results(params, [avgCompsPerSize, avgLinksPerSize], COUNT_TYPE_BOTH, TYPES, "sorting-loc-lazy")
