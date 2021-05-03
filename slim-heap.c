/*
                     Slim heap implementation

  The "Slim heap" is a variant of the "Smooth heap". Both are simple and efficient 
  self-adjusting priority queues, with similarities to the Pairing heap. 
  The supported operations are:
    * insert        
    * find_min
    * delete_min
    * decrease_key
    * merge
    * delete
  
  Smooth and slim heaps are described in the papers:
   * L. Kozma, T. Saranurak: "Smooth heaps and a dual view of self-adjusting
      data structures" SIAM J. Comput. 49(5) (2020)
      https://arxiv.org/abs/1802.05471
   * M. Hartmann, L. Kozma, C. Sinnamon, R. Tarjan: "Analysis of smooth heaps
      and slim heaps" ICALP (2021)

  The implementation uses a straightforward pointer-structure, loosely 
  inspired by D. Sleator's implementation of the Splay tree.  It is based on
  a single multi-ary tree where each node stores a key, according to the 
  (min-)heap order, so that the key of a non-root node is at least the key
  of its parent.  Each node has the pointers: left (sibling), right (sibling), 
  and rightmost (child).  Siblings are linked into a doubly-linked, almost*
  circular list.
  (* The left pointer of each leftmost child points back to the parent,
  this allows us to get away without using parent pointers.)

  Additional data can be stored in the nodes as necessary.

  Compile: gcc slim-heap.c -lm

  This code was written by L. Kozma <laszlo.kozma@fu-berlin.de> 
  and is released into the public domain. 

  Version 0.02, May 2021.
  Latest version: www.lkozma.net/slim-heap.c  and   www.lkozma.net/smooth-heap.c

*/


#include <stdio.h>
#include <stdlib.h>
#define INT_MIN -2147483648

/*  The structure holding single nodes as well as the entire heap.  */

typedef struct heap_node Heap;
struct heap_node {
    Heap * left, * right, * rightmost;
    int key;
};


/*  Create a new node with a given key. 
    Return a pointer to the new node. 
    Needed if we may insert this node later using insertn.  */

Heap * new_node(int i) {

   Heap * n;
   n = (Heap *) malloc (sizeof (Heap));
   if (!n) {
	printf("Ran out of space\n");
	exit(1);
   }
   n->key = i;
   n->left = n->right = n; 
   n->rightmost = NULL;
   return n;
}


/*  Insert heap node n into the heap h.  
    Return a pointer to the modified heap.  
    This variant to be used if pointer to inserted node  
      needed later e.g. for decrease-key or delete.  */

Heap * insertn(Heap * n, Heap * h) {

    Heap * rm;
    if (!h || n->key < h->key) {
	n->rightmost = h;
	return n;
    }
    rm = h->rightmost;
    if (!rm) {                    /*  h has no child  */
        n->left = h;
        h->rightmost = n;
        return h;
    } else {                      /*  h has a child  */
        n->right = rm->right;
        n->left = rm;
        rm->right = n;
        h->rightmost = n;
        return h;
    }
}


/*  Insert key i into the heap h.   
    Return a pointer to the modified heap.  */

Heap * insert(int i, Heap * h) {

    Heap * n, * h2;
    n = new_node(i);
    h2 = insertn(n,h);
    return h2;
}


/*  Findmin needs no function.  For heap h, the minimum key is h->key.
    The node with minimum key is simply h.  */


/*  Link heaps parent and child, assuming both exist. 
    Return a pointer to the resulting heap. 
    This is also the linking primitive used by other operations.  */
 
Heap * link(Heap * parent, Heap * child) {

    Heap * rm;
    rm = parent->rightmost;
    if (!rm) {
        child->left = parent;
        child->right = child;
    } else {
        child->right = rm->right;
        child->left = rm;
        rm->right = child;
    }
    parent->rightmost = child;
    return parent;
}


/*  Merge heaps h1 and h2. Return a pointer to the resulting heap. 
    Also used by some other operations. */
 
Heap * merge(Heap * h1, Heap * h2) {

    Heap * rm, * parent, * child;
    if (!h1)  
        return h2;
    if (!h2 || h1 == h2)
        return h1;
    if (h1->key < h2->key) {
        parent = h1;
        child = h2;
    } else {
        parent = h2;
        child = h1;
    }
    parent = link(parent, child);
    return parent;
}


/*  Print keys of the heap in preorder.  Useful for debugging.  */

void print(Heap *h) {

    Heap * x, * lm, *rm;
    if (h) {
        printf("%d | ", h->key);
        rm = h->rightmost;
        if (rm) {
            x = lm = rm->right;
            do {
                print(x);
                x = x->right;
                printf("- ");
            } while (x != lm);
            printf("^ ");
        }
    }    
}


/*  Decrease key of node n in heap h to k. 
    Return a pointer to the resulting heap. 
    It is the user's responsibility to ensure that n exists within h,
    otherwise all bets are off.  */

Heap * decrease_key(Heap * n, Heap * h, int k) {

    Heap * h2, * nl, * nr;    
    if (!h || !n) {
        printf("Error: heap or node empty!\n");
        exit(1);
    } 
    if (n->key < k) {
        printf("Error: decrease_key trying to increase!\n");
        exit(1);
    }
    n->key = k;    
    if (n == h)                             /*  n is the root  */
        return h;
    nl = n->left;
    nr = n->right;
    if (nr == n) {                          /*  n is a unique child  */
        nl->rightmost = NULL;          
    } else if (nr->left->rightmost == n) {  /*  n is a rightmost child  */
        nl->right = nr;
        nr->left->rightmost = nl;
    } else if (nl->rightmost && nl->rightmost->right == n) { 
        nl->rightmost->right = nr;          /*  n is a leftmost child  */
        nr->left = nl;
    } else {                                /*  none of the above  */
        nl->right = nr;
        nr->left = nl;
    }
    n->left = n->right = n;
    h2 = merge(h, n);
    return h2;    
}


/*  Delete the minimum-key node (i.e. the root) of heap h. 
    This is where the restructuring specific to slim heaps happens.
    Return a pointer to the resulting heap after restructuring.  */

Heap * delete_min(Heap * h) {

    Heap * x, * tl, *tr, *rm;
    if (!h) {
        printf("Error: heap empty!\n");
        exit(1);
    } 
    rm = h->rightmost;
    if (!rm)
        return NULL;

    x = rm->right;                                  /*  close off margins  */
    x->left = NULL;                                  
    rm->right = NULL;

    while (x->right) {                              /*  left-to-right phase  */
        if (x->key < x->right->key)
            x = x->right;
        else {                                      /*  x is a local max  */
            while ((x->left) && (x->left->key > x->right->key)) { /*  link left  */
                tr = x->right;
                x = link(x->left, x);
                tr->left = x;
                x->right = tr;
            }
            tl = x->left;                                         /*  link right  */
            tr = x->right->right;
            x = link(x->right, x); 
            if (tl)
                tl->right = x;
            x->left = tl; 
        }    
    }
    while (x->left) {                               /*  right-to-left phase  */
        x = link(x->left, x);
    }
    x->left = x->right = x;
    free(h);
    return x;
}


/*  Delete node n in heap h. 
    Return a pointer to the resulting heap.  
    It is the user's responsibility to ensure that n exists within h,
    otherwise all bets are off.  */
 
Heap * delete(Heap * n, Heap * h) {

    Heap * h2;
    h2 = decrease_key(n, h, INT_MIN);
    h2 = delete_min(h2);
    return h2;
}


/*  A sample use of these functions.  Start with the empty heap,         
    insert some stuff into it, and play around with the operations.  */

void main() {
    Heap * heap, * heap2, * heap3, * heap4, * temp, * temp2;
    int z, i;
    heap = NULL;               /* the empty heap */
    heap = insert(10, heap);
    heap = insert(20, heap);
    heap = insert(5, heap);
    temp = new_node(25);
    heap = insertn(temp, heap);
    heap = insert(30, heap);
    heap = insert(9, heap);
    heap = insert(50, heap);
    heap = insert(6, heap);
    heap = insert(100, heap);
    heap = insert(120, heap);
    heap = insert(90, heap);

    heap2 = NULL;
    heap2 = insert(4, heap2);
    heap2 = insert(8, heap2);
    temp2 = new_node(11);
    heap2 = insertn(temp2, heap2);
    heap2 = insert(3, heap2);

    heap3 = NULL;
    heap3 = merge(heap2, heap);
    print(heap3);
    printf("#\n");

    heap3 = delete_min(heap3);
    print(heap3);
    printf("#\n");

    heap3 = delete_min(heap3);
    print(heap3);
    printf("#\n");

    heap3 = decrease_key(temp2, heap3, 1);
    print(heap3);
    printf("#\n");

    heap3 = delete_min(heap3);
    print(heap3);
    printf("#\n");

    heap3 = delete_min(heap3);
    print(heap3);
    printf("#\n");


    heap3 = delete(temp, heap3);
    print(heap3);
    printf("#\n");
   

    heap4 = NULL;             
    for (i=1;i<10000;i++) {
        z = (i*973133) % 10000;
        heap4 = insert(z, heap4);
        //printf("%d\n", z);
    }

    //printf("\n\n");
    //print(heap4);
    //printf("#\n");

    for (i=1;i<10000;i++) {
        //printf("%d.%d\n", i, heap4->key);
        heap4 = delete_min(heap4);
    }

}
