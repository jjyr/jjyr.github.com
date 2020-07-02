---
layout: post
title: "An optimized compacted sparse merkle tree"
data: 2020-02-26 12:40
comments: true
tags: Merkletree Cryptography English
---

Recently, I have designed and implemented a sparse merkle tree which has the following advantages:

* No pre-calculated hash set
* Support both exist proof and non-exists proof
* Efficient storage and key updating

I write this article to explain the construction and optimization tricks of the SMT.

Before diving into details, please make sure you completely understood what sparse merkle tree is, these articles would be helpful:

* [whats a sparse merkle tree]
* [Optimizing sparse Merkle trees]

-------

Trick 1: Zero value optimized hash function.

We define the node merging function:

1. if L == 0, return R
2. if R == 0, return L
3. otherwise return sha256(L, R)

By following this rule, the root of an empty SMT is zero, and nodes contract the SMT are all zero-valued; this brings an advantage: since all nodes are zero-valued for the empty tree, we do not need a pre-calculated hash set.

There's only one issue; this function potentially produces the same value for a different pair of leaves, for example:  `merge(N, 0) == merge(0, N)` . So in our SMT, there may be two trees with the same root but constructed from different leaves. This issue breaks the safety of SMT(an attacker can fooling verifier by pretending the root is constructed from an alternative set of leaves).

To fix this, instead of using `hash(value)` as a leaf's value, we compute the  `hash(key, value)`  as a leaf’s value, leaves using this value to merge with their sibling.

Additionally, we store `leaf_hash -> value`  in a map to keep the index of the original value.

Let's prove the security of this construction.

* Since the key is included in the leaf_hash, and leaf's key is a unique value in SMT, so no matter what the   `value`  is, a leaf's hash value is unique in the tree.
* Each node is either merged by two different hashes or merged by a hash with a zero-value. We already knew that all leaves have a unique hash, so their parent nodes also have a unique hash at the height `n`, and so on, the nodes at `n + 1` all have a unique hash, until the root.
* For the root, if the tree is empty, we got zero, or if the tree is not empty, the root must merge from two hashes or a hash with a zero, it's still unique, any changes in the leaves will also change the root hash.

So we believe this construction is security because we can't construct a collision root hash.

--------

Trick 2: Only store unique non-zero nodes.

The classical node structure for an SMT is `Node {left, right}`, it works fine if we insert every node from root of the tree to bottom, but with the zero-value optimization, mostly nodes are duplicated, we want our tree only store unique nodes.

The idea is simple: for a single leaf SMT, we only store the leaf itself, when inserting new leaves, we figure a way to extract location information from tree storage, and decide the merging order of hashes.

The key to this problem is the leaf's key.  Each key in the SMT can be seen as a path from the root of the tree to leaf, with the path information, we should be able to figure out the merging order of hashes, so on the insertion, we also store the leaf's key in node, and when we need to merge two nodes, we extract the location information from the key:

We can calculate the common height of two leaves' keys, which is exactly the same height that leaves' nodes be merged.

``` rust
fn common_height(key1, key2) {
    for i in 255..0 {
        if key1.get_bit(i) != key2.get_bit(i) {
            // common height
            return i;
        }
    }
    return 0;
}
```

The node structure `BranchNode { fork_height, key, node, sibling}`, using one unique `node` value to express all duplicated nodes' value and plus using the `key` to express all merging order information between `[node.fork_height, 255]`.

* `fork_height` is the height that the node is merged; for a leaf, it is 0.
* `key` is copied from node's one child. for a leaf node, the key is leaf's key.
* `node` and `sibling` is like the `left` and `right` in the classical structure; the only difference is their position is calculated from `key`, instead of fixed left and right.

To get a left child of a node in height `H`:

1. check `H`-th bit of key
2. if it is `1` means the `node` is on the right at height `H`, so `sibling` is the left child
3. if it is `0` means the `node` is on the left, so `sibling` is the right child

``` rust
// get children at height
// return value is (left, right)
fn children(branch_node, height) {
    let is_rhs = branch_node.key.get_bit(height);
    if is_rhs {
        return (branch_node.sibling, branch_node.node)
    } else {
        return (branch_node.node, branch_node.sibling)
    }
}
```

To get a leaf by a key, we walk down the tree from root to bottom:

``` rust
fn get(key) {
    let node = root;
    // path order by height
    let path = BTreeMap::new();
    loop {
        let branch_node = match map.get(node) {
            Some(b) => b,
            None => break,
        }
        // common height may be lower than node.fork_height
        let height = max(common_height(key, node.key), node.fork_height);
        if height > node.fork_height {
            // node is sibling, end search
            path.push(heignt, node);
            break;
        }
        // node is parent
        // extract children position from branch
        let (left, right) = children(branch_node, height);
        // extract key positon
        let is_right = key.get_bit(height);
        if is_right {
            path.push(height, left);
            node = right;
        } else {
            path.push(height, right);
            node = left;
        }
    }
    return self.leaves[node];
}
```

We use a similar algorithm to extract location information for other operations, like updating, merkle proof. It just works as expected.

Link of the [code repo](https://github.com/jjyr/sparse-merkle-tree).

[whats a sparse merkle tree]: https://medium.com/@kelvinfichter/whats-a-sparse-merkle-tree-acda70aeb837 "whats a sparse merkle tree"
[Optimizing sparse Merkle trees]: https://ethresear.ch/t/optimizing-sparse-merkle-trees/3751 "Optimizing sparse Merkle trees"
