---
layout: post
title: "Yet Another Markdown Parser, 没想到还原度还挺高的"
date: 2013-08-31 13:48
comments: true
tags: Ruby markdown
---

最近写了个[markdown parser][minidown]练手, 发现这种有规范的东西非常适合TDD, 照着markdown语法来写spec, 然后一个一个将其通过, 之前从未试过这么彻底的TDD


1. 是写代码写的很爽时顾不上测试

2. 是spec一定要事先定下，如果是创造性的编程, spec没法确定, 在代码和spec间来回改动就失去了TDD的意义

托TDD的福，写好各个语法的parse后跑了下GFM的source页，没想到还原度还挺高的
之后fix了几个小地方，parse的效果已经比较完善了，而且因为TDD 保证了测试的覆盖率(2k行左右的代码估计1k多都是spec)，可以放心的修改代码，只要可以pass spec基本就是没问题的

之前一直感觉TDD有点名副其实, 经过这次实践感觉这种编程方式真的能帮助你写出可靠的代码

当然关键还是要事先确定spec, 如果不能确定spec我是绝不会用TDD的方式去开发的, 实际上我把[minidown][minidown]改成支持GFM时就改动了一些spec, 当然相应之前的所有代码也需要修改，相当于白写了一遍测试


benchmark了下各种markdown parser解析14000篇文章的效率

* 跑在the ruby racer 上的marked大概3.8s可以完成
* minidown 大概16s可以完成
* maruku报错..
* kramdown 大概200+s可以完成...(这货README里写着fast..)

后3种都是pure ruby的markdown parser

marked考虑到主要是前端使用，可能没有太多考虑效率，看得出ruby和v8差距还是挺大...

对于后边两个结果到是很惊讶, 没想到minidown在pure ruby的parser里还挺快的..


[minidown]: https://github.com/jjyr/minidown
