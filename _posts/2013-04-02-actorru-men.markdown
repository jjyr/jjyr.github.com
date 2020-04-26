---
layout: post
title: "Actor入门"
date: 2013-04-02 16:30
comments: true
tags: Ruby actor
---

最近对Actor模式很有兴趣(Celluloid), 记下自己的心得和对Actor模式的理解。

要想知道一个东西有什么必要性，就要知道没有它的话是什么样子

如果没有struct...
```ruby
point1x = point1y = point2x = point2y = 0
```

如果没有class...
```ruby
def rectangle_area rect
  #something...
end

def circle_area circle
  #something...
end
#etc...
```

如果没有actor...
```ruby
  #好吧，可能没有的话也没什么关系..
```

当然还是有关系的..
比如我们设计一个账户
```ruby
class Account
  attr_accessor :money

  def take_money amount
    if amount < money
      new_amount = money - amount
      self.money = new_amount
      "ok!"
    else
      "no enough money :("
    end
  end
end
```
刚看到我就笑了，居然不用锁！要是有并发请求take_money不是有机会取出双份的钱吗

当然..我们可以把程序中所有危险的地方都加上锁，但是锁带来的死锁等问题相信写过这类程序的人都知道其麻烦之处(我没写过)

其实更简单的方法就是看下为什么会造成这样，然后把原因消除就好

原因很明显，因为有不同的thread来执行这段代码，所以会造成脏数据，需要用锁来保证这段代码必须是只能一个thread来执行

当然更简单的方法其实真的很简单..与其引入锁来保证这段代码只能被唯一的thread执行，不如我们让所有的代码都只能被一个thread来执行，这样当然就不需要锁了

``` ruby
require 'celluloid'
class Account

  include Celluloid

  attr_accessor :money

  def initialize
    @money = 0
  end

  def take_money amount
    if amount < money
      new_amount = money - amount
      self.money = new_amount
      "ok!"
    else
      "no enough money :("
    end
  end

  def save_money amount
    new_amount = money + amount
    self.money = new_amount
    "ok!"
  end
end
```
ruby + celluloid真的很方便..看起来就像是单线程程序， 实际上每个Account内部的确是单线程
但是已经可以避免之前的问题了，无论存钱还是取钱都是安全的！而且我们几乎都没有改动代码

不过此时的Account已经不是过去的他了， 每个实例都从object蜕变为了actor...

```ruby
a = Account.new
a.save_money 10000000000000000000000000000000000000000000000000000000000000000000
a.take_money 5
```
当我们调用方法时其实已经不是直接的调用，而是对actor发送消息，然后actor内部用自己的线程去执行，之后返回给我们消息，所以执行我们代码的永远只有一个线程，自然不需要锁
而每个actor会有一个邮箱来接受消息，之后actor线程去执行(你可能想到生产者消费者模式，那么你就对了)

所以当多个线程去并发的请求actor,实际上是一个Queue#push操作(这也是'无锁'的Actor必要的一个锁)

```
struct == datas
class == struct + method
actor == class + thread!!
```
