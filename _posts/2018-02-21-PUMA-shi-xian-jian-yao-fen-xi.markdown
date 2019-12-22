---
layout: post
title: "PUMA 实现简要分析"
data: 2018-02-21 23:25
comments: true
---
之前在 [绿色线程是如何提升服务器并发性能的](http://justjjy.com/2018/02/16/how-to-improve-server-concurrency-with-green-thread/) 一文中描述了绿色线程的原理。并且讲了我的计划：使用 Discourse 来 benchmark 绿色线程对并发性能的提升。经过一番折腾后在 [LightIO](https://github.com/socketry/lightio) 下成功运行了 Discourse 的 benchmark（折腾很久后发现需要将 Discourse 使用的 hiredis gem 换成纯 ruby 实现的 redis client），但结果却是使用绿色线程和不使用时性能表现差不多。

我推测性能相差不多的原因是 Discourse benchmark 使用了 thin 服务器，thin 是个单线程服务器，当然无法发挥出 LightIO 绿色线程的威力。那么换用 Puma 呢？来看一看 Puma 源码，Puma 实现的非常简单。

从 [https://github.com/puma/puma](https://github.com/puma/puma) Readme 中可以大概了解 Puma 的实现方式。
Puma 分为 Single, Cluster 两种模式：
Single 是单进程多线程模式，这种模式使用 ThreadPool 处理请求。
Cluster 是多进程多线程模式，在前者基础上增加了 Worker 的概念。使用过 Unicorn 的话对这种架构会比较亲切。

根据 Readme 所述，Puma 主要是为无 GIL 的 ruby 实现设计的，所以我们主要来看 Single 模式下的源代码。

顺着 `bin/puma` 一路看下去，大概了解 Puma 的主要概念：

* Accepter: 调用 `Socket#accept_nonblock` 并包装成 Client 的线程
* Client: Puma 中代表客户端的对象
* Reactor: 用来检查 Client IO 超时，或是否读取完成的一个线程
* App ThreadPool: 用来处理客户端链接，调用 Rack app

Puma 启动时会初始化这些对象。然后启动 **Accepter** 线程，Accepter 调用 `Server#handle_servers` 方法，负责接受客户端，将客户端 socket 包装成 Client 加入到 App ThreadPool 的队列。

**App ThreadPool** 会先检查并尝试读取 client 的请求，如果 client 的请求已经准备好，则调用 `process_client` 进行 HTTP 协议解析并传给 Rack app，完成一次 HTTP 的请求／响应。如果 client 请求无法立刻读取，则将 client 加入 Reactor。

**Reactor** 也是单独的一个线程，使用 `select` 来检测并尝试读取 client 请求，一旦成功就重新添加到 App ThreadPool。Reactor 也负责维护 client 的超时。

![Puma client object lifecycle](/images/posts/PumaSource/Puma_client_lifecycle.png)

这就是 Puma 的实现。主要思路就是减少 ThreadPool 的 Blocking，保证处理更多请求。因此引入了 Accepter 和 Reactor。大量的 IO wait 操作都在这两个线程中处理，而 App ThreadPool 仅处理计算工作(解析 Http, 调用 Rack)。由此来提升线程的利用率。

Puma 的实现非常简单优雅。比我想象的简单很多，我应该会尝试下如何结合 Puma 和 LightIO 以取得更好的性能（也因为懒得为 LightIO 单独再写个服务器了）。
