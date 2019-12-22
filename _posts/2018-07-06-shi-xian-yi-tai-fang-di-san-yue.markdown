---
layout: post
title: "实现以太坊第三月"
data: 2018-07-06 01:07
comments: true
---

系列第三篇文章。转眼之间三个月过去了，还是没有实现以太坊。两个月实现以太坊是不可能的了，黄皮书又不想看，只能写写文章装逼度日。

不过的确是学到了非常丰富的知识，并且对以太坊核心组件的内外有了整体概念。

我在这段时间从[黄皮书]实现了 EVM 和 Chain (后来几个命令实在看不下去参考了 py-evm)，有时会想是不是 Gavin wood 故意把黄皮书写的如此晦涩，来根据智商过滤实现者？为什么简单的规则非要用到这么多符号？公示的解释还是层层递归？耗尽了我的调用栈。

以太坊的规范化的确不是很好，Trie 等规则只有黄皮书上晦涩的公式，和 [Ethereum Wiki] 上并不完整的解释。唯一用来保证以太坊规范并且值得赞扬的是 [Ethereum tests] 项目，通过了这个项目的所有测试，就可以认为你基本实现了以太坊协议。

[Ciri] 项目 3 个月的工作成果转化成了在 Ethereum tests 上通过的八千多个测试(VMTest, VMStateTest, RLPTest, 常跑的有 5726 个测试，其余的测试耗时长跳过)。主要的测试部分还剩下 BlockChainTest 没有通过，这部分包含了以太坊大量的 Fork 规则，和各种区块运行状态的判断，通过了这个测试可以说算是完整的实现了**以太坊的核心**。(更新：现在 [Ciri Ethereum][Ciri] 已经通过了 Constantinople 分叉之前的所有测试!)

同时还输出了 ciri-rlp ，实现了以太坊的 RLP 编码（还是要吐槽下官方 Wiki 给的 RLP python 代码示例都是错的，而且 RLP 根本没有 Wiki 上这么简单）。

想要实现完整的以太坊客户端，还剩下 P2P 网络层, JsonRPC Server，KeyStore, CLI 等很多东西。看起来短时间内完成是不可能的了。

继续做的话下一步需要通过 BlockChainTest，不过的确是个体力活，主要是处理各种细节的错误。

写这篇文章是为了做个总结(snapshot)，暂时中断下目前放在 Ciri 项目上的工作。

实现以太坊实在是太消耗时间和体力了(不是年轻时拼体力能解决的了..)，很难仅仅依赖业余时间完成，之后应该会拿出更多精力放在其他东西上。把 [Ciri Ethereum][Ciri] 作为更长期的项目，在闲暇时继续开发吧。

同时我更想把 [Ciri Ethereum][Ciri] 作为一个社区化的开源项目来开发，下面是项目的 Wiki 页的内容，整理了目前的状态和长期 Roadmap 规划

<https://github.com/ciri-ethereum/ciri/wiki>

[Ethereum Wiki]: https://github.com/ethereum/wiki/wiki
[黄皮书]: https://ethereum.github.io/yellowpaper/paper.pdf
[Ciri]: https://github.com/ciri-ethereum/ciri
[Ethereum tests]: https://github.com/ethereum/tests
