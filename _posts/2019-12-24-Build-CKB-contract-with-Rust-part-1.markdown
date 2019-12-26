---
layout: post
title: "Build CKB contract with Rust - part 1"
data: 2019-12-24 10:24
comments: true
---

AFAIK, the most popular contracts that deployed on CKB is writing in C, yeah, there are 3 default contracts in the genesis block: `secp256k1 lock`, `secp256k1 multisig lock` and `Deposited DAO`, basically everyone uses CKB are using these contracts.

But as a rustacean, I understand that you want to write everything in Rust. The good news is yes, CKB-VM supports RISC-V ISA(instruction set architecture), and recently the RISC-V target is added to Rust, which means we can directly compile our code to RISC-V. However, the bad news is that the RISC-V target is not supporting the std library yet, which means we only can use `no_std` Rust.

This series of articles show you how to write a CKB contract in Rust and deploy it. We'll see that the `no_std` Rust better than our first impression.

This article assumes you are familiar with Rust and have some basic knowledge of CKB. You should know the CKB transaction structure and understand what a `type` script is and what a `lock` script is. The word `contract` used to describe both `type` script and `lock` script in this article.

## Setup Rust environment

### create a project

Let's initial a project template. Firstly we create two projects: `ckb-rust-demo` and `contract`. The `ckb-rust-demo` used to put our tests code, and the `contract` used to put the contract code.

``` sh
cargo new --lib ckb-rust-demo
cd ckb-rust-demo
cargo new contract
```

### install `riscv64imac-unknown-none-elf` target

We require several unstable features from the nightly Rust version, and then we install the RISC-V target.

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

Edit the `src/main.rs` to enable `no_std`.

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

This is a basic `no_std` main, try compile again:

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

The only thing that the contract does is return `0`. It's perfect for a `lock` script (don't do this on the mainnet!).

The basic idea to write test code is to use our contract as a cell's lock script, our contract return `0`, which means anyone can spend the cell.
Firstly, we mock a cell with our contract as the lock script, then construct a transaction to spend the cell, if the transaction verification succeeded that means our lock script is working.

Add `ckb-contract-tool` as dependent:

``` rust
[dependencies]
ckb-contract-tool = { git = "https://github.com/jjyr/ckb-contract-tool.git" }
```

`ckb-contract-tool` contains helper methods from several crates.

The test code which we put in `ckb-rust-demo/src/lib.rs` as below:

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

Don't panic! The error `OutOfBound` represents our program tries to access some memory that out of bound.

The target `riscv64imac-unknown-none-elf` have a little different behavior on compiling the program entry point, use `riscv64-unknown-elf-objdump -D <binary>` to disassembly we can find out that there no `.text` section, we must write a linker script to indicates the entry point.

## Customize linker script

A basic linker script, including the `.text`, `.sdata`, `.riscv` sections and the entry point: `ENTRY(start)`.

Put the linker script to `contract/linker.ld`

``` sh
MEMORY
{
  MEMORY : ORIGIN = 0x00000000, LENGTH = 1M
}

/* The entry point */
ENTRY(start);

SECTIONS
{
  .text :
  {
    *(.text .text.*);
  } > MEMORY
  .sdata :
  {
    *(.sdata .sdata.*);
  } > MEMORY
  .riscv :
  {
    *(.riscv .riscv.*);
  } > MEMORY
}
```

Modify `contract/.cargo/config` to apply the linker script when compiling:

``` toml
[target.riscv64imac-unknown-none-elf]
rustflags = ["-C", "link-arg=-Tlinker.ld"]
[build]
target = "riscv64imac-unknown-none-elf"
```

Let's compile and run test again:

``` sh
cargo build
cd ..
cargo tests
# ->
---- tests::it_works stdout ----
thread 'tests::it_works' panicked at 'pass test: Error { kind: ExceededMaximumCycles

Script }', src/libcore/result.rs:1188:5
```

`ExceededMaximumCycles` error occurs when the script cycles exceed the max limit. Apparently, our lock only returns a 0. It not supposed to cost many cycles.

The reason is when compiling to `riscv64imac-unknown-none-elf` target. The compiler does not handle the entry point properly. If we disassemble, we find that the entry point `start` is complied as a regular function, when the function returns the `pc` jump to the `0x0` address which is the begin address of the `start` function, so the code loop and loop again until exhausted all cycles.

To break the loop, we need to invoke the `exit` syscall in the `start` function.

## CKB-VM syscall

The CKB environment supports several [syscalls](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md).

The `exit` syscall used to exit and return the exit code, we  rewrite our `start` function like below:

``` rust
#[no_mangle]
#[start]
pub fn start(_argc: isize, _argv: *const *const u8) -> isize {
    exit(0);
    // just ignore this return value, this won't work under riscv64imac-unknown-none-elf target
    0
}
```

To call `exit` from Rust, we need some interesting code:

``` rust
#![feature(asm)]

...

/// Exit syscall
/// https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md
pub fn exit(_code: i8) {
    unsafe {
        // a0 is _code
        asm!("li a7, 93");
        asm!("ecall");
    }
}
```

The `a0` register contains our first arg `_code`, the `a7` register indicates which syscall do we want, `93` is the syscall number of exit.

Compile and rerun the test.

It finally works!

Now you can try to search each unstable `feature` we used and try to figure out what it means. Try to modify the exit code and the `start` function, rerun test see what happened.

## Conclusion

You may wonder why it's so complex to write a CKB contract in Rust, and it is true if you choose C, the thing's become much more straightforward.

The intention of this demo is trying to show you how to use `Rust` to write a contract at a low level. Since the lack of toolchain and libraries, it maybe seems not worth to use `Rust` developing CKB contract.

But with the Rust ecosystem, things could be better. For example, with `cargo`, you can abstract libraries into crates, we can gain a better developing experiment if we just import a syscalls crate instead write it ourselves. More people use `Rust` on CKB, more crates we can use.

The other downside is that Rust target `riscv64imac-unknown-none-elf` is still on a very early stage, it can't handle entry point properly, and do not support `std` library. But it's hopeful of getting better since the RISC-V becomes more popular.

That's it. We'll discuss more serious contracts in later articles.

* [ckb-rust-demo repository](https://github.com/jjyr/ckb-rust-demo)
* [CKB data structure](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0019-data-structures/0019-data-structures.md)
* [CKB syscalls](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0009-vm-syscalls/0009-vm-syscalls.md)
