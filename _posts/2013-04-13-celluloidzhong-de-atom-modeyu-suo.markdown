---
layout: post
title: "Celluloid中的Atom Mode与锁"
date: 2013-04-13 23:09
comments: true
tags: Ruby
---
Celluloid默认是[Atom Mode](https://github.com/celluloid/celluloid/wiki/Glossary)执行的, 这种模式下可以中断当前执行的任务 先执行下一个

Celluloid提供了一个sleep方法，在Actor内部调用sleep时会中断当前Fiber并且用timer异步来恢复
```ruby
def before_suspend(task)
  @timers.after(@interval) { task.resume }
end
```
当中断当前的TaskFiber时，Actor即可处理下一个message，被中断的message等待timer去恢复自身
```
def task(task_type, method_name = nil, &block)
  if...
     ....
  else
    @task_class.new(task_type, &block).resume#中断fiber时从此处返回
  end
end
```

我们在Actor上的每次调用都是一个独立Fiber

Actor 线程是一个worker,来运行多个Fiber，个人感觉这里有点矛盾，Celluloid把多线程程序，变成了多Fiber程序，不同的Fiber很有可能并发访问同一个变量
而`exclusive`就是Celluloid中的Fiber的锁。actor本身就是消除锁的，而现在却又引入了一个新的锁。

不过实际写过Celluloid程序后，感觉还是不要对这个锁太担心的，实际中只有中断时(调用sleep)才会插入新的fiber，而我们在写需要同步执行的代码时 一般的正常人类是不会在其中插入个sleep的，如果必须确定代码的同步 则要把代码写在`exclusive`块中(一般不需要，exclusive作用是阻止在本块中Fiber的中断)

这种机制虽然带来了少许的复杂性但是

1. 绝大多数情况下我们无需知道这种机制也可正常的运作程序
2. 即使用到`exclusive`， 也只是很简单的应用
3. 可以更加有效率的利用线程

Celluloid把任务和worker之间隔离开，之后可能会把[thread和actor也进行抽象分离](https://github.com/celluloid/celluloid/wiki/GSoC-Ideas#executing-actors-in-a-thread-pool-ben-langfeld)，这样增加了灵活性和效率， 不过随之也带来了复杂性， 其中得失还是很难说清的
