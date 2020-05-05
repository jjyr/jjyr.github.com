---
layout: post
title: "Break the liquidity limitation of NervosDAO"
data: 2020-05-05 14:26
tags: CKB English
---

I always wonder about breaking the liquidity limitation of NervosDAO since I first learned it from the CKB economic paper.

## NervosDAO's liquidity limitation

For readers who do not know what the NervosDAO is:

NervosDAO is a builtin contract that allows people to deposit CKB into it and get compensation back(to resist part of inflation), the purpose is to control on-chain data storage by providing a negative incentive for who store the data. NervosDAO is a critical part of the CKB economic design; you can learn it from the CKB economic paper.

A typical CKB owner chooses one of the following strategies:

* Deposit CKB into NervosDAO and get compensation, but the user can't uses the CKB until withdrawing it from NervosDAO.
* Store X Bytes data on the chain which occupied X CKB.
* Do nothing, let the coin diluted.
* Find other ways to earn more CKB: investing, lending, ...

For a holder, deposition in NervosDAO is the easiest way to resist (a part of) inflation.

NervosDAO also has an annoying design to limit the liquidity; the withdrawal must be made at `N * 180 epochs` after the deposition, which means we can only withdraw the coin at 180 epochs(~30 days), 360 epochs(~60 days), 540 epochs(~90 days) after the deposition.

Unfortunately(or we should say 'fortunately'), CKB is a powerful programming platform; in a powerful platform, we should be able to do almost anything, including breaking the liquidity limitation of NervosDAO.

## Let's break it

A simple idea comes to my head; I can build a UDT(user-defined token) to 'hijack' NervosDAO (not really hijack the coins from NervosDAO, but tokenize the NervosDAO so that we can hijack the ownership of coins). I name the UDT contract DCKB, so let's use the name for convenience.

The DCKB contract behaviors as following:

* Alice deposit X CKB to NervosDAO, the contract create X DCKB to Alice.
* Alice can send any DCKB to anyone just like sending other UDT.
* The contract creates Y DCKB (corresponds to NervosDAO compensation) to the token owner at every new block height.
* Alice or anyone can destroy X + Y DCKB and withdraw X + Y CKB from NervosDAO.

After the mainnet launch, I confirmed that DCKB is possible from technical; with some casual time, I had implemented the [DCKB] contract.

## Who will use DCKB

Layer2, Defi, and other contracts based on the custodian: Recently, smart contracts are more or less rely on the custodian mechanism; if layer2 / Defi projects allow DCKB as custodian assets, the depositor can get more benefits; it will incentivize more people to participate.

Crypto traders can use DCKB instead of CKB to gain compensation.

Writers and developers who receive CKB as donating can tell their sponsor to use DCKB.

## So do the economic model has broken

Yes, and no.

From some perspective, we do break the liquidity limitation; now, crypto traders can gain compensations without sacrifice the liquidity; It removes some original intended negative incentives for traders.

But at the same time, we also give layer2 / Defi depositors more benefits, IMO for a blockchain network which slogan is 'layer1 for layer2', the layer2 depositors are also significant contributors, the system should incentivize them.

From another perspective, DKCB does not break the core idea of the economic model; the core idea of the CKB economic model is to limit the on-chain data storage. DCKB does not affect this, the CKB is deposited to NervosDAO when the user gets DCKB, so obviously, a DCKB owner can not store on-chain data without occupied new CKB.

I think DCKB keeps the core idea of the economic model while extends it's potential.

## How DCKB works

This article is not focused on the implementation details of the DCKB contract, so I only explain the core part of DCKB. For more information, you should check the [DCKB] source code.

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

I'll continue to collect feedbacks before decide to deploy DCKB to the mainnet.

I hope that every serious layer2 / Defi project should consider allowing DCKB as their custodian assets.

[DCKB]: https://github.com/jjyr/DCKB "DCKB GitHub repo"
[DCKB Wiki]: https://github.com/jjyr/DCKB/wiki "DCKB wiki"
[NervosDAO formula]: https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0023-dao-deposit-withdraw/0023-dao-deposit-withdraw.md#calculation "NervosDAO formula"
