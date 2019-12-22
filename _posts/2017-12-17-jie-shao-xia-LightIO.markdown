---
layout: post
title: "介绍下 IO loop 和 Ruby 并发网络库 LightIO"
data: 2017-12-17 20:21
comments: true
---

说到脚本语言与高性能， Node.js 凭 benchmark 给人留下很深印象。

Node.js 的高性能来自于异步 IO。Node 本身提供了 IO loop 和大量的异步接口，而其臭名昭著的 callback hell 也是源于此。

IO loop，顾名思义就是一个循环，用来处理响应 IO 的代码。一般此类库的接口会允许注册一些 callback 用来处理 IO 结果。

类似的语言或库大同小异，用 Ruby 的 EventMachine 库做比方：

``` ruby
# echo server 经过简化
class EchoServer < EM::Connection
  def receive_data(data)
    send_data(data)
  end
end

EventMachine.run do
  EventMachine.start_server("0.0.0.0", 10000, EchoServer)
end
```

这个简单的示例注册了 EchoServer，并启动了 EventMachine。代码看起来非常简单，不愧是优雅的 Ruby 程序。

但毕竟是和 Node.js 同类的处理方式，也会有同样的问题。而问题就是出在 IO loop，掀开 EventMachine 的引擎盖：

``` ruby
# 仅为示意，不是真正的 EventMachine 源码
module EventMachine
  def run
    yield
    # IO loop
    loop do
      #...
      IO.select([@servers])[0].each do |server|
        run_receive_data server
      end
      #...
    end
  end
end
```

注意，所有的代码都是在 IO loop 中执行的。考虑到这是一个服务端程序，有一些耗费时间的操作会严重的影响程序性能。假如在处理时有个操作会耗费 1s，同时进入 10 个请求，最长响应时间会达到 10s 以上。

所以使用 IO loop 时必须要尽可能减少 callback 执行的时间，Node 和 EventMachine 提供了大量异步接口，让 callback 中尽量减少同步的操作，这样可以保证程序几乎没有浪费的等待时间，而结果就是**异步接口造成的 Callback Hell**。

既然找到了症结，也就有解决的方法，很多语言提供 Coroutine， Fiber 等机制，可以任意的切换控制流。通过这种机制可以使用同步接口来实现 IO loop 库。

``` ruby
## 示例代码
# 异步接口
db.async_query("...", proc{|result| http.post(data: result)})
# 同步接口
result = db.query("...") # 1. caller_fiber = Fiber.current # 保留当前位置
                         # 2. db.async_query("...", proc{|result| caller_fiber.transfer(result)}) # 回调时跳转回来
                         # 3. io_loop_fiber.transfer # 移交控制流到 IO loop
http.post(data: result)
```

以上代码演示了大致方法，使用 Fiber 来包装接口，则可以获取性能的同时消灭 Callback Hell。[async](https://github.com/socketry/async) 库使用了这种方法，是替代 EventMachine 比较好的选择。

对于异步编程库的接口，其实我更满意的是 python 世界的 gevent，同样提供了同步接口，并且把 IO loop 变成了隐式开始，即省去了 `EventMachine.run` 的调用，对用户更加透明。(当然 IO loop 隐式显示各有好处，显示对用户较为麻烦，但是更为清晰，隐式相反，可以看下 async 库作者的[论述](https://www.reddit.com/r/ruby/comments/7iugtd/i_am_writing_a_new_networking_concurrency_gem_for/dr2204e/))。

因为这点， gevent 可以在 IO loop 框架下可以提供多线程编程模型的接口。结合了 IO loop 的效率和多线程模型的简单灵活，我个人认为是目前异步编程的最佳方式。

身为 rubyist 还是说回 Ruby, 我最近在实现 Ruby 世界的 gevent，一个以隐式的 IO loop 和同步接口为核心的库 [LightIO](https://github.com/socketry/lightio)。

``` ruby
class EchoServer
  def initialize(host, port)
    @server = LightIO::TCPServer.new(host, port)
  end

  def run
    while (socket = @server.accept)
      _, port, host = socket.peeraddr
      puts "accept connection from #{host}:#{port}"

      # LightIO::Beam is lightweight executor, provide thread-like interface
      # just start new beam for per socket
      LightIO::Beam.new(socket) do |socket|
        loop do
          echo(socket)
        end
      end
    end
  end

  def echo(socket)
    data = socket.readpartial(4096)
    socket.write(data)
  rescue EOFError
    _, port, host = socket.peeraddr
    puts "*** #{host}:#{port} disconnected"
    socket.close
    raise
  end
end


EchoServer.new('localhost', 3000).run
```

可以从示例中看到，使用 LightIO 和原生的多线程编程非常相似，而与其他的库有巨大的区别。

打开引擎盖可以看到：

``` ruby
class Beam < Fiber
  def initialize(*args)
    #...
    @ioloop = IOloop.current
    #...
  end
end

class IOloop
  def initialize
    @fiber = Fiber.new{run_loop}
  end
  def self.current
    Thread.current[:"lightio.ioloop"] ||= self.new
  end
end
```

Beam 仅仅是对 Fiber 的封装，提供了方便操作的类似 Thread 的接口，创建／销毁 Beam 的成本非常低。

所有的 Beam 则是在同一个 IO loop 中执行，相当于 IO loop 的 callback。虽然貌似多线程编程，其实是单线程的 IO loop。

LightIO 目前在一个初步的阶段，经过半个月的时间完成了核心调度和 socket 库的包装。还未进行 Benchmark，性能优化等工作。预计 2018 年春季可以完成正式版。

与 Samuel Williams (async 作者) 沟通后，[LightIO](https://github.com/socketry/lightio) 移动到了 socketry 组织下！相信在高手的帮助下会取得更好的质量。
