---
layout: post
title: "实现以太坊第二周 RLPX 子协议、Actor 模型"
data: 2018-05-14 23:22
comments: true
tags: Ethereum
---

根据上篇继续： [实现以太坊第一周 DEVP2P::RLPX 握手协议](http://justjjy.com/2018/05/06/shi-xian-yi-tai-yi-zhou-DevP2P-RLPX-DevP2PRLPX-wo-shou-xie-yi/)

本周比较懒，字写的尽量少一点。

--------------

上周实现了以太坊的网络协议 DevP2P 中的握手部分。DevP2P 还包括了节点发现功能，子协议传输功能，还有整合了所有以上逻辑的 Server。

下一步我打算优先实现以太坊子协议，而不是继续实现 DevP2P 的其他功能。

以太坊子协议定义了一整套以太坊节点间的消息格式：同步区块，获取交易信息，获取区块头等等。实现了以太坊子协议，就可以接着实现区块同步，挖矿，还有相关的 web 3 接口。这部分功能触及了区块链、以太坊的核心机制，实现起来很有意思。比起单纯的 DevP2P 协议更有趣，所以我们采用深度优先的方式来实现以太坊，先做个能部分使用的客户端。

以太坊子协议是通过 DevP2P 中『RLPX 子协议』功能实现。上周我们实现了 RLPX 握手，握手之后就可以通过 RLPX 传输数据。RLPX 使用子协议的概念进行数据传输。


RLPX 子协议
----------

RLPX 包包含了 code, size, payload 三个字段。

``` text
RLPX 包(message): code | size | payload
```

payload 中用来保存二进制信息。(经过以太坊使用的 RLP 编码后的内容)

『RLPX 子协议』是在 RLPX 包之上的逻辑，允许包中传输几个不相干的子协议信息。

RLPX 通信时要求两个节点事先知道自己支持的子协议的 name、version、length 。

发送信息时按照 name， version 排序，并用 message code 代表当前协议的偏移量。

这样两个节点知道协议的顺序、长度，也知道偏移量，发送消息时如下：

``` text
预先知道:
protocol-1(name: "eth", version: 63, length:17)
protocol-2(name: "test", version: 1, length:20)

RLPX 包(message): code | size | payload

发送 protocol-1 时:
code: 16(message 头，固定 16)
payload: protocol-1 内容

发送 protocol-2 时，protocol-2 排序在 p1 之后，所以 code 要加上 p1 的偏移量:
code: 16(message 头) + 17(p1 的长度)
payload: protocol-2 内容
```

可以看出，通过 message code 偏移，RLPX 能够实现一个包中同时存在多个协议，
但目前看 geth 代码中并没有这样使用。
于是接收者也能按照同样规则解析不同的子协议。


Actor 模型
----------

参考 geth 简单的实现了DevP2P Server 的基础功能，Server 能主动连接 bootnode 并进行以太坊子协议的握手。

DevP2P Server 维护多个节点(peers)，每个节点同时有多个子协议，不同的子协议理论上都是可以并发处理的。

geth 大量使用 channel 和 go-routine 处理并发逻辑，导致代码有点混乱。

如果用 Actor 模型，接口会更整洁。

Actor 是个自动执行的实体，和对象不同，只能通过发送或接收消息来和 Actor 通信。

初接触 Actor 模型时没感觉和 CSP 有太大差别，现在看 Actor 抽象程度更高。

我发现 Actor 的最大优势就是在于使用消息的交互方式。这种交互方式可以对用户屏蔽更多的信息。调用传统库我们需要关心代码是否线程安全，而 Actor 的消息接口则对用户屏蔽了这一点，我们只需对 Actor 发送消息，等待回复，而具体代码由 Actor 执行，自然调用者不需要考虑并发、多线程安全等等问题，细节部分对调用者完全屏蔽。

我在实现 Server 相关逻辑时，用 200 行 ruby 实现的精简 Actor 模型 [GitHub](https://github.com/ruby-ethereum/ethruby/blob/1ceecac4152ed2ba99609bf30e0f5b88ee2d8647/lib/ethruby/devp2p/actor.rb)

ethruby 项目地址 [ruby-ethereum/ethruby](https://github.com/ruby-ethereum/ethruby)
