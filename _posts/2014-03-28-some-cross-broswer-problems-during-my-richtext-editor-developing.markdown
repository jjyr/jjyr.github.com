---
layout: post
title: "开发编辑器的过程中遇到的一些浏览器差异"
data: 2014-03-28 23:34
comments: true
categories: javascript, browser
---

测试新编辑器时发现在firefox下会有很高几率出现一个神奇的bug。

当光标在block元素(blockquote, pre, etc..)中时，按‘下’或‘右’或‘回车’键后，光标会选中block元素中第一段文本。刚开始怀疑是在FF下rangy设置selection的bug，但在注释所有js中keydown的处理事件后，还是会有此bug。

之后百思不得其解，甚至想到用[scribe][scribe]重写编辑器...

在观察[scribe][scribe]的demo在FF下的表现后，终于找出了这个很愚蠢的bug...

在blockquote中我特地的把p标签转换成`text + <br>`，但实际上在html4中是要求blockquote等块状元素中需要存在p标签(这是来自stackoverflow的一个回答，我没有看html4标准..)，所以我特地的去除p标签反而是画蛇添足之举。

在chrome, IE等浏览器下对于`<blockquote>test<br></blockquote>`这种html没有特殊限制，浏览器的默认行为完全可以正常工作。

但是在firefox下，当光标在`test`文本末端时，按下回车，本应换行，但是firefox会去寻找当前的p标签(这是html4规范，Firefox依赖了此规范，chrome等则没有)，但是我错误的没有把文本放入p标签，所以造成浏览器默认行为出现bug。

正确的标签应该是`<blockquote><p>test<br></p></blockquote>`这样才符合html规范。

在开发编辑器的过程中，接触到了很多这种浏览器默认行为不一致的问题。

比如firefox下偶尔会对br标签加上`type="_moz"`的属性。

chrome和safari下拖拽block中元素浏览器会把拖拽的文本放入span并且自动添加很多style属性。

在webkit内核浏览器中block元素里按回车会在下一行自动添加同样的block元素，在FF中则是自动换行。

如果一行中有br，在IE下光标在br之后，其余的浏览器则是在br之前(偶然通过range对象观测到的，在block末尾时IE中的endoffset会多1)

浏览器的很多上层API加上跨平台库已经让人很少能感受到js编程的平台差异，但是在contenteditable中诸如此类html中并无规定的默认行为在不同浏览器上的表现却是千差万别。尤其是号称跨平台的selection库rangy实际上在不同平台上还是会有很多bug与不一致，举例来说最基本的获取range对象，在webkit浏览器上取得range，start和end会优先是textElement，但是在FF上则会得到ElementNode。

html规范毕竟不可能涵盖所有情况，各种标签的嵌套以及不同情况下用户的操作，这些规范之外的情况只能靠具体的实现来决定行为。

就像各种的markdown解析器，在规定之下会输出相同的结果，但若在规定之外，每个parser都会有些许的差别。

看来浏览器距离完美的平台还有不短的距离..

[scribe]: https://github.com/guardian/scribe
