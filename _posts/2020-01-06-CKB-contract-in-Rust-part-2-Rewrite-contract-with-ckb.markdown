---
layout: post
title: "Rust contract, part 2 - Write contract with ckb-std"
data: 2020-01-06 12:06
comments: true
tags: Rust CKB English
---

> Edited at 2020-03-27
>
> * Update `ckb-std` and `ckb-tool`

This article introduces the `ckb-std` library; and shows how to rewrite our minimal contract with `ckb-std`, to enables syscalls and `Vec`, `String`.

The previous contract:

``` rust
#![no_std]
#![no_main]
#![feature(asm)]
#![feature(lang_items)]

#[no_mangle]
pub fn _start() -> ! {
    exit(0)
}

/// Exit syscall
pub fn exit(_code: i8) -> ! {
    unsafe {
        // a0 is _code
        asm!("li a7, 93");
        asm!("ecall");
    }
    loop {}
}

#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[lang = "eh_personality"]
extern "C" fn eh_personality() {}

#[no_mangle]
pub fn abort() -> ! {
    panic!("abort!")
}
```

## Makefile

We compile and run tests again and again in the previous article, for convenient, let's write a `Makefile` first:

``` sh
test: clean build patch
	cargo test -- --nocapture

build:
	cd contract && cargo build

clean:
	cd contract && cargo clean

C := contract/target/riscv64imac-unknown-none-elf/debug/contract
patch:
	ckb-binary-patcher -i $C -o $C

```

The `make test` is simple: rebuild the contract binary then run unit tests.

It is worth to notice the `patch` task, which calls `ckb-binary-patcher` to patch the contract binary; Its a solution for fixing VM's buggy instructions, even we developed the CKB-VM diligently, there no bug-free software. Unfortunately, as the nature of blockchain, we can't just fix the VM without a hard-fork. A better approach is to patch binary to get across the buggy instruction. You can see [this issue](https://github.com/nervosnetwork/ckb-vm/issues/92) for details.

Installing the `ckb-binary-patcher`:

``` sh
cargo install --git https://github.com/xxuejie/ckb-binary-patcher.git
```

Then type `make test` to compile and test contract.

## Hidden complexity under macro

Now let's get back to our contract, the code is little complicated for a "hello world". Let's slim it, we begin with wrapping `_start` function:

``` rust
#[no_mangle]
pub extern "C" fn _start() -> ! {
    exit(main())
}

pub fn main() -> i8 {
    // code...
    0
}
```

Now we can write code in the `main` function, that's looking more comfortable, except the `_start` function is annoying; we can use a macro to hide the `_start`:

``` rust
#[macro_export]
macro_rules! entry {
    ($main:path) => {
        #[no_mangle]
        pub extern "C" fn _start() -> ! {
            let f: fn() -> i8 = $main;
            ckb_std::syscalls::exit(f())
        }
    }
}
```

The `entry` macro defines the `_start` function which just calls main then exits the program with syscall `exit`; our contract code is below:

``` rust
pub fn main() -> i8 {
    // code...
    0
}

entry!(main);
```

The Rust macro system is powerful, we can hidden other annoying functions and definitions under the macro; this is the basic idea of `ckb-std`; let's refactor the contract with `ckb-std`:

``` rust
#![no_std]
#![no_main]
#![feature(lang_items)]
#![feature(alloc_error_handler)]
#![feature(panic_info_message)]

use ckb_std::{entry, default_alloc};

#[no_mangle]
pub fn main() -> i8 {
    // code...
    0
}

entry!(main);
// define global allocator
default_alloc!();
```

This code looks good enough for a "hello world" program. The `rustc` requires the definition of features in the file, so we still need to keep them, but we hide other functions include a well-implemented panic handler and a global allocator in macros.

## ckb std

Let's try using `Vec`, `String` from [alloc](https://doc.rust-lang.org/stable/std/alloc/index.html) crate, and use the debug syscall to output under the test environment.

``` rust
/// features...

use alloc::vec;
use ckb_std::{debug, entry, default_alloc};

#[no_mangle]
pub fn main() -> i8 {
    let v = vec![0u8; 42];
    debug!("{:?}", v.len());
    0
}

entry!(main);
default_alloc!();

// We can see the debug output under test environment.
// ->
// 0x423f33c96845ca512f4c9e9b19015481a4a8db1cf56dd1ddff8cecc17c38ac5d [contract debug] 42
```

References:

* [ckb-rust-demo](https://github.com/jjyr/ckb-rust-demo/tree/part2)
* [ckb-std](https://github.com/jjyr/ckb-std)
* [alloc crate](https://doc.rust-lang.org/stable/std/alloc/index.html)
* [ckb-binary-patcher](https://github.com/xxuejie/ckb-binary-patcher)
