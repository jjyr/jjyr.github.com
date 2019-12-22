---
layout: post
title: "javascript学习笔记(二)"
data: 2014-02-18 19:09
comments: true
categories:
---

1, 函数中this的四种情况

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

2, 原型

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

3，数组

```
//javaScript中的数组是key可以为number的类似数组的特殊对象（不像别的语言）
//js中数组可变，数组的length属性比最大的整数索引大1
arr = []
arr[10] = "first"
arr.length
//=> 11

//对length属性赋值，会删除length之后的元素
a = [1, 2, 3]
a.length = 1
a
//=> [1]

//数组就是对象所以可以用for...in语法
//但for..in会遍历所有key(不一定是下标)，并且不能保证遍历顺序
//所以绝大多数情况下应该用for循环语句
```