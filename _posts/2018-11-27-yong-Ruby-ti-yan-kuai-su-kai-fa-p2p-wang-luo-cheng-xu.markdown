---
layout: post
title: "用 Ruby 体验快速开发 P2P 网络程序"
data: 2018-11-27 23:48
comments: true
---

很多开发者很熟悉 Server-Client 这一套网络结构，Server-Client 是构建互联网应用的基础。
但在区块链技术这里就有点过时了，区块链的世界普遍采用 P2P 网络。

P2P network 是什么呢？

> 对等式网络（peer-to-peer， 简称P2P），又称点对点技术，是无中心服务器、依靠用户群（peers）交换信息的互联网体系，它的作用在于，减低以往网路传输中的节点，以降低资料遗失的风险。与有中心服务器的中央网络系统不同，对等网络的每个用户端既是一个节点，也有服务器的功能，任何一个节点无法直接找到其他节点，必须依靠其户群进行信息交流。
> 
> From 维基百科

`ciri-p2p` 是在我尝试实现以太坊协议([Ciri Ethereum](https://github.com/ciri-ethereum/ciri)) 时的一个副产品，使用这个库可以轻松的用 Ruby 来实现 P2P network 服务

考虑到如果可以用 Ruby 来试验各种 P2P 网络协议会非常爽，
所以我把以太坊的底层 P2P 通信协议 -  DevP2P 的实现作为了单独的一个库抽离了出来。

DevP2P 是一个相对独立的协议，和区块链、以太坊都没什么太多关联，
所以 `ciri-p2p` 也可以用来做和区块链完全不相关的事情：比如实现个 “基于 P2P 网络的 DNS 服务”，我们会在下文中用 `ciri-p2p` 来实现这个例子。

-----------------

DevP2P 主要包括了以下部分：

1. 基于公私钥的端到端加密
2. 基于 DHT 的发现协议
3. 架构上分层，支持多个子协议复用连接

在 `ciri-p2p` 中，前两点对于用户来说是透明的，我们只需要实现一个子协议来完成我们的应用逻辑

我们的示例是实现一个在 P2P 网络中可以与其他节点交换、发现网址的服务。

为了简化设计，我们设计为只去发现程序员们最喜爱的网站 - 1024 的最新网址列表。

实现子协议的代码：

``` ruby
require 'ciri/p2p/server'
require 'ciri/p2p/protocol'
require 'ciri/key'
require 'json'
require 'async'

# 来给 1024 发现协议起个优雅的名字，就叫 GossipDNS
class GossipDNS < Ciri::P2P::Protocol
  # code of our messages
  # 定义两个消息的 ID
  # 我们的简化协议只支持
  # FIND_URLS 查询 url 列表
  # NEW_URLS 返回 url 列表
  FIND_URLS = 1
  NEW_URLS = 2

  attr_reader :dns_records

  # 传入我们知道的 1024 最新网址列表
  def initialize(urls:) 
    # 设置我们的协议名称、版本、长度
    super(name: "1024discovery", version: 1, length: 8096) 
    @urls = urls 
  end
  
  # 协议初始化时会调用，context 代表当前网络的上下文
  def initialized(context) 
    puts "Service started!"
    # ciri-p2p 依赖 async 框架进行异步 IO 操作
    # 这里我们用 async 框架提供的定时功能每 10s 向所有 peers 请求最新列表
    task = Async::Task.current 
    # 每 10s 执行
    task.reactor.every(10) do
      # 取到当前连接的所有 peer
      context.peers.each do |peer| 
        task.async do
          # 对每个 peer 发送 FIND_URLS 消息, 注意这里 data 为空
          context.send_data(FIND_URLS, '', peer: peer) 
        end
      end
    end
  end
  
  
  # 收到消息时会调用
  def received(context, msg) 
    # check msg code
    case msg.code 
    when NEW_URLS
      # 收到新的 url 列表
      urls = JSON.load(msg.payload) 
      puts "receive #{urls.count} urls from #{context.peer.inspect}"
      @urls = (@urls + urls).uniq 
    when FIND_URLS
      # 收到请求消息，返回 url 列表
      puts "send #{@urls.count} urls to #{context.peer.inspect}"
      context.send_data(NEW_URLS, JSON.dump(@urls)) 
    else
      puts "received invalid message code #{msg.code}, ignoring"
    end

    # 输出当前节点和 url 列表
    puts "[#{context.local_node_id.short_hex}] current urls:"
    puts @urls
  end

  def connected(context) 
    puts "connected new peer #{context.peer.inspect}"
  end

  def disconnected(context) 
    puts "disconnected peer #{context.peer.inspect}"
  end

end
```

这段代码实现了 1024 发现协议的核心逻辑，注意 received 方法里我们针对收到的两个消息进行了不同的处理。整个应用由初始化时的定时任务触发。


下面来实现创建节点的代码

``` ruby
def start_node(protocols:,
               private_key: Ciri::Key.random, 
               bootnodes:, 
               host: '127.0.0.1', tcp_port: 0, udp_port: 0) 
  Ciri::P2P::Server.new( 
    private_key: private_key, # private key of our node, used for encrypted communication
    protocols: protocols, # 节点运行的协议
    bootnodes: bootnodes, # 节点启动时去连接的其他节点
    host: host, 
    tcp_port: tcp_port, # node port
    udp_port: udp_port, # port for discovery
    discovery_interval_secs: 5, # try discovery more nodes every 5 seconds
    dial_outgoing_interval_secs: 10, # try connect to new nodes every 10 seconds
    max_outgoing: 4, # number of nodes we will try to connect
    max_incoming: 8, # number of nodes we will accept
  ) 
end
```

注意这个方法的 protocols 参数，这里我们传入要启动的子协议，这些协议就会自动被节点运行。其他的参数是节点启动时的一些配置，查阅注释应该可以理解。


然后我们实现启动节点的代码：

``` ruby
# 我们来写启动两个节点的示例
def start_example
  puts "start example"
  # 启动 async 框架的 reactor
  Async::Reactor.run do |task| 
    # 随机一个 key 作为 node1 的私钥
    # 补充下公钥会作为节点地址的一部分，所以我们这里事先生成 key
    node1_key = Ciri::Key.random 
    # 初始化我们的协议，填入 1024 的最新网址获取方法
    protocol1 = GossipDNS.new(urls: ['baidu.com']) 
    # node2 的协议
    protocol2 = GossipDNS.new(urls: ['google.com']) 

    # start node1
    task.async do
      start_node(protocols: [protocol1], private_key: node1_key, bootnodes: [], tcp_port: 3000, udp_port: 3000).run 
    end
    
    # start node2
    task.async do
      # 注意这里的地址包含了 node_id 和 address，DevP2P 中节点地址是由这两部分组成。
      node1 = Ciri::P2P::Node.new( 
        node_id: Ciri::P2P::NodeID.new(node1_key), 
        addresses: [ 
          Ciri::P2P::Address.new( 
            ip: '127.0.0.1', 
            udp_port: 3000, 
            tcp_port: 3000, 
          ) 
        ]) 
      start_node(protocols: [protocol2], bootnodes: [node1], tcp_port: 3001, udp_port: 3001).run 
    end
  end

end

if caller.size == 0
  # 设置 ciri-p2p 的日志
  Ciri::Utils::Logger.setup(level: :info) 
  start_example 
end
```

上述代码涉及了一些 `async` 框架的部分，分别启动了两个节点，设置了 node2 的 bootnodes 参数，这样 node2 会去主动连接 node1。等待 10s 左右就会看到节点间互相传递数据的日志。

全部代码整理在 [gossip-dns-example](https://github.com/jjyr/gossip-dns-example) ，可以直接 clone repo 来启动。

在示例仓库目录下运行 `bundle install && bundle exec ruby app.rb`

产生如下日志，节点成功交换网址！

``` bash
start example
Service started!                                        
I, [2018-11-28 00:00:02#6306]  INFO -- Ciri::P2P::Server: start accept connections -- listen on localhost:hbci
Service started!
I, [2018-11-28 00:00:02#6306]  INFO -- Ciri::P2P::Server: start accept connections -- listen on localhost:redwood-broker
I, [2018-11-28 00:00:02#6306]  INFO -- Ciri::P2P::Discovery::Service: start discovery server on udp_port: 3000 tcp_port: 3000
local_node_id: 0xfcf53c4df3f3202c9b4835cad688828abdd01e3123dee1bcb5a6408199360f92e225a4d2e2d04e2e0f7002c1bde328e13c107ccd43140f08ce052f53753d3458
I, [2018-11-28 00:00:02#6306]  INFO -- Ciri::P2P::Discovery::Service: start discovery server on udp_port: 3001 tcp_port: 3001
local_node_id: 0x1640206ef2b13fb80c4b4d7af34cd3e1b319f2a4c139724d157458df456569487b17cd787072b94de1776c40bf51b8d4d1cfff56358dc5ecf7472fa2fe2d1d28
I, [2018-11-28 00:00:03#6306]  INFO -- Ciri::P2P::NetworkState: [0x1640206] connect to new peer <Peer:0xfcf53c4 direction: outgoing>
connected new peer <Peer:0xfcf53c4 direction: outgoing>
I, [2018-11-28 00:00:03#6306]  INFO -- Ciri::P2P::NetworkState: [0xfcf53c4] connect to new peer <Peer:0x1640206 direction: incoming>
connected new peer <Peer:0x1640206 direction: incoming>
send 1 urls to <Peer:0xfcf53c4 direction: outgoing>
[0x1640206] current urls:             
google.com                                  
receive 1 urls from <Peer:0x1640206 direction: incoming>                                                                        
[0xfcf53c4] current urls:                                                                                                        
baidu.com                                                                                                                       
google.com
```

这是个很简单的示例程序，展示了 `ciri-p2p` 的基本用法，`ciri-p2p` 本身的功能还是很完善的，结合 `async` 框架我们甚至可以把示例扩展为真正可用的 P2P 版 DNS。

区块链或其他的 P2P 网络环境中还有很多有趣的协议值得研究，不妨用 `ciri-p2p` 来实现下。

要注意的是，真实的 P2P 网络中，一定要考虑到 peer 间是无法信任的，像示例中这样简单的协议，很可能跑一整天也发现不了真正的网址。

* Ciri-p2p [https://github.com/ciri-ethereum/ciri-p2p](https://github.com/ciri-ethereum/ciri-p2p)
* 示例代码 [https://github.com/jjyr/gossip-dns-example](https://github.com/jjyr/gossip-dns-example)
