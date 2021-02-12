#!/usr/bin/python3
import random
import copy
import matplotlib.pyplot as plt
import math
import numpy as np

"""This file generates visualizations of the different random permutation classes.
Resulting plots are stored in ../plots"""

def plot_permutation(permutation, title, filename):
    # visualizing given permutation as element index in permutation over element index in sorted list
    # colours from https://xkcd.com/color/rgb/
    plt.figure(title)
    sortedList = copy.copy(permutation)
    sortedList.sort()
    indices = [i for i in range(len(sortedList))]
    pindices = [permutation.index(x) for x in sortedList]
    plt.plot(indices, pindices, color='xkcd:charcoal', marker='o', linestyle="", label="(sorted index, permuted index)")
    plt.xlabel('Index in sorted list', fontsize=26)
    plt.ylabel('Index in permutation', fontsize=26)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.rc('legend',fontsize=26) # using a size in points
    plt.legend()
    plt.grid(True)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 18)  # set figure's size manually to full screen
    plt.savefig('../plots/paper-permutation-{}.svg'.format(filename), bbox_inches='tight')  # bbox_inches removes extra white spaces
    plt.legend(loc='best')
    plt.show()
    
def localizedShuffleByIndex(llist, sdev):
    tuples = []
    for element in llist:
        key = np.random.normal(llist.index(element) * 1.0 / len(llist),
                               sdev)  # generate key using gaussian distribution over sorted index
        tuples += [(key, element)]  # store element with key
    sortedTuples = sorted(tuples, key=lambda x: x[0])  # sort key-element tuples by keys
    sortedList = [tup[1] for tup in sortedTuples]  # discard keys
    return sortedList
    
    
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
    
    
def generateContSortedSubseq(llist, sublen):
    listcopy = copy.copy(llist)
    random.shuffle(listcopy)
    res = []
    l = 0
    while l < len(llist):
        clen = random.randint(1, sublen)
#        clen = sublen
        sublist = copy.copy(listcopy[l:min(l + clen, len(listcopy))])
        sublist.sort()
        res += sublist
        l += clen
    return res
    
sortedList = [x for x in range(512)]
#  generating uniformly random permutation
randomPermutation = copy.copy(sortedList)
random.shuffle(randomPermutation)
plot_permutation(randomPermutation, "Uniformly Random Permutation", "uniform")
#  generating random separable permutation
separablePermutation = separablePermutation(512)
plot_permutation(separablePermutation, "Random Separable Permutation", "separable")
#  generating random localized permutation
localizedPermutation = localizedShuffleByIndex(sortedList, 0.15)
plot_permutation(localizedPermutation, "Random Localized Permutation", "localized")
#  generating random permutation with continuous sorted subsequences
subseqPermutation = generateContSortedSubseq(sortedList, 30)
plot_permutation(subseqPermutation, "Random Subsequence Permutation", "subseq")

