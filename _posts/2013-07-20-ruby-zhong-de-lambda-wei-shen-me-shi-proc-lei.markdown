---
layout: post
title: "ruby中的lambda为什么是Proc类"
date: 2013-07-20 11:33
comments: true
categories: ruby
---

当然写之前我试着在网上搜了下， 果然没有搜到类似的问题。

lambda为什么不是Function, Method 而是Proc ?

这个问题当然没有标准答案，于是我做了一番推(猜)测

lambda和proc都是Proc类，这样已经可以看出一些端倪，proc既然叫proc当然是Proc类的主角，所以lambda只是Proc的一个附属，因为已经实现了proc，所以就顺手实现了lambda。

 proc是用来代表block的(双飞燕中的话是proc更接近block), 如果我们在参数中用`&block`，我们会得到一个代表block的proc对象, 并且proc和block在各种行为上几乎都是一致的。

再来看下lambda，双飞燕中说lambda更接近method
当然...其实他们的区别是很大的，ruby中method必须bind到一个object上才可以调用，method(消息)必有接收者

而lambda就很异端了，仅仅是一段可执行代码，没有什么可与之对应的(python中的method可以对应为第一个参数为self的lambda)

而与proc的区别仅仅是传参和上下文跳转上更像method，并且在block的压力之下几乎没有任何用处..


> “虽然很鸡肋， 但是实现上很简单(把proc稍微改下？) 干脆一起实现了，说不定谁可以用得上”   
> \--------------------------（我猜测的实现lambda时matz的想法)


于是就同归于Proc类了
