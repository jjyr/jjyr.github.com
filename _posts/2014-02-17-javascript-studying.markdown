---
layout: post
title: "JavaScript 学习笔记"
data: 2014-02-17 18:52
comments: false
tags: JavaScript 中文
---

打算好好学习下 JS, 在阅读《JavaScript 语言精粹》把要点整理如下

所有内容基于ECMAScript-262 (JavaScript 1.5)

-----------

* false - 条件判断中 `0, -0, null, false, "", undefined, NaN` 均为 `false` (CoffeeScript 中的 `?` 操作符编译为 `typeof a !== "undefined" && a !== null;` 使其行为接近一般语言)

* Number - 数字储存为 double 而非 integer

* 基本类型 - 有 `Number, Boolean, String, Array, Object, undefined` 基础类型， `Boolean, String, Array, Object` 都属于 Object (因为可以用原型系统,  null 比较特殊)

* 对比 - `==` 仅对比值，`===`更为严格，要求类型也一致(coffeScript把这两个颠倒了过来，更加接近一般语言的行为)

* 注释 - 单行注释用 `//` ，导致你无法用 `//` 来表示一个空的正则，`/**/` 也代表注释

* 原型继承 - 通过键来获取对象中的值时，如果该对象无此键，则会到对象的原型链中去查找，直到 Object 的 prototype ，任何对象都隐含链接到 `Object.prototype`，该值默认是 `{}`

* delete 操作符 - 删除对象的键(不会影响到原型)，这时对象原型的相应键会暴露(如果有的话)，再次 delete 会被忽略并返回 true

* `for..in` 可以用来遍历对象的所有key

* `hasOwnProperty` 方法用来判断对象是否有该 key (从原型中继承的不算)

* 不同上下文中 `this` 的四种情况

  ```
  //1. 函数绑定到对象上时, this为对象
  a = {func: function(){ console.log(this)}}
  a.func() // this是a
  
  //2. 没有绑定到对象时，this为全局对象
  (function(){ console.log(this) })()
  //上面的this在浏览器中是window(全局对象)
  
  //3. 用new调用时this绑定到新构造的对象
  
  //4. 函数对象的apply方法
  (function(){console.log(this)}).apply("hello")
  //通过apply可以指定function的this值
  ```

* 原型速通

  ```
  //javaScript中的原型继承必须通过函数来完成
  
  //function有一个很重要的prototype属性，默认值为{}
  (function(){}).prototype
  //=> Object {}
  
  //函数的prototype属性是javascript中原型的关键
  //用new去调用function时，会以该函数的prototype为原型构建对象(常用此行为来模拟继承)
  a = {hello: function(){return "world"}}
  //现在来构建一个链接到a的对象，首先需要一个function
  A = function(){}
  A.prototype = a
  //用new调用A时会构建出以对象a为原型的对象
  b = new A()
  b.hello()
  //=> "world"
  b.__proto__ == a
  //=> true
  
  //所有对象都隐含链接自Object.prototype(相当于new Object())
  //没有类型，又能随意的改变原型的键，结果就是可以很方便的动态更改代码
  //通过函数和对象的任意组合，可以做到同一个原型对象具有多个“构造器”，可以任意的链接原型等等。比基于面向对象的语言要灵活许多
  ```

* 数组

  ```
  // JavaScript中的数组是 key 可以为 number 的类似数组的特殊对象（不像别的语言）
  // JS 中数组可变，数组的 length 属性比最大的整数索引大1
  arr = []
  arr[10] = "first"
  arr.length
  //=> 11
  
  //对length 属性赋值，会删除 length 之后的元素
  a = [1, 2, 3]
  a.length = 1
  a
  //=> [1]
  
  //数组就是对象所以可以用 for...in 语法
  //但 for..in 会遍历所有 key (不一定是下标)，并且不能保证遍历顺序
  //所以绝大多数情况下应该用 for 循环语句
  ```
  
