---
layout: post
title: "ruby vs python benchmark"
date: 2013-07-22 22:15
comments: true
categories: ruby python other
---

写这篇的目的是下次在看见有人认为ruby效率比python低时我可以直接贴给他链接..

鉴于很多人用ruby1.8来benchmark说明ruby效率是多么低下，我使用了ruby和python标准实现的最新稳定版本

```
ruby -v
ruby 2.0.0p247 (2013-06-27 revision 41674) [x86_64-linux]

python3 --version
Python 3.3.2
```

使用传统的fibonacci来benchmark

```ruby
#ruby
require 'benchmark'

def fib n
  if n < 2
    1
  else
    fib(n - 1) + fib(n - 2)
  end
end

Benchmark.bm{|bm| bm.report{puts fib(35)}}
```

```python
#python
import timeit

def fib(n):
	if n < 2:
		return 1
	else:
		return fib(n - 1) + fib(n - 2)

if __name__=='__main__':
	from timeit import Timer
	t = Timer("print(fib(35))","from __main__ import fib")
	print(t.timeit(1))
```

```
#ruby

ruby fib.rb
       user     system      total        real
 14930352
  2.600000   0.000000   2.600000 (  2.601639)

#python3.2.2

fib.py 
14930352
9.720147652000378
```

ruby版本快了大概3.7倍
我使用python2.7.5版会稍微快些，大概6.3秒，当然还是比ruby慢的
