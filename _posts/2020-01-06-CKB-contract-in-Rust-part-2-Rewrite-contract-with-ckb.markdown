---
layout: post
title: "Rust contract, part 2 - Write contract with ckb-contract-std"
data: 2020-01-06 12:06
comments: true
---

This article introduces the `ckb-contract-std` library; and shows how to rewrite our minimal contract with `ckb-contract-std`, to enables syscalls and `Vec`, `String`.

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

## Hidden complexity under macro

It seems too complicated for a "hello world".
 Let's begin with wrapping a `main` function, then call it from the `_start`.

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

That's looking more familiar, except the `_start` function is annoying; we can use a macro to hide the `_start`:

``` rust
#[macro_export]
macro_rules! setup {
    ($main:path) => {
        #[no_mangle]
        pub extern "C" fn _start() -> ! {
            let f: fn() -> i8 = $main;
            ckb_contract_std::syscalls::exit(f())
        }
    }
}
```

The `setup` macro defines the `start` function that the `_start` just calls main then exits the program with syscall `exit`; our contract is below:

``` rust
pub fn main() -> i8 {
    // code...
    0
}

setup!(main);
```

The Rust macro system is powerful, we can hidden other annoying functions and definitions under the macro; it is the basic idea of `ckb-contrac-std`; let's rewrite the whole contract:

``` rust
#![no_std]
#![no_main]
#![feature(lang_items)]
#![feature(alloc_error_handler)]
#![feature(panic_info_message)]

use ckb_contract_std::setup;

#[no_mangle]
pub fn main() -> i8 {
    // code...
    0
}

setup!(main);
```

This code looks suitable for a "hello world" program. The `rustc` requires the definition of the features in the file, so we still need to keep them, but we hide the other functions include a well-implemented panic handler and a global allocator in the `setup` macro.

## Rewrite contract

Let's try using `Vec`, `String` from [alloc](https://doc.rust-lang.org/stable/std/alloc/index.html) crate, and use the debug syscall to output under the test environment.

``` rust
/// features...

use alloc::vec;
use ckb_contract_std::{debug, setup};

#[no_mangle]
pub fn main() -> i8 {
    let v = vec![0u8; 42];
    debug!("{:?}", v.len());
    0
}

setup!(main);

// We can see the debug output under test environment.
// ->
// 0x423f33c96845ca512f4c9e9b19015481a4a8db1cf56dd1ddff8cecc17c38ac5d [contract debug] 42
```

References:

* [ckb-contract-demo](https://github.com/jjyr/ckb-rust-demo/tree/part2)
* [ckb-contract-std](https://github.com/jjyr/ckb-contract-std)
* [alloc crate](https://doc.rust-lang.org/stable/std/alloc/index.html)
