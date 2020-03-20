---
layout: post
title: "Introducing Godwoken - A missing piece of the cell model"
data: 2020-03-03 16:15
comments: true
---

For developers, the cell programming model certainly is the most interesting part of Nervos CKB.

There is a short description:

* Cell is generalized UTXO.
* A cell is a UTXO contains arbitrary data and customizable scripts.
* When tx tries to consume or creates a cell, cell's scripts will be loaded and executed, any error returned by scripts will fail the tx.

Cell model is very different compares to account model:

* do verification instead of computing
* store data in separate cells instead of store data in an account

There are many other differences when you compare two models, but we only talk about things related to today's topic, you can find more discussions about cell model vs account model on [nervos talk].

## A missing piece of the cell model

UTXO model is great, and Cell model inherited it's flexible. We can [issue UDT](https://talk.nervos.org/t/rfc-simple-udt-draft-spec/4333)(user-defined token, like ERC-20), deposit on-chain assets, play paper-rock-scissors, or [atomic swap with bitcoin](https://talk.nervos.org/t/summa-bitcoin-spv-utils/4162). Cell model can achieve many things that people don't think it is possible at first thought.

But unfortunately, some contracts that certainly are hard to be implemented on the cell model:

* Voting
* ICO
* Decentralized price oracle
* ...

A common pattern of these hard-problem contracts is the requirement of a shared state.

In a UTXO-like model, the state is naturally separated.

In CKB, users can vote in separate cells. An off-chain actor collects voting cells and calculates the result.

![voting in separate cells](/assets/images/godwoken1/voting.jpg)

It works fine when we only want to "see" the result. But we can't use the voting result in another contract, for example, a voting based DAO contract. It's hard to verify the aggregated result in an on-chain contract. Since we need to prove exists of voting cells, the transaction must refer to every voting cell; it could be costly.

![voting result](/assets/images/godwoken1/voting_result.jpg)

For another example, let's think about an ICO contract:

A cell holds all ICO token; a user can pay CKB to get the corresponded amount of the token.

The issue is when we split the cell, the outpoint of the ICO cell is changed; other users must wait to the next block to see the new outpoint. So during a block time, only one user can participate in the ICO; it's unacceptable for an ICO contract.

Like the voting example, a typical solution is to introduce an off-chain actor. Users make ICO requests in individual cells; then, these cells are collected by the off-chain actor and resulted in one cell.

We can see that since the state in the cell model is naturally separated, we must rely on some off-chain actor to collect state.

This solution works, but some questions still open:

* How to efficiently prove the aggregated result
* How do we guarantee the decentralize after introducing the off-chain actor
* How does a user interacts with an off-chain actor

Ok, these questions are not too hard; we can incentive off-chain actors by paying them fees; use some challenge mechanism or zk proof magically verifies the aggregated result; define few protocols to specify the interaction with the actors. We can always solve these problems.

Wait, what I want is just a voting contract. Why do I need to build these things?

## One contract to rule them all

Indeed! we don't want to build these things for every contract, so we only build once:

![One contract to rule them all](/assets/images/godwoken1/one-contract-to-rule-them-all.jpg)

Godwoken is an account-based programming layer build upon CKB that aiming to rule them all. (them: shared state contracts)

Godwoken composited by the following parts:

* Main contract - a type script maintains the global state of all accounts and all blocks(layer-1.5).
* Challenge contract - a type script that handles challenge requests.
* Aggregator - an off-chain program that collects layer-1.5 transactions and submits layer-1.5 blocks to the main contract regularly.
* Validator - an off-chain program that continuously watches the two contracts. The validator sends a challenge request when an invalid block is submitted and sends an invalid challenge request when a wrong challenge request is submitted.

![Godwoken components](/assets/images/godwoken1/godwoken-components.jpg)

You may found this sounds like a rollup solution which popular these days, and yes it is. But we focus on the aggregation problems, rather than the scalabilities. Godwoken provides account-based programming ability to solve the aggregation problem.

Godwoken contract shares the same tech stack with the native CKB contract. The only difference is that Godwoken abstract state of cells into accounts, the contract only cares about accounts, and the Godwoken handle the logic to mapping the account state to layer-1 cells.

For a contract developer, who wants to create a voting contract, simply create an account with a script, the script verifies the input data and the state root of accounts.

``` rust
// pseudo code
fn verify_voting(i, votes) -> bool {
    state[i] += votes;
    merkle_root(state) == output_account_root
}
```

From the pseudo code, we can see the verification model is similar to the layer-1.

The main contract uses a [sparse merkle tree] root to store the accounts and state of accounts.

So if another Godwoken contract wants to use the voting result, it can directly use the result with a merkle proof to prove the result exists in the root.

For a layer-1 contract to use the voting result, we can reference the main contract cell in the transaction's `cell_deps` field, and read the global state to get the merkle root, then verify the voting result with a merkle proof.

By creating an abstract account layer, we minimize the cost of building a shared state contract on CKB.

In later articles, we will discuss the details of Godwoken, how we maintain layer-1.5 accounts and blocks, and how the account-based contract works.

* [Godwoken design document](https://github.com/jjyr/godwoken/blob/master/docs/design.md)
* [Sparse merkle tree](https://justjjy.com/An-optimized-compact-sparse-merkle-tree)

[merkle mountain range]: https://github.com/nervosnetwork/merkle-mountain-range "merkle mountain range"
[sparse merkle tree]: https://github.com/jjyr/sparse-merkle-tree "sparse merkle tree"
[nervos talk]: https://talk.nervos.org "nervos talk forum"
