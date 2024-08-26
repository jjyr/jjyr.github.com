---
layout: post
title: "Rust no-std FAQ"
data: 2020-10-21 02:52
tags: Rust English
---

### Why write this?

Most rustaceans(including me) using the std crate day-to-day since we learned how to write `println!("hello world")`. But it is still a very important feature of Rust: to deploy our code to bare-metal environments. Without OS support, we can not use the std crate, and it is usually scares people, so I write this article to clear most misunderstandings about Rust no-std.

### What is Rust no-std?

In std Rust, which is the default learned version. We can do many operations to interact with the machine and the internet, such as print messages to the console, read from files, and open URLs. All these features are provided by the underlying execution environment: our operating system. Our OS provides several syscalls to support IO, network, file systems, and process; rust delegates these features to OS via these syscalls.

You can look through the [modules of std](https://doc.rust-lang.org/stable/std/#modules) and try to identify which modules depends on the OS. Of course, we can't use these features if we do not have an operating system that provides the underlayer implementation. A feature called no-std is used for these bare-metal environments. In no-std Rust, we can only use the core features that do not depend on the operating system. Look at the [core crate](https://doc.rust-lang.org/stable/core/index.html); The core crate is a subset of std crate; you can find many familiar modules in the core that implement memory operations, arithmetic, or commonly used type structure.

The differences between std and no-std are tiny:

1. In no-std, you can't use *std* crate, however, you can import mostly modules from *core*.
2. You can't use heap related modules(box, collections, string, etc.) because the default Rust memory allocator depends on OS syscalls to increase heap memory; unless you implement your own version *global allocator*.
3. If you write a bin crate, you must implement a few *lang items*.

Don't be scared by these unfamiliar terms; to understand these, you need to know a few rustc concepts like *lang item* or *global allocator* which have been hidden from us in the std environment.

### What is lang item?

The short version: rustc is designed as pluggable; instead of builtin all operations in the compiler, rustc allows users to customize the language features via *lang items*.

The long version: [lang-items document](https://doc.rust-lang.org/unstable-book/language-features/lang-items.html)

Mostly lang items are defined in the *core* crate; however, some are defined in the *std* crate. For example, *eh_personality* is used by the failure mechanism. If you are writing a *no-std bin* crate, you need to implement these lang items to make the compiler work; but if you are writing a *lib* crate, you can assume the *bin* crate defined these lang items, so you don't need to do it.

The *lang items* feature is unstable, which means we can only define lang items in nightly Rust. The Rust team exposes some lang items via the compiler attribute; it allows us to define them in the stable Rust, for example: `#[panic_handler]` defines *panic_impl* lang item, and `#[alloc_error_handle]` defines *oom* [lang item](https://github.com/rust-lang/rust/issues/51540).

A suggestion is that you should always search for a runtime support crate before you try to implement them from scratch. The [Rust embedded work group](https://github.com/rust-embedded) is an excellent place to start. They provide crates to define lang items for different embedded environments; by using these crates, you can forget lang items and get a better life.

### What is the alloc crate? What is the global allocator?

The *alloc* crate contains heap related modules; modules in the *alloc* use the *global allocator* to allocate memory. The *std* crate defines a default *global allocator*, which depends on the operating system; when heap memory is exhausted, the *std* *global allocator* invokes OS syscalls to increase the memory. So in *no-std* environments, we need to define our *global allocator*; we can use the `#[global_allocator]` attribute to define it. Typically, we use a fixed memory range as our heap; when the heap is exhausted, instead of calling *brk* or *mmap*(Linux syscalls to ask for more memory from OS), we raise an out of memory error.

There are many global allocator implementations; for example, the simplest one is implemented as a [linked list](https://github.com/phil-opp/linked-list-allocator); here is one I wrote using [buddy allocator](https://github.com/jjyr/buddy-alloc) algorithm, it can guarantee stable response time in different scenarios.

By defining the *global allocator*, we can use the [alloc crate](https://doc.rust-lang.org/stable/alloc/index.html#modules) in our *no-std* program. The *alloc* contains very frequently used modules such as string, box, collections, etc. The *core* and the *alloc* crates almost covered my most frequently used modules in the *std*.

### How to write no-std lib crate

By adding #![no_std] on the top of the *lib.rs*, we tell the rustc to compile the whole crate under *no-std* Rust; the compiler will raise errors if we try to import from *std* or use a crate that depends on the *std*. Usually, we use another compiling condition #![cfg_attr(not(test), no_std)] to tell the rustc to compile to *no-std* Rust only when the *test* flag is disabled so that we can use *std* in our tests, just like the *std* Rust.

If we need to use the *alloc* crate, we need to add another line in the *lib.rs* `extern crate alloc`; since the *alloc* is a built-in crate, rustc will link it for us automatically.

``` rust
//! lib.rs
#![cfg_attr(not(test), no_std)]

/// Add this line if you need to use alloc modules
extern crate alloc;
```

### How to support both std and the no-std environment in my crate?

The idiomatic way is to use [cargo features](https://doc.rust-lang.org/cargo/reference/features.html#features).

We add a feature *std* in the *Cargo.toml*, and enable it as default:

``` toml
# Cargo.toml
[features]
default = ["std"]
std = []
```

Then in the *lib.rs* we use *std* feature as compiling condition:

``` rust
//! lib.rs
#![cfg_attr(not(feature = "std"), no_std)]

/// different implementations under std or no-std

#[cfg_attr(feature = "std")]
fn a () { // std implementation }

#[cfg_attr(not(feature = "std"))]
fn a () { // no-std implementation }
```

Because we define *std* as default features, so our tests are still compiling in the *std* Rust.

We can also control dependencies to enable *std* feature:

``` toml
# Cargo.toml
[features]
default = ["std"]
std = ["crate-a/std", "crate-b/std"]

[dependencies]
crate-a = { version = "0.1", default-features = false }
crate-b = { version = "0.1", default-features = false }
```
