---
layout: post
title: "javascript学习笔记(一)"
data: 2014-02-17 18:52
comments: true
categories: javascript
---

以前没怎么用过javascript(仅停留在简单的dom处理与ajax上)，身为后端程序员对其印象仅有杂乱

完成简书新richtext编辑器的基本功能后，感到js也没这么不堪，反而基于原型的模型能很轻易的应对反射，动态定义Function/Object等‘元编程任务’

并且和ruby中的'元编程'不同，在js中这些就是通常编程

“原型”的表达力不弱于OO，并且复杂程度远小于OO。当然在javascript中的实现还是略微杂乱..虽然这门语言很多细节部分的设计让人匪夷所思，但是其核心的原型功能还是兼具了**精简**与**好用**这两处优点

遂打算好好学习下js, 并在阅读《JavaScript语言精粹》时把一些知识要点记录下来

本文会以tips的方式罗列从书中获取的知识要点，以及一些我自己的理解和对这门语言的想法

所有内容基于ECMAScript-262 (javascript 1.5)

-----------

1. false，js的条件判断中 `0, -0, null, false, "", undefined, NaN` 均为 `false`(coffeeScript中的`?`操作符编译为`typeof a !== "undefined" && a !== null;`使其行为接近一般语言)

2. Number，js中数字储存为(相当于java中的)double, 所以1/2会等于0.5

3. 基本类型，js中有 `Number, Boolean, String, Array, Object, undefined`几种类型，`Boolean, String, Array, Object`都属于Object(因为可以用原型系统, null比较特殊)

4. 对比，js中`==`仅对比值，`===`更为严格，要求类型也一致(coffeScript把这两个颠倒了过来，更加接近一般语言的行为)

5. 注释，js中单行注释用//，导致你无法用//来表示一个空的正则，/**/也是

6. 原型继承，js中通过键来获取对象中的值时，如果该对象无此键，则会到对象的原型链中去查找，直到Object的prototype，任何对象都隐含链接到Object.prototype，该值默认是`{}`

7. 更改对象的键时不会影响到原型

8. delete操作符，用来删除对象的键(不会影响到原型)，这时对象原型的相应键会暴露(如果有的话)，再次delete会被忽略并返回true（这代表如果原型上有key，则没办法在对象上删除该键，但是可以赋值为undefined）

9. `for..in` 语句可以用来遍历对象的所有key

10. `hasOwnProperty`方法用来判断对象是否有该key(从原型中继承的不算)