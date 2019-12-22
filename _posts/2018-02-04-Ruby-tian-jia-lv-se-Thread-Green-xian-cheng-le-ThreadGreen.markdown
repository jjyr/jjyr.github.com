---
layout: post
title: "Ruby 又要添加绿色线程了 Thread::Green"
data: 2018-02-04 15:27
comments: true
---

翻到了 ruby-lang 的这个 issue，Eric Wong 给 Ruby 提了一个绿色线程的 PR


https://bugs.ruby-lang.org/issues/13618


总结下:


1. Eric Wong 给 ruby 增加了可以自动调度的 fiber，暂命名为 Thread::Green。就是类似 go 的 goroutine 这样的轻量级线程
2. Queue, SizedQueue 等用于同步的类是可以和 Thread::Green 一起使用的。意味着现有的 WebServer 换成 Thread::Green 很简单可以迁移
3. Matz, ko1 等大佬纷纷拍手称赞，(说不定很快就能用上了)
4. 之后 ruby 可以说摆脱异步编程模型了，直接起 Thread::Green 然后用 blocking IO 就可以和 node 的 callback hell 怼一怼
5. 对‘应用级别’开发者意味着 Web Server 会更高效，Rails 等框架也会更高效


用法大概就是和 Thread api 会兼容 所以没什么区别，比如下面示例:

``` ruby
urls = ["https://...", ...]
results = urls.map do |url|
  Thread::Green.new(url) do |url|
    # request url
    ....
  end
end
```

--------


感觉 Eric Wong 这个人很神奇啊，Unicorn 应该也是他写的。很低调、很少出境，不用非自由软件..有谁知道他的故事..

--------

坏消息就是我之前写的库已经失去存在意义了 ([lightio](https://github.com/socketry/lightio)), 不过可以当作个教学示例吧，这些功能从 ruby 层面去实现大概就是这个库
