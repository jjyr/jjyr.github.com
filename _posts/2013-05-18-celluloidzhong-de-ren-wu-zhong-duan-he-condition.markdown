---
layout: post
title: "Celluloid中的任务中断和Condition"
date: 2013-05-18 16:24
comments: true
tags: Ruby
---


######Celluloid有个很[神奇的机制](https://github.com/celluloid/celluloid/wiki/Exclusive)（<--示例代码）


Celluloid每次任务(方法调用)会用Fiber去包装

当一个FiberTask因为**某些代码**被中断时，此时Celluloid可以回到[线程执行任务的方法](https://github.com/celluloid/celluloid/blob/master/lib/celluloid/actor.rb#L418)

**相当于**中断的任务已经结束

之后Actor线程继续的从mailbox[取任务](https://github.com/celluloid/celluloid/blob/master/lib/celluloid/actor.rb#L168)


######某些代码!
FiberTask会因某些方法被中断，上面的示例代码中中断当前Fiber的是sleep方法，这个方法由Celluloid做了覆盖
```ruby
  sleeper = Sleeper.new(@timers, interval)
  Celluloid.suspend(:sleeping, sleeper)
```

`Celluloid.suspend`这行代码就起到中断作用，(知道它会中断当前Fiber即可，实际会根据后边的参数调用一些callback)

######中断了。。如何恢复？
```ruby
  def before_suspend(task)
    @timers.after(@interval) { task.resume }
  end
```

这就是参数sleeper的callback,可以看到利用定时器来执行恢复的task

如果Fiber.resume的时候当前正在执行别的FiberTask会怎么办？岂不是会乱掉？

after定时器也是通过[FiberTask](https://github.com/celluloid/celluloid/blob/master/lib/celluloid/actor.rb#L279)来执行的，所以到时间后我们的block会被传到mailbox中，就像一个新任务被调用一样，完全没有问题!

######某些方法能中断？
actor当然不是再任何情况下都可以自己中断..上文`sleep`方法是之一，另外Celluloid还提供了`Condition`类来进行中断

Condition类和[ConditionVariable](http://rdoc.info/stdlib/thread/ConditionVariable#)行为类似

######Condition
ConditionVariable主要是用来在线程间统一资源的，README很详细

在Celluloid中应该用`Celluloid::Condition`来完成这件事，他们的行为是差不多的

`Celluloid::Condition`的好处是会[中断当前的FiberTask](https://github.com/celluloid/celluloid/blob/master/lib/celluloid/condition.rb#L48), 这样Actor可以去执行之后的Task,而不是一直block住,基本原理和之前`sleep`是差不多的

Condition可以很好用的去做些同步操作，而且不会浪费线程
