---
layout: post
title: "fiber， goroutine/erlang process， thread的区别"
data: 2014-01-19 18:17
comments: true
tags: Ruby IO
---
经常看到有人会认为fiber和thread是一类东西，或者认为fiber就是轻量级的thread，和goroutine / erlang process是同一种东西

JRuby的fiber目前也是用thread来实现的，可能因此引起很多fiber和thread的误解

当然它们**当然不是**同一种概念..(两个当然!!哦不..三个！！)

thread是一种“执行单位”，操作系统会分配CPU去运行thread。goroutine和erlang process与此相近，相比thread更加的轻量化（貌似听说过goroutine就是简单的通过线程池来实现），所以它们也是“执行单位”。概念上thread 和goroutine / erlang process更加接近，都会由VM或OS(OS也可看做是VM!)分配CPU时间去执行。

fiber与此不同，打个简单的比方，如果你用了两个线程，并且你用的双核电脑，这时你的代码很有可能会跑在两个CPU上。

如果你用了两个fiber会怎么样？当你调用run的时候并不会新开始一个“执行单位”，fiber的调用是在你当前的thread执行的，fiber的call需要占用“执行单位”(通常是thread)，因为其本身不是一个“执行单位”。

fiber是在“执行单位”**之上**的，与thread不是同一个概念，fiber用来**保存**“执行流程”，仅仅是**保存**，这样可以把“执行流程”从“执行单位”上抽离，更加有效的利用“执行单位”。

Celluloid(ruby的一个实现actor model的库)中Actor就是这样的用法，可以让本应被block的“执行流程”暂时保存在fiber中，这时“执行单位”(其实就是thread)可以执行下一个“流程”，让thread的利用率更高。

em-synchrony则更巧妙的通过fiber切换“执行流程”来达到写同步代码，异步执行(有兴趣可以看em-synchrony在github主页上的链接，里面讲了如何实现)

这样看的话就很清晰了，thread和goroutine / erlang process 这些都是“执行单位”，可以获得CPU时间。fiber的用处则是保存“执行流程”，与前者完全不是同一个概念。
