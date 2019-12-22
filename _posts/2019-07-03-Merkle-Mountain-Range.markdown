---
layout: post
title: "Merkle Mountain Range"
data: 2019-07-03 21:55
comments: true
---

## Merkle Tree

Merkle Tree 是区块链中经常（或者说必须？）会用到结构。

``` bash
// 比特币交易列表的 Merkle Tree

            A
          /   \
        B       C
       / \     / \
      D   E   F   G
     / \ / \ / \ / \
     1 2 3 4 5 6 7 8
```

树的叶子节点（图中的 `1,2,3,4,5,6,7,8`）是插入的元素，在图例中是比特币的 txid。
非叶子节点是对左右子节点的 hash 摘要如 `D = hash(1, 2)`, `B = hash(D, E)`。

树的根即 root hash (也叫 merkle root) 是对整棵树的摘要。

Merkle Tree 使用加密学 hash 方法保证安全性，只有以同样顺序插入同样的叶子节点才可以算出一致的 root hash。现在常用的 256 位 hash 碰撞的几率为 `1 / 2 ** 256`，几乎不会在现实中发生[碰撞][Hash Collision]。

Bitcoin 在区块头保存了交易列表的 merkle root，节点同步交易列表时通过计算 merkle root 并与块头的 `hashMerkleRoot` 对比来确认交易列表是否正确。

Merkle tree 的另一个特性，是可以证明某个元素是否是 merkle tree 的成员。

``` bash
// 比特币交易列表的 Merkle Tree

             A
           /   \
         B       C.
       /  \      / \
      D.    E   F    G
     / \  /  \ / \  / \
     1 2 (3) 4. 5 6 7 8
```

我们发现，仅用图中标识 `.` 的节点就可以计算出 merkle root，我们可以计算从 tx3 到 merkle root 之间的中间节点 `E = hash(tx3, tx4)`，`B = hash(D, E)`，`A = hash(B, C)`。
计算过程恰好是叶子节点 `tx3` 到 merkle root `A` 的路径 `tx3 -> E -> B -> A`，所以也叫做 merkle path。

利用这个特性我们可以向只有 `merkle root` 的人证明 `tx3` 是这个 merkle tree 的成员。
证据就是 `tx4, D, C`，这是 `tx3` 的 merkle proof。

Merkle proof 大小是 `树高度 - 1`, 叶子节点数量为 `n` 时，merkle proof 中 hash 数量为 `log(n)`，

Bitcoin 轻节点的 SPV 就是依赖 merkle proof，不需要发送完整交易列表，只需发送 `log(txs_count)` 个 hash 就可以证明块中包含某个交易。

全节点生成 Merkle 证明算法如下:

1. 从树中需要证明的节点节点开始
2. 找到兄弟节点将其加入 proof
3. 跳转到父节点，如果抵达 root 节点则停止，否则回到第 2 步

## Merkle Mountain Range

Merkle Mountain Range (简称 MMR) 是 Peter Todd 提出的一种 Merkle Tree，被 Open timestamp 和 Grin 等项目使用，轻节点协议 Fly client 的论文中也使用 MMR 来做 Merkle proof。

MMR 被设计为 append only, 节点插入后就不会被修改，支持动态的插入。

MMR 和比特币的 Merkle tree 相比，更适合需要动态插入的场景。

比如 Fly client 协议的需求，对整条链中的区块头计算 merkle root 并放入下一个区块头中。如果每个块都重新构造这么庞大的 merkle tree 计算量会非常大，使用 MMR 可以动态的插入新区块头并计算 root hash。

而比特币 Merkle tree 的场景是静态的，在构造树前就已知整个交易列表，且列表不会变化。

MMR 的特点是 append only, 因为这个特性，我们可以用插入顺序作为节点的坐标。

``` bash
// Height
3              14
             /    \
            /      \
           /        \
          /          \
2        6            13
       /   \        /    \
1     2     5      9     12     17
     / \   / \    / \   /  \   /  \
0   0   1 3   4  7   8 10  11 15  16 18
```

如图所述，插入了 11 个叶子节点的 MMR，节点数字代表插入的顺序，同时也是节点的坐标。

当插入新节点时，如果出现了同样高度的树，则需要进行合并。

``` bash
// Height
3              14
             /    \
            /      \
           /        \
          /          \
2        6            13           21
       /   \        /    \       /    \
1     2     5      9     12     17     20
     / \   / \    / \   /  \   /  \   /  \
0   0   1 3   4  7   8 10  11 15  16 18  19
```

插入第 12 个叶子节点(节点 19)，因为 `18` 和 `19` 高度相同，合并两个叶子得到 `20`, 此时 `17` 和 `20` 高度相同，合并得到 `21`。

可以注意到，合并节点的次数和树的高度有关，树高为 `log(n)`, 增加叶子节点时最差的情况下需要插入 `log(n) + 1` 个节点。 

### MMR add

从图中可以观察到

* 父节点和左子节点 offset 为  `2 ** height`
* 兄弟节点间的 offset 为 `2 ** (height + 1) - 1`

利用这些特性可以计算出任意节点的兄弟节点和父节点的坐标。

MMR 插入操作需要判断是否合并，有两种做法：
一是判断节点高度和兄弟节点的高度是否相同，高度相同则进行合并；
二是计算下一个节点的高度，如果高于当前节点则需要合并。

``` python
# 一个简单的做法:
# 1. 尝试找左侧的兄弟节点的高度
# 2. 高度与当前节点相同则合并
class MMR(object):
    def __init__(self, hasher=hashlib.blake2b):
        self.pos_height = []

    def need_merge(self, pos, height):
        left_sibling_pos = pos - sibling_offset(pos)
        return self.pos_height[left_sibling_pos] == height
```

这个算法比较简单直观，弊端是 MMR 必须维护一个数组来保存节点坐标和对应高度。

我们注意节点的高度只和节点坐标有关，能否通过节点坐标来计算出对应的高度？

观察图中最左侧的树可以发现不同高度的子树坐标隐含了节点数量，比如 6 为根的子树共有 (0 ~ 6) 7 个节点， 14 为根的树共有 (0 ~ 14) 15 个节点。
如果将坐标变为从 1 开始, 子树根坐标就恰好等于节点数。

``` bash
// Grin 使用的算法，使用 1 based 二进制来表示节点坐标
Height

2        111
       /     \
1     11     110       1010
     /  \    / \      /    \
0   1   10 100 101  1000  1001  1011
```

每次高度上升，左子树要合并同样 n 节点的右子树并新增一个父节点，实际上相当于计算 `(n << 1) + 1`。
表现在二进制则是图中最左侧根坐标 `1, 11, 111, 1111` 这样的形式, 恰好是高度加一。

我们从任何一个坐标开始(比如 1010)，将坐标不断向左跳转，直到坐标所有 bits 为 1，代表我们到达了最左侧节点，就可以得到高度。
因为坐标从 1 开始，和节点数量一致，我们发现将坐标向左跳转，相当于将左侧的树整个删除。

``` bash
Height

2        111
       /     \
1     11     110       1010
     /  \    / \      /    \
0   1   10 100 101  1000  1001  1011

// 删除掉整个左侧树后，1010 坐标变成了 11

1     11
     /  \
0   1   10 100
```

从 `1010` 坐标开始，减去左侧树(当前坐标最高有效位减一 `1000 - 1 => 111`), 可以向左跳转 `1010 - (1000 - 1) => 11`，不断重复这个过程直到得到全部 bits 为 1 的坐标。

``` python
def tree_pos_height(pos: int) -> int:
    # 转换为从 1 开始的坐标
    pos += 1

    def all_ones(num: int) -> bool:
        return (1 << num.bit_length()) - 1 == num

    def jump_left(pos: int) -> int:
        most_significant_bits = 1 << pos.bit_length() - 1
        return pos - (most_significant_bits - 1)

    # loop until we jump to all ones position, which is tree height
    while not all_ones(pos):
        pos = jump_left(pos)
    # count all 1 bits
    return pos.bit_length() - 1
```

有了 `tree_pos_height` 方法，我们可以写入如下插入方法。

``` python
class MMR(object):
    def __init__(self, hasher=hashlib.blake2b):
        self.last_pos = -1
        self.pos_hash = {}
        self._hasher = hasher

    def add(self, elem: bytes) -> int:
        """
        Insert a new leaf
        """
        self.last_pos += 1
        hasher = self._hasher()
        hasher.update(elem)
        # 保存叶子节点的 hash
        self.pos_hash[self.last_pos] = hasher.digest()
        height = 0
        pos = self.last_pos
        # 判断是否需要合并节点
        # tree_pos_height 根据节点坐标计算节点所在高度
        # 如果下个插入节点高度大于当前高度，代表需要合并
        while tree_pos_height(self.last_pos + 1) > height:
            # 合并的父节点坐标
            self.last_pos += 1
            # 左子树
            left_pos = self.last_pos - (2 << height)
            # 右子树
            right_pos = left_pos + sibling_offset(height)
            hasher = self._hasher()
            # 合并 Hash
            hasher.update(self.pos_hash[left_pos])
            hasher.update(self.pos_hash[right_pos])
            self.pos_hash[self.last_pos] = hasher.digest()
            height += 1
        return pos

# get left or right sibling offset by height
def sibling_offset(height) -> int:
    return (2 << height) - 1
```

### MMR get_root

MMR 可能会出现多个“山峰”，要把多个山峰合并为一个 root hash，
这个操作被称为 "拱起"（Bagging）。

``` bash
// Height
3              14
             /    \
            /      \
           /        \
          /          \
2        6            13
       /   \        /    \
1     2     5      9     12     17
     / \   / \    / \   /  \   /  \
0   0   1 3   4  7   8 10  11 15  16 18
```

"拱起" 操作从最右侧山峰，依次向左合并，直到只剩下 root hash。

如图 root hash 等于 `hash(hash(Node(18), Node(17)), Node(14))`

只要能够找到所有山峰的坐标, 再进行 "拱起" 就可以得到 root hash。 因为 MMR 会不断合并子树，左侧的山峰一定是是个尽可能大的平衡二叉树，且节点数量为 `1 << height + 1`。

在确定 MMR 节点数量为 `mmr_size` 的情况下，我们可以不断的尝试左侧山峰的高度，计算山峰的二叉树节点数量 `1 << height + 1` 找到小于 `mmr_size` 的最大的树，此时的 height 就是左侧山峰的高度。

使用上一节的二进制节点坐标，可以从 height 转换为山峰的坐标。

``` python
def left_peak_height_pos(mmr_size: int) -> Tuple[int, int]:
    def get_left_pos(height):
        """
        将高度转为从 1 开始的二进制的节点坐标: (1 << height + 1) - 1
        再减去 1 得到从 0 开始的坐标
        """
        return (1 << height + 1) - 2
    height = 0
    prev_pos = 0
    pos = get_left_pos(height)
    # 每次增加 height 1 尝试计算坐标
    # 如果坐标超出当前的 mmr_size，代表前一次结果正确
    while pos < mmr_size:
        height += 1
        prev_pos = pos
        pos = get_left_pos(height)
    return (height - 1, prev_pos)
```

计算出左侧山峰后，通过以下步骤寻找下一个山峰

1. 以左侧山峰为当前坐标
2. 跳到当前坐标的右侧兄弟
3. 再跳到左侧子节点，如高度低于 0 则代表山峰不存在
4. 如果坐标小于 mmr size 则该坐标是山峰，否则回到第 3 步

``` python
def get_peaks(mmr_size) -> List[int]:
    def get_right_peak(height, pos, mmr_size):
        # 跳到兄弟节点
        pos += sibling_offset(height)
        # 跳到左侧子节点
        while pos > mmr_size - 1:
            height -= 1
            if height < 0:
                # no right peak exists
                return (height, None)
            pos -= 2 << height
        return (height, pos)

    poss = []
    height, pos = left_peak_height_pos(mmr_size)
    poss.append(pos)
    # 高度为 0 时代表找到了所有的山峰
    while height > 0:
        height, pos = get_right_peak(height, pos, mmr_size)
        if height >= 0:
            poss.append(pos)
    return poss
```

最后进行 "拱起" 得到 root hash

``` python
class MMR(object):
    def get_root(self) -> Optional[bytes]:
        # 所有山峰坐标
        peaks = get_peaks(self.last_pos + 1)
        # 合并
        return self._bag_rhs_peaks(-1, peaks)

    def _bag_rhs_peaks(self, peaks: List[int]
                       ) -> Optional[bytes]:
        rhs_peak_hashes = [self.pos_hash[p] for p in peaks]
        while len(rhs_peak_hashes) > 1:
            # 合并右山峰和左山峰
            peak_r = rhs_peak_hashes.pop()
            peak_l = rhs_peak_hashes.pop()
            hasher = self._hasher()
            hasher.update(peak_r)
            hasher.update(peak_l)
            rhs_peak_hashes.append(hasher.digest())
        if len(rhs_peak_hashes) > 0:
            return rhs_peak_hashes[0]
        else:
            return None
```

### MMR gen_proof

MMR 构造 Merkle proof 非常简单：

1. 构造从叶子节点到山峰的 merkle proof
2. 拱起右侧的山峰，将结果加入 proof
3. 将左侧的山峰从右到左加入 proof

``` bash
// Height
3              14
             /    \
            /      \
           /        \
          /          \
2        6            13           21
       /   \        /    \       /    \
1     2     5      9     12     17     20     24
     / \   / \    / \   /  \   /  \   /  \   /  \
0   0   1 3   4  7   8 10  11 15  16 18  19 22  23 25
```

例子：构造叶子节点 `15` 的 Merkle proof

1. 构造 `15` 到山峰的 `21` Merkle proof，proof = `16, 20`
2. 拱起右侧山峰，右侧只有 `24` 和 `25`，结果为 `hash(25, 24)` 加入 proof，proof = `16, 20, hash(25, 24)`。
3. 将左侧的山峰从右到左的插入 proof，左侧只有 `14`，所以最终的 proof 为 `16, 20, hash(25, 24), 14`。

``` python
class MMR(object):
    def gen_proof(self, pos: int) -> 'MerkleProof':
        proof = []
        height = 0
        # 构造叶子节点到山峰的 Merkle proof
        while pos <= self.last_pos:
            pos_height = tree_pos_height(pos)
            next_height = tree_pos_height(pos + 1)
            if next_height > pos_height:
                # get left child sib
                sib = pos - sibling_offset(height)
                # break if sib is out of mmr
                if sib > self.last_pos:
                    break
                proof.append(self.pos_hash[sib])
                # goto parent node
                pos += 1
            else:
                # get right child
                sib = pos + sibling_offset(height)
                # break if sib is out of mmr
                if sib > self.last_pos:
                    break
                proof.append(self.pos_hash[sib])
                # goto parent node
                pos += 2 << height
            height += 1
        peak_pos = pos
        peaks = get_peaks(self.last_pos + 1)
        # 拱起右侧的山峰
        rhs_peak_hash = self._bag_rhs_peaks(peak_pos, peaks)
        if rhs_peak_hash is not None:
            proof.append(rhs_peak_hash)
        # 从右向左插入左侧的山峰
        proof.extend(reversed(self._lhs_peaks(peak_pos, peaks)))
        return MerkleProof(mmr_size=self.last_pos + 1,
                           proof=proof,
                           hasher=self._hasher)
```

验证 Merkle proof 时按照同样顺序计算 Merkle Root 即可

``` python
class MerkleProof(object):
    def __init__(self, mmr_size: int,
                 proof: List[bytes],
                 hasher):
        """
        MMR Merkle Proof
        包含 mmr_size 和 proof 列表
        """
        self.mmr_size = mmr_size
        self.proof = proof
        self._hasher = hasher

    def verify(self, root: bytes, pos: int, elem: bytes) -> bool:
        """
        root - MMR root
        pos - 验证的叶子节点坐标
        elem - 验证的叶子节点内容
        """
        peaks = get_peaks(self.mmr_size)
        hasher = self._hasher()
        hasher.update(elem)
        elem_hash = hasher.digest()
        height = 0
        for proof in self.proof:
            hasher = self._hasher()
            # 判断是否进入验证山峰的阶段
            if pos in peaks:
                if pos == peaks[-1]:
                    hasher.update(elem_hash)
                    hasher.update(proof)
                else:
                    hasher.update(proof)
                    hasher.update(elem_hash)
                    pos = peaks[-1]
                elem_hash = hasher.digest()
                continue

            # 验证子树的 Merkle proof
            pos_height = tree_pos_height(pos)
            next_height = tree_pos_height(pos + 1)
            # 如果下个标作高度更高，证明当前是右子节点，否则当前为左子节点
            if next_height > pos_height:
                hasher.update(proof)
                hasher.update(elem_hash)
                pos += 1
            else:
                hasher.update(elem_hash)
                hasher.update(proof)
                pos += 2 << height
            elem_hash = hasher.digest()
            height += 1
        return elem_hash == root
```

## 参考

Merkle Mountain Range 的结构和名字一样非常容易理解，但想要正确的实现则需要掌握一些 trick, 文中使用的坐标计算算法大部分是参考自 Grin 的文档和源码。

Merkle proof 在轻节点协议中非常重要，我最近在做 Nervos CKB 轻节点的 POC 研究，后续会在博客里介绍更多 Nervos CKB 相关的技术。

1. [Merkle Mountain Range][Merkle Mountain Range]
2. [Grin MMR 文档][Grin MMR]
3. [Grin 源码注释 根据坐标计算高度][Grin Binary Encoded Tree]
4. [mmr.py 完整的 MMR 实现][mmr.py]
5. [3Blue1Brown 256 位碰撞的概率][Hash Collision]

[Merkle Mountain Range]: https://github.com/opentimestamps/opentimestamps-server/blob/master/doc/merkle-mountain-range.md
[Grin MMR]: https://github.com/mimblewimble/grin/blob/master/doc/mmr.md
[Grin Binary Encoded Tree]: https://github.com/mimblewimble/grin/blob/0ff6763ee64e5a14e70ddd4642b99789a1648a32/core/src/core/pmmr.rs#L606
[mmr.py]: https://github.com/jjyr/mmr.py
[Hash Collision]: https://www.bilibili.com/video/av12467314

