---
layout: post
title: "Rust contract part 1 - Build CKB contract with Rust"
data: 2019-12-24 10:24
comments: true
tags: Rust CKB English
---

> Edited at 2020-03-27
>
> * Update ckg-std link
> * Remove the linker script section since I found its unnecessary to customize linker
> * Refactor the main function interface

AFAIK, the most popular contracts that deployed on CKB is writing in C. There are 3 default contracts in the genesis block: `secp256k1 lock`, `secp256k1 multisig lock` and `Deposited DAO`, basically everyone uses CKB are using these contracts.

As a rustacean, I understand that you want to write everything in Rust. The good news is it's possible, since CKB-VM supports RISC-V ISA(instruction set architecture), and recently the RISC-V target is added to Rust, which means we can directly compile our code to RISC-V. However, the bad news is that the RISC-V target is not supporting the std library yet, which means you can't use Rust as a usual way.

This series of articles show you how to write a CKB contract in Rust and deploy it. We'll see that the `no_std` Rust is better than our first impression.

This article assumes you are familiar with Rust and have some basic knowledge of CKB. You should know the CKB transaction structure and understand what a `type` script is and what a `lock` script is. The word `contract` used to describe both `type` script and `lock` script in this article.

## Setup Rust environment

### create a project

Let's initial a project template. First, we create two projects: `ckb-rust-demo` and `contract`. The `ckb-rust-demo` used to put our tests code, and the `contract` used to put the contract code.

``` sh
cargo new --lib ckb-rust-demo
cd ckb-rust-demo
cargo new contract
```

### install `riscv64imac-unknown-none-elf` target

We choose nightly Rust since several unstable features are required, then we install the RISC-V target.

``` sh
# use nightly version rust
echo "nightly" > rust-toolchain
cargo version # -> cargo 1.41.0-nightly (626f0f40e 2019-12-03)
rustup target add riscv64imac-unknown-none-elf
```

## Compile our first contract

Let's try to compile the contract and see what happened:

``` sh
cd contract
cargo build --target riscv64imac-unknown-none-elf
```

The compiling fails because of no `std` for target `riscv64imac-unknown-none-elf`.

Edit the `src/main.rs` to notate `no_std` flag.

``` rust
#![no_std]
#![no_main]
#![feature(start)]
#![feature(lang_items)]

#[no_mangle]
#[start]
pub fn start(_argc: isize, _argv: *const *const u8) -> isize {
    0
}

#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[lang = "eh_personality"]
extern "C" fn eh_personality() {}
```

The above code is a basic `no_std` main, try compile again:

To avoid typing the `--target` every time, we can write it into a config file `contract/.cargo/config` then update the content:

``` toml
[build]
target = "riscv64imac-unknown-none-elf"
```

Then build:

``` sh
cargo build
file target/riscv64imac-unknown-none-elf/debug/contract
# -> target/riscv64imac-unknown-none-elf/debug/contract: ELF 64-bit LSB executable, UCB RISC-V, version 1 (SYSV), statically linked, with debug_info, not stripped
```

## Test our contract

The only thing that the contract does is to return exit-code `0`. It's perfect for a `lock` script (it's not perfect, don't do it on the mainnet!).

The basic idea to write test code is to use our contract as a cell's lock script, our contract return `0`, which means anyone can spend the cell.
First, we mock a cell with our contract as the lock script, then construct a transaction to spend the cell, if the transaction verification succeeded that means our lock script is working.

Add `ckb-tool` as dependent:

``` rust
[dependencies]
ckb-tool = { git = "https://github.com/jjyr/ckb-tool.git" }
```

`ckb-tool` contains helper methods from several crates.

The test code which put in `ckb-rust-demo/src/lib.rs` as below:

``` rust
#[test]
fn it_works() {
    // load contract code
    let mut code = Vec::new();
    File::open("contract/target/riscv64imac-unknown-none-elf/debug/contract").unwrap().read_to_end(&mut code).expect("read code");
    let code = Bytes::from(code);

    // build contract context
    let mut context = Context::default();
    context.deploy_contract(code.clone());
    let tx = TxBuilder::default().lock_bin(code).inject_and_build(&mut context).expect("build tx");

    // do the verification
    let max_cycles = 50_000u64;
    let verify_result = context.verify_tx(&tx, max_cycles);
    verify_result.expect("pass test");
}
```

1. Load contract code.
2. Build a context. The `TxBuilder` helps us inject a mocked cell into the context with our contract as the cell's lock script, then construct a transaction to spend the cell.
3. Do verification.

Let's try it:

``` sh
cargo test
# ->
---- tests::it_works stdout ----
thread 'tests::it_works' panicked at 'pass test: Error { kind: InternalError { kind: Compat { error: ErrorMessage { msg: "OutOfBound" } }

VM }

Internal }', src/libcore/result.rs:1188:5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace.
```

Don't panic! The error tells us our program access some memory that out of bound.

The `riscv64imac-unknown-none-elf` target is little different on handling the entry point, use `riscv64-unknown-elf-objdump -D <binary>` to disassembly we can find out that there no `.text` section, we must find the other way to indicates the entry point other than using `#[start]`.

## Define the entry point and main

Let's remove the entire `#[start]` function, insteadly define a function with name `_start` as entry point:

``` rust
#[no_mangle]
pub fn _start() -> ! {
    loop{}
}
```

The return value of `_start` is `!`, which means this function never returns; if you try to return from this function, you get an `InvalidPermission` error, since the entry point has no place to return.

Let's compile it:

``` sh
cargo build

# -> rust-lld: error: undefined symbol: abort
```

We define an `abort` function to passing the compile.

``` rust
#[no_mangle]
pub fn abort() -> ! {
    panic!("abort!")
}
```

Compile and run test again:

``` sh
cargo build
cd ..
cargo tests
# ->
---- tests::it_works stdout ----
thread 'tests::it_works' panicked at 'pass test: Error { kind: ExceededMaximumCycles

Script }', src/libcore/result.rs:1188:5
```

`ExceededMaximumCycles` error occurs when the script cycles exceed the max cycle limitation.

To exit the program, we need to invoke the `exit` syscall.

## CKB-VM syscall

The CKB environment supports several [syscalls](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md).

We need call `exit` syscall to exit program and return a exit code:

``` rust
#[no_mangle]
pub fn _start() -> ! {
    exit(0)
}
```

To invoke syscall `exit` from Rust, we need to write some interesting code:

``` rust
#![feature(asm)]

...

/// Exit syscall
/// https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md
pub fn exit(_code: i8) -> ! {
    unsafe {
        // a0 is _code
        asm!("li a7, 93");
        asm!("ecall");
    }
    loop {}
}
```

The `a0` register contains our first arg `_code` according to the function calling convention, the `a7` register indicates the syscall number, `93` is the syscall number of exit. We mark the return value with `!` since `exit` should never return.

Compile and rerun the test.

It finally works!

Now you can try to search each unstable `feature` we used and try to figure out what it means. Try to modify the exit code and the `_start` function, rerun the test see what happened.

## Conclusion

The intention of this demo is trying to show you how to use `Rust` to write a CKB contract from a low-level sight. The real power of Rust is the abstract ability of the language and the Rust toolchain, which we do not touch in this article.

For example, with `cargo`, we can abstract libraries into crates; we gain a better developing experiment if we can just import a syscalls crate instead write it ourselves. More people use `Rust` on CKB, more crates we can use.

Another advantage to use Rust is that in CKB, the contract only does verification. Aside from on-chain contracts, we also need to write an off-chain program to generate transaction data. That means we may need to write duplicated code if we use different languages, but with Rust, we can use the same code across the contract and the generator.

Write a CKB contract in Rust may seem a little bit complex; you may wonder the thing could get much more straightforward if you choose C, and you are right, just for now!

In the next article, I'll show you how to rewrite our contract with `ckb-std` library; you'll surprise how simple thing goes.

That's it. We'll also discuss more serious contracts in later articles.

* [CKB contract in Rust - part 2](https://justjjy.com/CKB-contract-in-Rust-part-2-Rewrite-contract-with-ckb)
* [ckb-rust-demo repository](https://github.com/jjyr/ckb-rust-demo)
* [ckb-std repository](https://github.com/jjyr/ckb-std)
* [CKB data structure](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0019-data-structures/0019-data-structures.md)
* [CKB syscalls](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md)
