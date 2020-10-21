---
layout: post
title: "Rust no-std FAQ"
data: 2020-10-21 02:52
comments: true
tags: Rust English
---

### Why write this?

Sometimes, we need to deploy our code to bare-metal environments. Without the POSIX OS support, we can not use the Rust battery-included std library. The no-std Rust usually scared and confused people, so I write this article to clear the most misunderstanding questions of Rust no-std.

### What is Rust no-std?

In std Rust, which is people default learned version. We can print messages to the console, read from files, and open URLs. All these features are underlayer provided by the execution environment: our operating system. Our OS support printing text to the screen, connect to the internet via socket, or increase memory when we allocate too many data structures on the heap; rust delegate these works to OS via syscalls so we can do all these.

You can look through the [modules of std](https://doc.rust-lang.org/stable/std/#modules) and try to identify which module depends on the OS(hint: net, file, ..); if we do not have an operating system that provides these features, we can't use them.

The no-std Rust is for these no POSIX OS environments. In no-std, Rust only keeps the core features that do not depend on the operating system; we can look at the [core crate](https://doc.rust-lang.org/stable/core/index.html) which is a subset of std crate, you can find many familiar modules exists in the core.

The differences between std and no-std are tiny:

1. In no-std, you can't use std crate, however, you can import mostly modules from core.
2. You can't use heap related modules(box, collections, string, etc.) because the default Rust memory allocator depends on OS syscalls to increase heap memory; unless you implement the global allocator.
3. If you write a bin crate, you must implement a few lang items.

Don't be scared by these unfamiliar terms; to understand these, you need to know a few rustc concepts like language item or global allocator which has been hidden from us in the std environment.

### What is lang item?

Short version: rustc is designed as pluggable; instead of builtin all operations in the compiler, rustc allows users to customize the language features via lang_items.

Long version: [lang-items document](https://doc.rust-lang.org/unstable-book/language-features/lang-items.html)

Mostly lang items are defined in the core crate; however, some lang items are defined in the std; for example, eh_personality is used by the failure mechanism. If you write a no-std bin crate, you need to implement lang items; but if you write a lib crate, you can assume the bin crate defined these lang items, so you don't need to it.

The lang items feature is unstable, which means we can only define lang items in nightly Rust. The Rust team expose some lang items via compiler attribute, it allows us to define some lang items via in the stable Rust, for example: `#[panic_handler]` defines panic_impl lang item, and `#[alloc_error_handle]` defines oom [lang item](https://github.com/rust-lang/rust/issues/51540).

A recommendation is you should always looking for runtimes support crates before you implement them from scratch. The [Rust embedded work group](https://github.com/rust-embedded) is an excellent place to start. They provide several crates to implement lang items for embedded environments; by using these crates, you can forget the lang items and get a better life.

### What is the alloc crate? What is the global allocator?

The alloc crate contains heap related modules, the alloc required the global allocator to allocate heap memory. The std crate defines the default global allocator, and when the heap memory is exhausted, the allocator uses OS syscalls to increase heap memory. So we can't use it under no-std environments. We can use the `#[global_allocator]` attribute to define our allocator. Typically, we use a fixed memory range as our heap; when the heap is exhausted, instead of call brk or mmap(Linux syscalls to ask for more memory from OS), we raise an out of memory error.

There are many global allocator implementations; for example, the simplest one is implemented in [linked list](https://github.com/phil-opp/linked-list-allocator); here is one I wrote using [buddy allocator](https://github.com/jjyr/buddy-alloc) algorithm, it can guarantee stable response time in different scenarios.

The [alloc crate](https://doc.rust-lang.org/stable/alloc/index.html#modules) contains the string, box, collections, ... core, and alloc crates almost covered my daily used modules when I use the std Rust.

### How to write no-std lib crate

By adding #![cfg(no_std)] on the top of the lib.rs, we tell the rustc to compile the whole crate under no-std, the compiler will raise errors if we import from std or use a crate that depends on the std. But usually, we use compiling condition #![cfg_attr(not(test), no_std)] to tell the rustc to compile as no-std only when we are not in the test so that we can write tests just like the std Rust.

If we need to use the alloc crate, add a line in the lib.rs `extern crate alloc`;, since the alloc is a built-in crate rustc will link it for us.

``` rust
//! lib.rs
#![cfg_attr(not(test), no_std)]

/// Add this line if you need to use alloc modules
extern crate alloc;
```

### How to support both std and the no-std environment in my crate?

The idiomatic way is to use [cargo features](https://doc.rust-lang.org/cargo/reference/features.html#features).

We add a feature std in the Cargo.toml, and enable it defaultly:

``` toml
# Cargo.toml
[features]
default = ["std"]
std = []
```

Then in the lib.rs we use std feature as compiling condition:

``` rust
//! lib.rs
#![cfg_attr(not(feature = "std"), no_std)]

/// different implementations under std or no-std

#[cfg_attr(feature = "std")]
fn a () { // std implementation }

#[cfg_attr(not(feature = "std"))]
fn a () { // no-std implementation }
```

Because we define std as default features, so our tests are still compiling in the std environment.

We can control dependencies to enable std if they support std feature:

``` toml
# Cargo.toml
[features]
default = ["std"]
std = ["crate-a/std", "crate-b/std"]

[dependencies]
crate-a = { version = "0.1", default-features = false }
crate-b = { version = "0.1", default-features = false }
```
