#!/usr/bin/python3
"""Experimental script comparing performance of pairing heap and smooth heap
as priority queue in Dijkstra's algorithm. Algorithm is run on randomly generated
Erdös-Renyi graphs of fixed size and variable edge probability.
Results are stored as .csv files in ../data folder and plots of results in ../plots"""


import os, sys, inspect
# ensuring imports work
from typing import List

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from node import Node
from pairing_heap import PairingHeap
import networkx as nx
import random
import matplotlib.pyplot as plt
import os
import psutil
import csv

COUNT_TYPE_BOTH = 0
COUNT_TYPE_LINKS = -1
COUNT_TYPE_COMPS = -2

TYPES = {21: "Pairing", 22: "Smooth", 23: "Slim", 25: "Pairing Lazy", 27: "Pairing Slim", 28: "Pairing Smooth"}

MAX_TYPE_KEY = max(TYPES.keys())
FIG_LABELS = ["comparisons", "links"]

COLOURS = {21:'xkcd:fire engine red', 22:'xkcd:sea green', 23:'xkcd:electric blue',
           25:"xkcd:mauve", 27: "xkcd:pink", 28: "xkcd:orange"}
SHADE_COLOURS = {21:'xkcd:fire engine red', 22:'xkcd:sea green', 23:'xkcd:electric blue',
                 25:"xkcd:mauve", 27: "xkcd:pink", 28: "xkcd:orange"}

NUMBER_TESTS = 10  # number of tests to run
TEST_SIZE = 500
EDGE_PROBABILITY = 0.05
WEIGHT_RANGE = 10000


def plot_avg_counts_links(avgCounts):
    """generates and saves plot of results"""
    # colours from https://xkcd.com/color/rgb/
    #https://matplotlib.org/3.1.1/api/markers_api.html
    MARKERS_LINK = {21:"o", 12:"D", 22:"D", 23: "X", 25: "*", 27: "<", 28: "d"}
    plt.figure('avg number of links in Dijkstra\'s algorithm')
    deviations = [factor * EDGE_PROBABILITY for factor in range(1, 21, 1)]
    for k in TYPES.keys():
        avgLinks = [acounts[k] for acounts in avgCounts[1]]
        maxLinks = [acounts[k] for acounts in avgCounts[3]]
        minLinks = [acounts[k] for acounts in avgCounts[5]]
        plt.plot(deviations, avgLinks, color=COLOURS[k], linestyle="--", marker=MARKERS_LINK[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " links")
        plt.fill_between(deviations, minLinks, maxLinks, color=SHADE_COLOURS[k], alpha=.3)

    plt.xlabel('Edge probability', fontsize=39)
    plt.ylabel('Avg. number of links / size', fontsize=39)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.rc('legend',fontsize=30)  # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to full screen
    plt.savefig(r'C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\paper-dijkstra-links.svg', bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()

def plot_avg_counts_comps(avgCounts):
    MARKERS_COMP = {21:"o", 12:"d", 22:"^", 23:"p", 25:"s", 27: ".", 28: ">"}#https://matplotlib.org/3.1.1/api/markers_api.html
    plt.figure('avg number of comparisons in Dijkstra\'s algorithm')
    deviations = [factor * EDGE_PROBABILITY for factor in range(1, 21, 1)]
    for k in TYPES.keys():
        avgComps = [acounts[k] for acounts in avgCounts[0]]
        maxComps = [acounts[k] for acounts in avgCounts[2]]
        minComps = [acounts[k] for acounts in avgCounts[4]]
        plt.plot(deviations, avgComps, color=COLOURS[k], linestyle="-", marker=MARKERS_COMP[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " comparisons")
        plt.fill_between(deviations, minComps, maxComps, color=SHADE_COLOURS[k], alpha=.3)

    plt.xlabel('Edge probability', fontsize=39)
    plt.ylabel('Avg. number of comparisons / size', fontsize=39)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.rc('legend',fontsize=30)  # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to full screen
    plt.savefig(r'C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\paper-dijkstra-comps.svg', bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()

def plot_pointer_updates(avgCounts):
    """generates and saves plot of results"""
    # colours from https://xkcd.com/color/rgb/
    MARKERS_POINTERS = {21:"o", 12:"d", 22:"^", 23:"p", 25:"s", 27: ".", 28: ">"}#https://matplotlib.org/3.1.1/api/markers_api.html
    deviations = [factor * EDGE_PROBABILITY for factor in range(1, 21, 1)]
    plt.figure('avg number of pointer updates in Dijkstra\'s algorithm')
    for k in TYPES.keys():
        avgPointers = [acounts[k] for acounts in avgCounts[0]]
        maxPointers = [acounts[k] for acounts in avgCounts[1]]
        minPointers = [acounts[k] for acounts in avgCounts[2]]
        plt.plot(deviations, avgPointers, color=COLOURS[k], linestyle="--", marker=MARKERS_POINTERS[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " pointer updates")
        plt.fill_between(deviations, minPointers, maxPointers, color=SHADE_COLOURS[k], alpha=.3)

    plt.xlabel('Edge probability', fontsize=39)
    plt.ylabel('Avg. number of pointer updates / size', fontsize=39)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.rc('legend',fontsize=30)  # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to full screen
    plt.savefig(r'C:\Users\Admin\PycharmProjects\smooth-heap-pub\plots\pointer-updates-dijkstra.svg', bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()

def export_results(xs, results, countType, heapTypes, filename="dijkstra-lazy"):
    # parse data as randomness parameter; counts per heap type
    if countType == COUNT_TYPE_BOTH:
        with open(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-comps.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
            for i in range(len(results[0])):
                row = [xs[i]] + [results[0][i][k] for k in TYPES.keys()]
                csvwriter.writerow(row)
        with open(r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-links.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
            for i in range(len(results[1])):
                row = [xs[i]] + [results[1][i][k] for k in TYPES.keys()]
                csvwriter.writerow(row)
    else:
        fn = r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-links.csv' if countType == COUNT_TYPE_LINKS else r"C:\Users\Admin\PycharmProjects\smooth-heap-pub\data\\" + filename + '-comps.csv'
        with open(fn, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
            for i in range(len(results)):
                row = [xs[i]]+[results[i][k] for k in TYPES.keys()]
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

    xs = [factor * EDGE_PROBABILITY for factor in range(1, 21, 1)]
    for x in xs:
        avgCountsLinks = [0 for _ in range(MAX_TYPE_KEY + 1)]
        avgCountsComps = [0 for _ in range(MAX_TYPE_KEY + 1)]
        avgCountsPointers = [0 for _ in range(MAX_TYPE_KEY + 1)]
        maxCountsLinks = [0 for _ in range(MAX_TYPE_KEY + 1)]
        maxCountsComps: list[int] = [0 for _ in range(MAX_TYPE_KEY + 1)]
        maxCountsPointers = [0 for _ in range(MAX_TYPE_KEY + 1)]
        minCountsLinks = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]
        minCountsComps = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]
        minCountsPointers = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]


        for _ in range(NUMBER_TESTS):
            # some nice graph generators here: https://networkx.github.io/documentation/stable/reference/generators.html
            # initialize input graph
            graph = nx.fast_gnp_random_graph(TEST_SIZE, x)
            for (u, v) in graph.edges():  # assign weights
                graph.edges[u, v]['w'] = random.randint(1, WEIGHT_RANGE)
            # heapType: int
            for heapType in TYPES.keys():
                for v in graph.nodes():
                    graph.nodes[v]['v'] = False  # "visited" marker
                linkCount = 0
                compCount = 0
                vertex2qnode = {}  # mapping graph nodes to heap nodes
                dist = [888888888 for _ in range(len(graph.nodes()))]
                prev = [None for _ in range(len(graph.nodes()))]

                heap = PairingHeap(heapType, COUNT_TYPE_BOTH)
                heap.make_heap()

                # Dijkstra's algorithm
                dist[0] = 0  # start node
                for idx, v in enumerate(graph.nodes()):
                    qnode = Node(dist[v])
                    qnode.vertex = v
                    vertex2qnode[v] = qnode
                    (cc, lc) = heap.insert(qnode)
                    linkCount += lc
                    compCount += cc

                for s in range(len(graph.nodes())):
                    (minNode, cc, lc) = heap.delete_min()
                    linkCount += lc
                    compCount += cc
                    if minNode is None:
                        raise Exception(
                            "delete-min on heap of type {} returned None with {} nodes removed".format(TYPES[heapType],
                                                                                                       s))
                    u = minNode.vertex
                    uk = minNode.key
                    graph.nodes[u]['v'] = True  # minNode has been visited
                    for idx, v in enumerate(graph.neighbors(u)):
                        alt = uk + graph.edges[u, v]['w']
                        if alt < dist[v] and not graph.nodes[v]['v']:
                            (cc, lc) = heap.decrease_key(vertex2qnode[v], dist[v] - alt)
                            linkCount += lc
                            compCount += cc
                            dist[v] = alt
                            prev[v] = u

                    pointers = heap.pointer_updates()
                # track avg. results
                avgCountsLinks[heapType] += (linkCount / NUMBER_TESTS)/TEST_SIZE
                avgCountsComps[heapType] += (compCount / NUMBER_TESTS)/TEST_SIZE
                avgCountsPointers[heapType] += (pointers / NUMBER_TESTS)/TEST_SIZE
                maxCountsLinks[heapType] = max(maxCountsLinks[heapType], linkCount/TEST_SIZE)
                maxCountsComps[heapType] = max(maxCountsComps[heapType], compCount/TEST_SIZE)
                maxCountsPointers[heapType] = max(maxCountsPointers[heapType], pointers/TEST_SIZE)
                minCountsLinks[heapType] = min(minCountsLinks[heapType], linkCount/TEST_SIZE)
                minCountsComps[heapType] = min(minCountsComps[heapType], compCount/TEST_SIZE)
                minCountsPointers[heapType] = min(minCountsPointers[heapType], pointers/TEST_SIZE)

        for heapType in TYPES.keys():
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print(
                "[{}] \t avgComp: {} \t avgLink: {} \t RAM: {} \t |V|={} \t |E|={}".format(
                    TYPES[heapType], avgCountsComps[heapType], avgCountsLinks[heapType], memoryUse, len(graph.nodes()), len(graph.edges())))
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
        [avgCompsPerSize, avgLinksPerSize, maxCompsPerSize, maxLinksPerSize,  minCompsPerSize, minLinksPerSize])
    plot_avg_counts_comps(
        [avgCompsPerSize, avgLinksPerSize, maxCompsPerSize, maxLinksPerSize, minCompsPerSize, minLinksPerSize])
    plot_pointer_updates([avgPointersPerSize, maxPointersPerSize, minPointersPerSize])
    # export_results(xs, [avgCompsPerSize, avgLinksPerSize], COUNT_TYPE_BOTH, TYPES, "dijkstra-lazy")
