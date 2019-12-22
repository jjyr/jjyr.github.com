---
layout: post
title: "CSRF 矛与盾"
data: 2017-09-21 01:07
comments: true
---

CSRF(跨站请求伪造：Cross-site request forgery) 可谓老生长谈的话题，有无数的博客和文章都在讲 CSRF 攻击与防范。

近日感觉自己知识点之间存在着裂缝，无法做到了如指掌。于是弥补了下知识裂缝，并写成文章，贡献了 yet another CSRF 博文..

摘要
* CSRF 实践
* POST 比 GET 安全？
* 为什么还要 CSRF protect token?
* 前后端分离和 CORS

CSRF 实践
--------------
顾名思义，一句话概括**跨站**请求伪造(CSRF)就是：在用户浏览 A 站(恶意网站)时，伪造用户向 B 站(正常网站)发起请求。

我们用 ruby sinatra 简单的模拟下这个过程，从而更好的理解这种攻击手段。

用 a.rb, b.rb 两个脚本来模拟 A, B 站点，并修改 `/etc/hosts` 为两个站点提供不同的域名。

如果不明白可以先略过这两个脚本，之后回来再看。

``` ruby
# a.rb
# testa:4000
# 恶意网站 A, 有一个奇怪的 img 标签
require 'sinatra'

get '/' do
<<-HTML
<img src="http://testb:5000/get">
A
HTML
end
```

``` ruby
# b.rb
# testb:5000
# 善良网站 B, 提供基本的设置／获取 cookie 能力
require 'sinatra'
require "sinatra/cookies"

get '/' do
  'B!'
end

get '/set' do
  cookies[:secret] = params[:secret]
  'set!'
end

get '/get' do
  puts "secret is #{cookies[:secret]}"
  "secret is #{cookies[:secret]}"
end
```

分别启动这两个网站，现在开始模拟用户被攻击！

1. 访问 `testb:5000/set?secret=123123` 模拟用户正常使用 B 站
2. 访问 A 站

OK，这时我们打开 chrome 的开发者工具，刷新 A 站，可以看到两个请求。第一个是我们访问页面的请求，第二个则是 A 站中潜藏的 img 标签发起的请求，因为 img 的 src 属性引用到 B 站，浏览器会发送请求来尝试获取图片。

![A site chrome dev tool](/images/posts/CSRF/CSRF-1.jpg)

点击 'Response' 发现并没有显示内容，这是因为 B 返回的格式不是图片。

我们看下 B 的 server log，发现的确被访问。
![B site server log](/images/posts/CSRF/CSRF-2.jpg)

浏览器对**同源**的请求会附加上 **cookie** ，会被攻击者利用破坏你的数据，虽然示例中的 CSRF 没有造成实际损害，但我们把 A 站中的 img 的 src 换为 `testb:5000/set?secret=csrf_attack` 就会在用户不注意时写入数据，达到破坏的目的！

同样的 iframe 等 HTML 标签也会有相同效果。

经常会听说 POST 请求比 GET 要安全。仅看示例的话，如果我们把 B 的 '/set' 换成 POST 请求，上述攻击的确无法成功，但如果因此认为 POST 有更高的安全性还是 too naive。

用 POST 可以避免 CSRF 吗？
-----------
当然不可以，要不然也不会有这一节

我们就试一试 POST 是否安全

把 B 站代码略作修改
``` ruby
# get 变成 post
post '/set' do
  cookies[:secret] = params[:secret]
  'set!'
end
```

道高一尺魔高一丈，这时我们的 A 站也升级了

``` ruby
# a.rb
require 'sinatra'

get '/' do
<<-HTML
<form id="myform" method="POST" action="http://testb:5000/set">
<input type="hidden" value="321321" name="secret">
</form>

<script>
document.forms["myform"].submit();
</script>

A
HTML
end
```

访问 A，表单会自动提交到 B 站(浏览器会一起发送 B 站的 cookie)，并且成功的修改了数据。

我们可以看到使用 POST 并**没有更安全**，仅仅把 GET 换为 POST 无法保证防止 CSRF 攻击。

CSRF protect token
--------------

在流行 web 框架中基本都有 **CSRF protect token** 的概念，这就是为了防止我们在上一节演示的跨站提交表单攻击。

基本思想是 A 服务器每次渲染 form 时，同时生成一个隐藏的表单元素(token)，A 处理表单提交时验证这个 token 是否正确，如不正确就拒绝这次提交。攻击者猜不出 token 的值，自然无法提交表单进行攻击。

要注意的是 token 最好每次不同，并且不容易让人猜到，v2ex 论坛就曾因使用可以猜到的 CSRF protect token 而被人攻击。

我们来修改 B 站，实现 CSRF protect token 功能。

首先第一步，介绍一下我们的 token 生成算法。为了保证 CSRF protect token 的安全性，我们将 token 设计为: 1. 可以过期，2. 保证每个用户生成的不同，3. token 的内容是加密的无法篡改。

我们使用简单的哈希表(Hash)来表示加密前的 token：

token 结构如下

``` ruby
{
    expired_at: <unix_time>,
    current_secret: "secret" # 在实际中这里应该使用 user_id
}
```

这样当我们处理表单提交时，先检查 expired_at 验证 token 是否过期，再验证当前的 secret 是否正确(这里为了简化，使用 'cookie[:secret]' 来区分不同用户，有很大概率碰撞。实际中应使用用户的 'user_id' 来保证每个用户的 token 不同。)，只要有一个不通过我们就认为是恶意攻击。

然后我们用 JSON 序列化 token，再对其进行加密处理。下面是一段将 token 加密解密的代码

``` ruby
# 当然实际中不要用全局变量..
$iv = nil
$key = nil

def encrypt(data)
  cipher = OpenSSL::Cipher::AES256.new :CBC
  cipher.encrypt
  $key ||= cipher.random_key # 随机生成密钥
  $iv ||= cipher.random_iv
  cipher.key = $key
  cipher.iv = $iv
  encrypted_text = cipher.update(data) + cipher.final
  # 使用 base64 生成可以放心插入到 HTML 的字符串
  Base64.encode64(encrypted_text)
end

def decrypt(data)
  encrypted_text = Base64.decode64(data)
  cipher = OpenSSL::Cipher::AES256.new :CBC
  cipher.decrypt
  cipher.key = $key
  cipher.iv = $iv
  cipher.update(encrypted_text) + cipher.final
end
```

通过以上代码加密，恶意网站不知道我们的密钥，无法篡改 token；而且因为使用了 user_id 隔离不同用户生成的 token，恶意网站无法用自己账号伪造 token (示例中用的 current_secret，隔离效果不好，仅作示范)；

就算恶意网站侥幸得到了 token，我们还有过期时间的保护，只要段时间内无法对我们发起 CSRF 攻击，则还是具有一定安全。

完整代码如下：

``` ruby
# b.rb
require 'sinatra'
require "sinatra/cookies"
require 'openssl'
require 'base64'
require 'json'

get '/' do

# 使用当前时间加 60s 作为 token 过期时间
# ! 真实情况下应该使用 user_id 等信息一起加密
data = {
  expired_at: Time.now.to_i + 60,
  current_secret: cookies[:secret]
}
token = encrypt(JSON.dump(data))

<<-HTML
<form id="myform" method="POST" action="/set">
<input type="hidden" name="token" value="#{token}">
<input type="text" name="secret">
<input type="submit">
</form>

  B!
HTML
end

post '/set' do
  token_data = JSON.load(decrypt(params[:token]))
  if token_data['expired_at'] < Time.now.to_i || token_data['current_secret'] != cookies[:secret]
    return "you're bad guy"
  end
  cookies[:secret] = params[:secret]
  'set!'
end

get '/get' do
  puts "secret is #{cookies[:secret]}"
  "secret is #{cookies[:secret]}"
end

private

$iv = nil
$key = nil

def encrypt(data)
  cipher = OpenSSL::Cipher::AES256.new :CBC
  cipher.encrypt
  $key ||= cipher.random_key
  $iv ||= cipher.random_iv
  cipher.key = $key
  cipher.iv = $iv
  encrypted_text = cipher.update(data) + cipher.final
  Base64.encode64(encrypted_text)
end

def decrypt(data)
  encrypted_text = Base64.decode64(data)
  cipher = OpenSSL::Cipher::AES256.new :CBC
  cipher.decrypt
  cipher.key = $key
  cipher.iv = $iv
  cipher.update(encrypted_text) + cipher.final
end
```

这样，我们终于得到了一个安全的，可以防范 CSRF 攻击的服务。

前后端分离和 CORS
-----------

CSRF 和前后端分离有什么关系呢？是不是前后端分离的架构中就不会出现 CSRF 攻击，也不会需要 form protect token？

这话对也不对，对于服务器来说，CSRF 和前后端是否分离没太大关系，只要服务器端接受 form 请求还是有跨站提交的问题，目前基本都是使用 json 来通信，所以服务器端只要限制仅接受 **Content-Type** 为 **application/json** 格式的数据就可以避免 CSRF，至于为什么可以避免就要先介绍下 CORS。

实践过前后端分离的读者基本都会听说过 CORS 这个东西。

CORS 是在前端复杂化、后端 API 化后，为了避免类似 CSRF 攻击的悲剧而加入的限制策略。浏览器在发出真正请求前会先使用 'OPTION' 请求询问服务器接受哪种 'Method'，哪些 'Headers'，如果发现 js 发出的请求不被服务器接受，则会禁止发送并报错。

![No 'Access-Control-Allow-Origin' header](/images/posts/CSRF/CSRF-3.jpg)

如上图所示，浏览器发现 js 请求的域名没有提供 **Access-Control-Allow-Origin**，于是报错。

CORS 可以参考 MDN 的详细介绍:
https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Access_control_CORS

值得一提的是在发送**简单请求**时，不会触发 'OPTION' 的验证。
根据 MDN 文章的解释，当使用 'GET', 'HEAD' 请求，或使用  'POST' 但 'Content-Type' 的值为 'text/plain'、 'multipart/form-data'、'application/x-www-form-urlencoded' 时，浏览器**不会进行验证**。

这也就解释了 CORS 的控制边界，之前示范的表单提交属于简单请求，所以跨域不受浏览器限制。而前后端分离时大多使用 json 交互，这时就进入了 CORS 的保护范围。

至于 form 提交，作为最基本的数据提交方式，跟随 Web 标准发展了几十年，仍因兼容性而允许跨站提交。幸好 Web 生态圈有社区推动的各种解决方案来不断的完善，才会有 csrf protect token 等方案让 Web 平台更加安全开放。
