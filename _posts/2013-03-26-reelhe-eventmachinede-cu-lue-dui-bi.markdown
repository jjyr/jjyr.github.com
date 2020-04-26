---
layout: post
title: "reel和eventmachine的粗略对比[更新2013年7月]"
date: 2013-03-26 20:14
comments: true
tags: Ruby
---


四个月后的更新
---------------------------
因为水平不足，对Reel造成了极大的误解..
(希望不要误解到别人)

更正下之前的误解

Reel其实是异步IO单线程的，可以认为和EM一样，但是大家都知道Celluloid主打的就是并行编程

于是..如果你想要并行的话可以调用[detach](http://rdoc.info/gems/reel/Reel/Connection:detach)方法，并且自己管理socket

当然这样做的话就不是异步IO了(WTF..........)

另外reeltalk中的代码貌似也有一些问题..

所以现在来说还是优先使用eventmachine, celluloid-io & reel目前还是有一些问题(当然celluloid已经比较成熟了, 可以大胆使用)


起因
--------------------
本来是很追捧EM的，直到看到了一篇[文章](https://news.ycombinator.com/item?id=4695828)

感觉之前学过些erlang, 应该很容易理解celluloid. 而且最近工作中也需要用到websocket，果断选择reel来做(无条件听信大牛..)


一坑
-----------------
看了下文档，结果从README的helloworld就被坑了, 粘贴后执行程序会直接退出，不会block住

源码
```ruby
require 'reel'

Reel::Server.supervise("0.0.0.0", 3000) do |connection|
  while request = connection.request
    case request
    when Reel::Request
      puts "Client requested: #{request.method} #{request.url}"
      request.respond :ok, "Hello, world!"
    when Reel::WebSocket
      puts "Client made a WebSocket request to: #{request.url}"
      request << "Hello everyone out there in WebSocket land"
      request.close
      break
    end
  end
end
```


回去又翻了下celluloid的文档，发现README上的代码的确是有问题，因为是调用的`Server.supervise`所以Server是由`Supervisor`线程来执行的，主线程当然会直接退出，需要改成用run方法来直接执行，或者在后边调用sleep来阻塞住主线程(开源社区文档真是大问题啊..尤其是helloworld就跑不通的..严重打击新手)

二坑
---------------------------
关键这helloworld坑的还不止这里,因为之前写过EM的server再加上示例代码的误导，让我以为处理代码应该在代码中的when..case块中执行。结果发现无法判断客户端的disconnect。经过对比了EM和reel的源码后发现他们的设计思路是完全不同的。

先来看下EM

from em-websocket README
```
require 'em-websocket'

EM.run {
  EM::WebSocket.run(:host => "0.0.0.0", :port => 8080) do |ws|
    ws.onopen { |handshake|
      puts "WebSocket connection open"

      # Access properties on the EM::WebSocket::Handshake object, e.g.
      # path, query_string, origin, headers

      # Publish message to the client
      ws.send "Hello Client, you connected to #{handshake.path}"
    }

    ws.onclose { puts "Connection closed" }

    ws.onmessage { |msg|
      puts "Recieved message: #{msg}"
      ws.send "Pong: #{msg}"
    }
  end
}
```

代码是通过注册回调来完成的，然后EM会去并发执行这些回调

EM的核心是一个loop{...}然后在其中触发所有已经注册的io对象和timer和heartbeat

因为定期去进行io所以才会引发EOF的错误，从而得知客户端断开链接(之前我还以为socket都是不需要类似轮询的行为的。。)

而on_exit就是在此时rescue块中被触发的


~~reel中没有on_exit之类回调，且没EM的heartbeat机制去周期性io~~

~~所以不会产生客户端断开的错误~~

~~reel中把这个定期read交给用户来做。~~

~~而用户需要的是在取到request时转发给一个Actor来处理(这样才会non-block,要是直接处理会阻塞到while)~~
~~然后在actor中实现heartbeat去定时read Websocket~~

~~[就像这个刚开始被我忽视了，后来才好不容易找到的示例,这个才是正确的，reel的helloworld的太具有误导性了](https://github.com/celluloid/reel/blob/master/examples/websockets.rb)~~


~~订正: [现在最好的示例是这个](https://github.com/tarcieri/reeltalk)~~

对比
----------------------------
对比了下em-socket(eventmachine)和reel(celluloid)的设计思路

reel是获取request后交给用户处理， 而em-socket是通过事件来回调用户的方法

~~reel可以让用户自己去通过不同的Actor处理request, 而em-socket的回调类似于处理request的Actor的内部方法 所以有内存共享带来的麻烦~~

~~reel的heartbeat需要自己实现，而EM有已经实现的统一的heartbeat。~~所以EM的IO是'更异步'的(所有IO对象一起io)

而celluloid(~~每个connection有自己的io周期)~~的优势则是并行(当然是在Jruby和rbx上),

不过据说MRI的一些io操作是可以并行(毕竟本来也达不到性能瓶颈，而且Actor的优势还是很明显的,毕竟不会因为锁把程序搅乱)。


是自己坑的，不能怪文档
---------------------------------
被坑了一下午，真的感觉开源社区的文档真是很痛苦，尤其是helloworld(能不能笼络新手关键就看这个了..),当然主要原因还是自己对底层的一窍不通导致误解。。

对应用层开发来讲底层知识比想象的要重要

另外celluloid真的很好用..只要`async.method` or `future.method #可以取得返回值`就可以异步执行
不需要像erlang那样再去做消息匹配。


celluloid简洁的API 配合ruby强大的表达能力一定会越来越火
