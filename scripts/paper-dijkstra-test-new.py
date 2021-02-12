#!/usr/bin/python3
"""Experimental script comparing performance of pairing heap and smooth heap
as priority queue in Dijkstra's algorithm. Algorithm is run on randomly generated
Erdös-Renyi graphs of fixed size and variable edge probability.
Results are stored as .csv files in ../data folder and plots of results in ../plots"""


import os, sys, inspect
# ensuring imports work
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

TYPES = {21: "Pairing", 22: "Smooth"} 
MAX_TYPE_KEY = max(TYPES.keys())
#COLOURS = ['xkcd:fire engine red', 'xkcd:dusty orange', 'xkcd:clear blue', 'xkcd:cool green',
#           'xkcd:macaroni and cheese', 'xkcd:fire engine red', 'xkcd:dusty orange', 'xkcd:clear blue',
#           'xkcd:cool green', 'xkcd:macaroni and cheese', 'xkcd:bright sky blue', 'xkcd:bright sky blue', 'xkcd:green',
#           'xkcd:ochre', 'xkcd:sea blue', 'xkcd:sea green', 'xkcd:sea blue', 'xkcd:warm grey',
#           'xkcd:bright sky blue', 'xkcd:bright sky blue']
LINETYPES = 5 * ['-'] + 5 * ['--'] + ['--', '-'] + ['--', '--', '--', '--', '--', '--', '-', '-']
FIG_LABELS = ["comparisons", "links"]
MAX_TYPE_KEY = max(TYPES.keys())

COLOURS = {21:'xkcd:fire engine red', 22:'xkcd:sea green'}
SHADE_COLOURS = {21:'#fe4d4e', 22:'#58ab8e'}

NUMBER_TESTS = 10  # number of tests to run
TEST_SIZE = 500  # ,6000,7000,8000,9000,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000
EDGE_PROBABILITY = 0.05
WEIGHT_RANGE = 10000


def plot_avg_counts_old(avgCounts):
    # colours from https://xkcd.com/color/rgb/
    linetypes = 5 * ["-"] + 5 * ["--"] + ["--", "-"] + ["-, -"]
    plt.figure('Dijkstra with variable connectivity')
    for k in TYPES.keys():
        avgComps = [acounts[k] for acounts in avgCounts[0]]
        plt.plot([factor * EDGE_PROBABILITY for factor in range(1, 101, 1)], avgComps, color=COLOURS[k], linestyle='-',
                 label=TYPES[k] + " comparisons")
        avgLinks = [acounts[k] for acounts in avgCounts[1]]
        plt.plot([factor * EDGE_PROBABILITY for factor in range(1, 101, 1)], avgLinks, color=COLOURS[k], linestyle='--',
                 label=TYPES[k] + " links")
    plt.grid(True)
    plt.legend(loc='best')
    plt.show()

def plot_avg_counts(avgCounts):
    # colours from https://xkcd.com/color/rgb/
    MARKERS_COMP = {21:"o", 12:"d", 22:"^"}#https://matplotlib.org/3.1.1/api/markers_api.html
    MARKERS_LINK = {21:"o", 12:"D", 22:"D"}
    plt.figure('avg number of operations in Dijkstra\'s algorithm')
    deviations = [factor * EDGE_PROBABILITY for factor in range(1, 21, 1)]
    for k in TYPES.keys():
        #print(k)
        avgComps = [acounts[k] for acounts in avgCounts[0]]
        maxComps = [acounts[k] for acounts in avgCounts[2]]
        minComps = [acounts[k] for acounts in avgCounts[4]]
        plt.plot(deviations, avgComps, color=COLOURS[k], linestyle="-", marker=MARKERS_COMP[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " comparisons")
        plt.fill_between(deviations, minComps, maxComps, color=SHADE_COLOURS[k], alpha=.3)
        avgLinks = [acounts[k] for acounts in avgCounts[1]]
        maxLinks = [acounts[k] for acounts in avgCounts[3]]
        minLinks = [acounts[k] for acounts in avgCounts[5]]
        plt.plot(deviations, avgLinks, color=COLOURS[k], linestyle="--", marker=MARKERS_LINK[k], markerfacecolor=COLOURS[k], markersize=9, markeredgewidth=1, markeredgecolor='black', label=TYPES[k] + " links")
        plt.fill_between(deviations, minLinks, maxLinks, color=SHADE_COLOURS[k], alpha=.3)


    plt.xlabel('Edge probability', fontsize=26)
    plt.ylabel('Avg. number of operations / size', fontsize=26)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.rc('legend',fontsize=26) # using a size in points
    plt.legend()
    plt.grid(True)
    #plt.gca().invert_xaxis()
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to full screen
    plt.savefig('../plots/paper-dijkstra-new.svg', bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()


def export_results(xs, results, countType, heapTypes, filename="dijkstra"):
    # parse data as randomness parameter; counts per heap type
    if countType == COUNT_TYPE_BOTH:
        with open("../data/" + filename + '-comps.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
            for i in range(len(results[0])):
                row = [xs[i]] + [results[0][i][k] for k in TYPES.keys()]
                csvwriter.writerow(row)
        with open("../data/" + filename + '-links.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.values()])
            csvwriter.writerow(["randomness parameter value"] + [name for name in TYPES.keys()])
            for i in range(len(results[1])):
                row = [xs[i]] + [results[1][i][k] for k in TYPES.keys()]
                csvwriter.writerow(row)
    else:
        fn = "../data/" + filename + '-links.csv' if countType == COUNT_TYPE_LINKS else "../data/" + filename + '-comps.csv'
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
    maxLinksPerSize = []
    maxCompsPerSize = []
    minLinksPerSize = []
    minCompsPerSize = []

    xs = [factor * EDGE_PROBABILITY for factor in range(1, 21, 1)]
    for x in xs:
        avgCountsLinks = [0 for _ in range(MAX_TYPE_KEY + 1)]
        avgCountsComps = [0 for _ in range(MAX_TYPE_KEY + 1)]
        maxCountsLinks = [0 for _ in range(MAX_TYPE_KEY + 1)]
        maxCountsComps = [0 for _ in range(MAX_TYPE_KEY + 1)]
        minCountsLinks = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]
        minCountsComps = [1000000000000 for _ in range(MAX_TYPE_KEY + 1)]


        for _ in range(NUMBER_TESTS):
            # some nice graph generators here: https://networkx.github.io/documentation/stable/reference/generators.html
            graph = nx.fast_gnp_random_graph(TEST_SIZE, x)
            # graph = nx.random_regular_graph(10, 1000)
            for (u, v) in graph.edges():
                graph.edges[u, v]['w'] = random.randint(1, WEIGHT_RANGE)
            for heapType in TYPES.keys():
                for v in graph.nodes():
                    graph.nodes[v]['v'] = False # "visited" marker
                linkCount = 0
                compCount = 0
                vertex2qnode = {}
                dist = [888888888 for _ in range(len(graph.nodes()))]
                prev = [None for _ in range(len(graph.nodes()))]

                heap = PairingHeap(heapType, COUNT_TYPE_BOTH)
                heap.make_heap()

                source = graph.nodes()[0]
                dist[0] = 0
                for idx, v in enumerate(graph.nodes()):
                    #qnode = Node(dist[idx])
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
                    #print(uk)
                    #print('extracted {}'.format(minNode.key))
                    graph.nodes[u]['v'] = True #  minNode has been visited
                    for idx, v in enumerate(graph.neighbors(u)):
                        alt = uk + graph.edges[u, v]['w']
                        if alt < dist[v] and not graph.nodes[v]['v']:
                            (cc, lc) = heap.decrease_key(vertex2qnode[v], dist[v] - alt)
                            #print('decreased from {} to {}'.format(dist[v],alt))
                            linkCount += lc
                            compCount += cc
                            dist[v] = alt
                            prev[v] = u
                avgCountsLinks[heapType] += (linkCount / NUMBER_TESTS)/TEST_SIZE
                avgCountsComps[heapType] += (compCount / NUMBER_TESTS)/TEST_SIZE
                maxCountsLinks[heapType] = max(maxCountsLinks[heapType],linkCount/TEST_SIZE)
                maxCountsComps[heapType] = max(maxCountsComps[heapType],compCount/TEST_SIZE)
                minCountsLinks[heapType] = min(minCountsLinks[heapType],linkCount/TEST_SIZE)
                minCountsComps[heapType] = min(minCountsComps[heapType],compCount/TEST_SIZE)

        for heapType in TYPES.keys():
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print(
                "[{}] \t avgComp: {} \t avgLink: {} \t RAM: {} \t |V|={} \t |E|={}".format(
                    TYPES[heapType], avgCountsComps[heapType], avgCountsLinks[heapType], memoryUse, len(graph.nodes()), len(graph.edges())))
        avgLinksPerSize += [avgCountsLinks]
        avgCompsPerSize += [avgCountsComps]
        maxLinksPerSize += [maxCountsLinks]
        maxCompsPerSize += [maxCountsComps]
        minLinksPerSize += [minCountsLinks]
        minCompsPerSize += [minCountsComps]
    # plot_avg_counts([avgCompsPerSize, avgLinksPerSize])
    plot_avg_counts([avgCompsPerSize, avgLinksPerSize, maxCompsPerSize, maxLinksPerSize,  minCompsPerSize, minLinksPerSize])
    export_results(xs, [avgCompsPerSize, avgLinksPerSize], COUNT_TYPE_BOTH, TYPES, "dijkstra")