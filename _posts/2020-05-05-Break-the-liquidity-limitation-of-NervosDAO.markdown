---
layout: post
title: "Break the liquidity limitation of NervosDAO"
data: 2020-05-05 14:26
tags: CKB English
---

I always wonder about breaking the liquidity limitation of NervosDAO since I first learned it from the CKB economic paper.

## NervosDAO's liquidity limitation

For readers who do not know what the NervosDAO is:

NervosDAO is a builtin contract that allows people to deposit CKB into it and get compensation back(to resist part of inflation), the purpose is to control on-chain data occupation by providing a negative incentive for users who stores the data. NervosDAO is a critical part of the CKB economic design; you can learn it from the CKB economic paper.

A typical CKB holder chooses one of the following strategies to earn more benefits:

* Deposit CKB into NervosDAO and get compensation, but the user can't use or spend the CKB within NervosDAO lock period.
* Store some data on the chain which per byte data occupies 1 CKB.
* Do nothing, let the coin diluted.
* Find other ways to earn more CKB: investing, lending, ...

For a holder, obviously deposition in NervosDAO is the easiest way to resist (a part of) inflation.

NervosDAO has an annoying design to limit the coin liquidity; the withdrawal must be made at `N * 180 epochs` after the deposition, which means we can only withdraw the coin at 180 epochs(~30 days), 360 epochs(~60 days), 540 epochs(~90 days) after the deposition.

Unfortunately(or should we say 'fortunately'), CKB is a powerful programming platform; in such a powerful platform, we can even write a contract to break the NervosDAO liquidity limitation.

## Let's break it

A simple idea comes to my head; We can build a UDT(user-defined token) to 'hijack' NervosDAO. Ok, let's be clear, the 'hijack' does not means that some exploit exists in the NervosDAO, what we do is to create a token to tracing NervosDAO compensation, so we can hijack(prove) the ownership of NervosDAO coins by destroy the same amount of our UDT. I name the UDT contract DCKB, so let's use the name in the rest of the article.

The DCKB contract behaviors as following:

* Alice deposit X CKB to NervosDAO, the contract creates X DCKB to Alice.
* Alice can send any DCKB to anyone just like sending other UDT.
* The contract creates Y DCKB (corresponds to NervosDAO compensation) to the token owner at every new block height.
* Alice or anyone else can destroy X + Y DCKB to withdraw X + Y CKB from NervosDAO.

After the mainnet launch, I confirmed that the DCKB solution actually works; By spending some casual time, I have implemented the [DCKB] contract.

## Who is the user of DCKB

Layer2, Defi, and other contracts which based on the custodian: Nowadays, smart contracts are more or less rely on the custodian mechanism; if layer2 / Defi projects allow DCKB as a custodian asset, the depositor can get more benefits; it will incentivize more people to participate the deposition.

Crypto traders can use DCKB instead of CKB to pursue better benefits.

Writers and developers can receive DCKB as donating to gain compensation coins.

## So do the economic model has broken

Yes, and no.

From some perspective, we do break some assumption from the original design; now, crypto traders can gain compensations without sacrifice the liquidity; It removes some original intended negative incentives for traders.

But at the same time, we also give layer2 / Defi depositors more benefits, in my opinion for a blockchain which slogan is 'layer1 for layer2', the layer2 depositors are also significant contributors to the system, the system should incentivize them.

From another perspective, DKCB does not break the core idea of the economic model; the core idea of the CKB economic model is to limit the on-chain data occupation. DCKB does not affect this, the same amount of CKB is deposited to NervosDAO when the user creates DCKB, so obviously, a DCKB owner can not store on-chain data without occupying new CKB coins.

I think DCKB keeps the core idea of the economic model while extends it's potential.

## How DCKB works

This article is not focused on the implementation details of the DCKB contract, so I only explain the core part of it. For more information, you should check the [DCKB] source code.

A typical UDT contract contains a `u128` number in the cell to represent the amount of token. DCKB uses an extra `u64` number to represent a block number. So a DCKB cell contains `amount` and `block number`, which represents we have X DCKB at block number N.

We assume Alice has two DCKB cells:

The first cell contains `X1` amount DCKB at block number `N1`, the second cell contains `X2` amount DCKB at block number `N2`, which `N2` is higher than `N1`.

Then Alice transfers all DCKB tokens to Bob:

* DCKB contract load block header of `N1` and `N2` blocks.
* Then recalculate `X1` at `N2` by applies [NervosDAO formula]: `dao_formula(X1, N1_header, N2_header)`.
* Finally, verifies the output cell is `dao_formula(X1, N1_header, N2_header) + X2` DCKB at `N2`.

## Current status

* [DCKB] GitHub repo
* A forked version of [ckb-cli](https://github.com/jjyr/ckb-cli/tree/DCKB/src/subcommands/dckb) that supports DCKB
* [DCKB Wiki], document and testnet deployment status

I'll continue to collect more feedback before I decide to deploy DCKB to the mainnet.

I hope that every serious layer2 / Defi project should consider allowing DCKB as an asset.

[DCKB]: https://github.com/jjyr/DCKB "DCKB GitHub repo"
[DCKB Wiki]: https://github.com/jjyr/DCKB/wiki "DCKB wiki"
[NervosDAO formula]: https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0023-dao-deposit-withdraw/0023-dao-deposit-withdraw.md#calculation "NervosDAO formula"
