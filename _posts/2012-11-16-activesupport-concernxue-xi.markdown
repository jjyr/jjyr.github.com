---
layout: post
title: "ActiveSupport::Concern学习"
date: 2012-11-16 16:27
comments: true
tags: Rails Ruby
---

##为什么需要使用ActiveSupport::Concern
*active_support/concern.rb*中已解释的很清楚
简要的总结下
------------------------
module Bar需要在included时调用module Foo的方法

此时需要在class C中include Bar就需要先include Foo

但是像这样使用的时候需要关心依赖问题是很不爽的，我们希望使用Bar则include Bar即可,不应该再去管Bar的依赖问题

```ruby
module Bar
  include Foo
  #.....
end
```
这样我们就可以只include Bar而不需要关心Foo

但这样也有问题,Foo可能在included中需要class C。但是现在这样Foo在included中取到的实际是Bar，并不是C

ActiveSupport::Concern可以神奇的帮我们解决这个问题，保证Bar的执行没问题,并且使用者不需要关心Foo

只需把def self.included换成Concern提供的include方法即可

Concern源码
-------------------
```ruby
module Concern
    #被extend时会对extend其的module设置一个实例变量用于储存依赖数组
    def self.extended(base) #:nodoc:
      base.instance_variable_set("@_dependencies", [])
    end

    #被include时会在include其的module中追加依赖self
    #如果include的对象中不包含@_dependencies(即没有extend Concern)
    #则表明该对象为正确的include目标,在该对象上include所有本module依赖的module,extend ClassMethods。最后调用'included'可以保证避免included中的依赖问题
    def append_features(base)
      if base.instance_variable_defined?("@_dependencies")
        base.instance_variable_get("@_dependencies") << self
        return false
      else
        return false if base < self
        @_dependencies.each { |dep| base.send(:include, dep) }
        super
        base.extend const_get("ClassMethods") if const_defined?("ClassMethods")
        base.class_eval(&@_included_block) if instance_variable_defined?("@_included_block")
      end
    end

    #如果base不为nil则认为是调用super的included(保证通常的钩子也可使用)
    #否则存下block待真正的类include时再调用
    def included(base = nil, &block)
      if base.nil?
        @_included_block = block
      else
        super
      end
    end
  end
```
大致就是这样。用是否extend Concern来判断是用于include的module还是真正需要max-in的类
