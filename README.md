This repository contains an implementation of smooth heap and pairing heap, as well as scripts to reproduce experimental findings.

# Documentation
### Heap implementations
The top level contains the actual heap implementations used in experiments, as well as a low-level implementation of smooth heap.

- `pairing_heap.py` 'Universal heap', bundles all variant implementations.
- `pairing_heap_standard.py` Implements the standard pairing heap variant; used for sorting experiments.
- `pairing_heap_l.py` Implements lazy-linking variant of standard pairing heap; used for experiments with Dijkstra's algorithm.
- `smooth_heap.py` Implements analytical variant of smooth heap; used for sorting heap experiments.
- `smooth_heap_l.py` Implements slightly modified lazy-linking variant of smooth heap; used for experiments with Dijkstra's algorithm.
- `smooth_heap.c` Sample implementation of smooth heap in C, not used in experiments.

### Experimental scripts
All scripts running experiments are located in the /scripts folder. Each script generates two .csv files of results, reporting average number of linking operations and comparisons, respectively.
These files are stored in the /data folder. Plots of results are stored in the /plots folder.
- `paper-permutations.py` Generates sample plots of classes of permutations used for the sorting tests. Images generated are saved to /plots folder.
- `paper-sorting-loc.py` Performs sorting on random instances of the class of localized permutations.
- `paper-sorting-sep.py` Performs sorting on random separable permutations.
- `paper-sorting-subseq.py` Performs sorting on random permutations containing sorted subsequences.
- `paper-sorting-uniform.py` Performs sorting on uniformly random permutations.
- `paper-dijkstra-test.py` Performs Dijkstra's algorithm on randomly generated Erdös-Renyi graphs of fixed size and variable edge probability.
- `paper-dijkstra-test2.py` Performs Dijkstra's algorithm on randomly generated
k-regular graphs of variable size.