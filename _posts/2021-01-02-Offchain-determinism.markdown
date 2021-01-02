---
layout: post
title: "Off-chain determinism"
data: 2021-01-02 12:19
tags: CKB blockchain English
---

### How to get the current block number

Several times, I have heard developers complain about why can't they read the current block number in their CKB scripts(smart contract)?

Every blockchain developer knows it is a fundamental feature of Ethereum and other blockchains that use EVM.  So if CKB, like it says, is the next-generation blockchain, why can't it do the thing that the last generation blockchain can do?

Well, I guess very few people can answer it; The core team doesn't frequently explain the unique design of CKB to the community, which I think the core team should do better.

So I decide to write this article to explain the trade-off of this design: why can't we read the current block number in the script.

### The right way to do it

First, let's see the right way to read the block number in the CKB script.

By my observation, almost all developers ask for the block number is for measuring the block time between two actions, in the abstract: a user makes a deposition at the block height X, then withdraws the money at the block height Y. After the withdrawal, the developer wants to calculate the blocks during X and Y, so they can send a reward according to the user's deposition time or do other things similar.

Ethereum can directly read the block number of the current block and calculate the reward. But in CKB, instead of directly read the block number, we must use other methods:

1. We can use [transaction valid since] to constraint the withdrawal tx, to ensure it is at least send after Z blocks since the deposition. However, the user can delay the tx for a longer time than Z. It maybe not appropriate for some situations.
2. We can use two steps withdrawal to locate block height. In the first step, we read the deposition block height X by using [CKB syscalls], then record the X in the new prepare-withdrawal cell; in the second step, we use syscall to read the height of the prepare-withdrawal cell Y and read the X from the cell's data. So we can calculate the block time Y - X.

![Two steps withdrawal](/assets/images/offchain-determinism/two steps withdrawal.png)

### The off-chain determinism

So what's the point of this? Clearly, developers prefer the simple and intuitive method, so why the CKB uses such a hard way to do a simple job?

It is all for the **off-chain determinism**. Let's start the explanation from a question: What is the input of the Ethereum contract? What is the input of the CKB script?

If we think of the contract(or script) as a function `f`, then we can express the calculation of the smart contract in the following form:

In Ethereum:

``` javascript
output = f(tx, state tree, current blockchain)
```

In CKB:

``` javascript
output = f(tx, deterministic blockchain)
```

In Ethereum, a contract can read information from three inputs: tx, account state tree, or the current blockchain status. For example, current block number or block hash.

In CKB, we only allow a script to read deterministic inputs; even if a user wants to read information from the blockchain, the user must include the block's hash in the tx in the first place. So all information that a script can read is deterministic. We called it off-chain determinism, which is an essential feature of CKB.

### The benefit

Off-chain determinism brings few benefits; the most important one is that once we verify a tx, we know the tx will always be valid or invalid since it is deterministic. The verification result doesn't depend on blockchain status.

The determinism introduces a verification strategy in the CKB; we only verify a tx once before pushing it into the memory pool. When we package txs into a block, we only need to check the tx inputs are still unspent; this cost is very light compared to execute a complete verification for a tx.

This off-chain deterministic of tx is not only bound to one node; We can guarantee that a tx is valid even if we send it across the P2P network. Because once a tx is valid will always be valid, so the CKB only broadcast valid txs to other nodes. If a malicious node tries to broadcast invalid txs, network peers will immediately ban the node once they fail to validate a tx send by the node. Because invalid txs can't get broadcast into the CKB network anyway, the CKB only packages valid txs into blocks. Which I think is a significant advantage of CKB.

Note that it is impossible in Ethereum because Ethereum tx is not off-chain determinism; even a tx is valid on block number 41, it may fail on block number 42, so we never know if a failed tx is intended sent by a malicious peer or it failed because of the tip block change. Thus, Ethereum chose another way; Ethereum allows nodes to broadcast invalid txs and package them into the block. Then the protocol lets the miner take the max fee from the user to penalize failure txs. The purpose of this mechanism is to enhance security by incentivizing users to only send valid txs; but even you are an honest user, you may sometimes send a failed tx by accidentally running into an invalid contract state. (I have lost about 50$ in a failed tx when I try to deposit into Curve.)

Whether to include only valid txs in the block or include failed txs in the block then to penalize the sender, such different design philosophies are from different answers to the simple question:  Should we let a script read the current block number?

### Layer1 robust vs. user experience

From my understanding, between the layer1 robustness and the user experience, the design of CKB clearly chooses the former.

And I think the choice is right; the most and the only important thing of the layer1 blockchain is to provides robustness and safety service. And this trade-off doesn't mean that CKB doesn't care about users' experience. Remember the slogan of CKB: a layer1 built for layer2. And in this case, layer1 is made for robustness, and layer2 is made for user experience.

In layered architectures, most people should use a higher-layer technique, and only a few people need to access from the lower-layer. For example, most users use HTTP or WebSocket; fewer people use TCP or UDP, and almost no-one uses IP directly.

So from the smart contract developers' view, can't read the current block number from the script makes no sense. But once you bring yourself into a layered architecture's view, you can see the design is natural and fundamental.

Once the layer2 of CKB is enabled, you should see how easy the developer access more features from layer2, and it is far more than reading the block number.

[transaction valid since]: https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0017-tx-valid-since/0017-tx-valid-since.md "Transaction valid since"
[CKB syscalls]: https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md "CKB Syscalls"
