---
layout: post
title: "Introducing Godwoken - A missing piece of the cell model"
data: 2020-03-03 16:15
comments: true
tags: CKB English
---

For developers, the cell programming model certainly is the most interesting part of Nervos CKB.

There is a short description of the cell model:

* Cell is generalized UTXO.
* A cell is a UTXO contains arbitrary data and customizable scripts.
* When tx consume or create a cell, CKB will load and execute the cell's scripts, any error returned by scripts will fail the tx.

The cell model is very different compares to account model:

* Contracts do verification instead of computing
* Data is stored in separate cells instead of an account tree

There are many other differences when you compare two models, but we focus on today's topic, you can find more discussions about cell model vs account model on [nervos talk].

## A missing piece of the cell model

UTXO model is a very flexible model, and the Cell model inherited directly from it plus turing-complete programming ability. We can [issue UDT](https://talk.nervos.org/t/rfc-simple-udt-draft-spec/4333)(user-defined token, like ERC-20), deposite on-chain assets, play paper-rock-scissors, or do [atomic swap with bitcoin](https://talk.nervos.org/t/summa-bitcoin-spv-utils/4162). Cell model can achieve many things that people don't think it is able to at first thought.

But unfortunately, some contracts are certainly harder to be implemented on the cell model:

* Voting
* Crowdfunding
* Decentralized price oracle
* ...

A common pattern of these harder contracts is the requirement of a shared state.

In a UTXO-like model, the state is naturally separated.

In CKB, users can vote in separate cells; an off-chain actor collects voting cells and calculates the result.

![voting in separate cells](/assets/images/godwoken1/voting.jpg)

It works fine if we only want to know the result off-chain. But we can't use the voting result on-chain. The reason is if we want to use the voting result, we must do verification on-chain since we need to prove all the aggregated voting cells exist, the transaction must refer to every voting cell: it will be costly.

![voting result](/assets/images/godwoken1/voting_result.jpg)

Let's take a look for another example, a crowdfunding contract:

We try to use a single cell to hold all crowdfunding token; users can use CKB to exchange the corresponded amount of the token.

The problem is when a user tries to exchange token, the original cell is consumed, and two new cells are created: one contains the tokens to the user, another cell holds rest crowdfunding token; then the outpoint of the crowdfunding cell is changed; other users must wait to the next block to find the new outpoint. So in every block, only one user can participate in crowdfunding; it's unacceptable.

Just like voting, a typical solution is to introduce an off-chain actor. Instead of using one single cell, users make crowdfunding requests in individual cells; then, the off-chain actor collects these cells and aggregate the result in the result cell.

We can see, that since the state in the cell model is naturally separated, we must rely on some off-chain actor to collect state.

This solution works, but some questions still open:

* How to efficiently prove the aggregated result
* How do we guarantee the decentralize after introducing the off-chain actor
* How does a user interacts with an off-chain actor

Ok, we can incentive off-chain actors by paying them fees; use some challenge mechanism or zk proof to magically verifies the aggregated result; define protocols to specify the interaction interface. We can always solve these problems.

Wait, if what I want is just a voting contract. Do I really need to do all these things?

## One contract to rule them all

Indeed! It's too stupid to do all bunch things just for a voting contract. We don't want to build these things for every contract, so we only build once:

![One contract to rule them all](/assets/images/godwoken1/one-contract-to-rule-them-all.jpg)

Godwoken is an account-based programming layer build upon CKB that is aiming to rules shared state contracts.

Godwoken composited by the following parts:

* Main contract - a type script maintains the global state of all accounts and all layer-1.5 blocks.
* Challenge contract - a type script that handles challenge requests.
* Aggregator - an off-chain program collects layer-1.5 transactions and 'mine' layer-1.5 blocks.
* Validator - an off-chain program that continuously watches the contract states. The validator sends a challenge request when an invalid block is submitted.

![Godwoken components](/assets/images/godwoken1/godwoken-components.jpg)

You may found this sounds like a rollup solution which popular these days, and yes it is. But we focus on the aggregation problems rather than the scalabilities. Godwoken provides account-based programming ability to solve the aggregation problem.

> Some people refer to Rollup as layer-1.5; some people think it's layer-2, or even layer-1(by trust-level). In this article we refer Godwoken as layer-1.5 to distinguish it with the layer-1 concepts.

Godwoken shares the same tech stack with the native CKB contract. The only difference is that Godwoken contracts are built upon account-based APIs; Godwoken verifies the state of account instead of the cell. The mapping relationship between account state and layer-1 cells is handled by the Godwoken main contract, which is transparent to layer-1.5 contracts.

For a developer who wants to create a voting contract, can simply create an account with a script, the script verifies the input data and account state.

``` rust
// pseudo code
fn verify_voting(i, votes) -> bool {
    state[i] += votes;
    merkle_root(state) == next_account_root
}
```

The Godwoken main contract uses a [sparse merkle tree] to store all accounts and state of accounts.

If we want to refer to account state in layer-1.5 contracts, we simply generate a merkle proof and verify the proof in the contract.

If we want to refer to a layer-1.5 account state in layer-1 contracts, we can refer the Godwoken main contract cell in the transaction's `cell_deps` field, and read Godwoken global state from the cell to get the merkle root, then verifies the state and merkle proof.

By creating an abstracted account layer, we minimize the work of building a shared state contract on CKB.

In later articles, we will discuss the details of Godwoken, how we maintain layer-1.5 accounts and blocks, and how the account-based contract works.

* [Godwoken design document](https://github.com/jjyr/godwoken-original/blob/master/docs/design.md)
* [Sparse merkle tree](https://justjjy.com/An-optimized-compact-sparse-merkle-tree)

[merkle mountain range]: https://github.com/nervosnetwork/merkle-mountain-range "merkle mountain range"
[sparse merkle tree]: https://github.com/jjyr/sparse-merkle-tree "sparse merkle tree"
[nervos talk]: https://talk.nervos.org "nervos talk forum"
