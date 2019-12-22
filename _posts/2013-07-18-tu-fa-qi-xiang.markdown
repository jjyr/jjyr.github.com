---
layout: post
title: "突发奇想, 试下celluloid + eventmachine"
date: 2013-07-18 12:32
comments: true
categories: celluloid eventmachine ruby
---

前几天[benchmark了下ruby中比较有前途的websocket-server](https://github.com/jjyr/websocket-benchmark)(reel和em-websocket)，结果是eventmachine完胜..

而且发现reel有个很严重的问题，打开的文件描述符有一部分不能释放，于是造成打开的文件越来越多

https://groups.google.com/forum/?fromgroups=#!topic/celluloid-ruby/4btMSHIcjj4

mail list中问了下， tony说是我用法不对，但是我按照他说的用了detach还是会有此问题

但是如果使用em-websocket来写server的话难度的确是很大, 多线程环境很容易出问题, 于是我想如果有个能运行在eventmachine thread pool里的轻量级actor库就好了。

于是花时间研究了下如何实现，结果发现同步是个大问题
调用异步的actor没有什么问题，让他在pool里执行便可，但是如果同步的调用，那么当前的线程必须要阻塞住等待结果返回，可能阻塞住pool中很多的thread, 如果引入fiber进行异步的回调，则必须保证当前actor在fiber结束前不能被再次执行
```ruby
class Player
  ...
    def
      ...
        @mp = ...
        @hp = ...#假设是异步计算的代码, 如果在fiber.yield之间有其他任务执行
                        #可能会造成数据不一致
      ...
  ...
end
```
于是需要引入exclusive之类机制

这样实现的话就偏离了轻量二字，而且更关键的。。这简直就是celluloid啊。。身为ruby程序员当然不能重新发明轮子

于是干脆使用eventmachine + celluloid这种形式，由em-websocket进行异步的io，然后celluloid并行的去执行代码, 而且还有个好处就是因为每个链接分一个线程，所以完全不要担心阻塞em-websocket的线程，在actor中可以尽情使用阻塞io

至于效率就交给传说中JVM上很屌的抢占式线程调度吧

于是这里是['成品'](https://github.com/jjyr/hara)
