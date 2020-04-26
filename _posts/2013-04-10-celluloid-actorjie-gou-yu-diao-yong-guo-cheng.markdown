---
layout: post
title: "Celluloid::Actor结构与调用过程"
date: 2013-04-10 22:27
comments: true
tags: Ruby
---

ruby是面向对象语言,但是Celluloid做到了无需更换代码，仅在类中`include Celluloid`就可以进行面向Actor编程
```ruby
class A
  include Celluloid
  def foo
    puts "bar"
  end
end
```
此时A已经代表一个Actor类
```
a = A.new
a.class #A
a.class.ancestors #[A,
 Celluloid::InstanceMethods,
 Celluloid,
 Object,
 PP::ObjectMixin,
 Kernel,
 BasicObject]

a.is_a? A #true 
A === a #true      of course!
a.is_a? Celluloid #true 
Celluloid === a #false    W..T..F??
```
wtf?

a是A的实例，我们的测试可以通过
但是当我们用Celluloid来测试时`a.is_a?`和`Celluloid.===`结果不一致

###why?

因为a并不是A的实例

```ruby
a.class #A
a.inspect #<Celluloid::ActorProxy(A:0x3fecb9cfab6c)>
#a实际上的类是Celluloid::ActorProxy
```
Celluloid会覆盖new方法
```ruby
 def new(*args, &block)
   proxy = Actor.new(allocate, actor_options).proxy
   proxy._send_(:initialize, *args, &block)
   proxy
 end
 alias_method :spawn, :new
```
我们得到的a是ActorProxy实例 并且Celluloid会覆盖===方法使`A === a`返回`ture`

当前的大致结构为
```ruby
a #ActorProxy 用来把ruby中对对象的方法调用封装成对Actor的发送消息

a.send :instance_eval,"Thread.current[:celluloid_actor]" #Actor 用来表示Actor的对象，内部持有线程,  所有对Actor的操作均通过ActorProxy, 所以一般取不到此引用

a.wrapped_object #<WARNING: BARE CELLULOID OBJECT (A:0x3fecb9ccdfa4)> 会提示警告，直接使用原始的ruby对象会破坏Actor的封装,破坏线程安全 所有方法会通过Actor的thread在此原始对象上调用
```

我们调用A.new时会new一个Actor并且我们得到的是ActorProxy
当我们调用其上的方法时 ActorProxy会把我们的调用请求封装后发送到a的Actor的邮箱，并且阻塞当前线程， 直到接收到Actor返回的消息

具体过程如下
```ruby
a = A.new
#1 实例化A,Actor和ActorProxy
#2 Actor内部实例化ThreadHandle --这里使用了一个线程池，这样如果大量生产Actor可以直接取得提前构造的线程
#3 ThreadHandle 内部的Thread开始loop检查mailbox

a.foo #bar => nil
#1 触发ActorProxy的method_missing 把方法调用封装到SyncCall
#2 向a的mailbox发送调用消息
#3 调用SyncCall#value(Celluloid#suspend -> SyncCall#wait)阻塞当前线程并检查当前线程的mailbox
  ####loop.1 actor的thread从mailbox取出msg, 调用message_handle, 用TaskFiber封装后调用(为了实现Celluloid的Atom模式[https://github.com/celluloid/celluloid/wiki/Glossary])
  ####loop.2 执行成功后封装到SuccessResponse,发送到调用者的mailbox
#4 收到SuccessResponse， 调用SuccessResponse#value， return
```

因为ruby并非erlang这种原生支持线程的语言
所以在分析时很容易混淆当前的调用线程

#####容易误解的地方
######scope
因为ruby并非原生的支持线程消息， 调用者的当前线程和执行代码的线程很容易混淆。不过Celluloid已经很好的封装了这些，我们只要当对象为Actor直接调用即可，一般编程中不需考虑的这些

######inner scope
因为ruby的线程与消息并非原生支持，所以如果是下面这种情况
```ruby
class A
  include Celluloid
  def foo
    puts "bar"
    foo2
  end

  def foo2
    puts "bar2"
  end
end
``` 
当我们调用`A.new.foo`时，`foo2`是在A实例的内部调用的，所以并非经过ActorProxy,此时是在原始对象内部直接调用的ruby方法，当然也不会通过mailbox(和erlang不一样),不过编程时同样不需关心这点

