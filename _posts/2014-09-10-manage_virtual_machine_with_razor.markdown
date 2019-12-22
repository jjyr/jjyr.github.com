---
layout: post
title: "通过Razor管理Virtual box虚拟机"
data: 2014-09-10 23:32
comments: true
categories: razor VM DHCP PXE iPXE
---

打算在mac上用虚拟机玩下云。之前工作中用到了[Razor](https://github.com/puppetlabs/razor-server)，于是萌生了用Razor来管理虚拟机的想法(顺便试验下最近很火的docker)。

为了让开发机尽量保持"干净"，决定用docker来做个razor-server的镜像(docker pull jjy0/razor 可以下载到)

制作镜像还算顺利，没想到在虚拟机的网络配置和IPXE boot上栽了跟头，记录在此引以为戒，同时期望能帮助到他人(没接触过PXE boot或Razor的朋友就此别过！)

用docker启动 razor-server非常简单
`docker run -d -p 8080:8080 jjy0/razor start`
在本地安装razor-client`gem install razor-client`
已经完成了razor的安装！

接下来根据官方教程配置[PXE boot](https://github.com/puppetlabs/razor-server/wiki/Installation#pxe-setup)


#### VMware Fusion的坑
刚开始我使用的是Vmware Fusion，在一台虚拟机中设置好了razor和DHCP server，却无法被同网络其他机器探测到。
没能找到解决办法，之后使用Vmware自带的DHCP server redirect到razor，发现Vmware自导的dhcpd版本过低(2.x)不支持chain命令，只好作罢


#### Virtual Box的坑
转战到Virtual Box
我搜索了一番，发现[已有前人尝试过](http://www.0xf8.org/2013/02/pxe-booting-inside-virtualbox-and-kvm-virtual-machines-stopwatched-1/)比较简单的方法(把dhcp-server假设在host上)。决定使用这种方法

1. 先按照上文链接中得做法建立host-only net
2. 查看现有dhcp server`VBoxManage list dhcpservers`
3. 禁用相应网络的dhcp server`VBoxManage modify --netname HostInterfaceNetworking-vboxnet0 --disable`
4. 按链接中方法配置dhcp server
5. 启动裸机
6. 成功发现DHCP server!!

#### iPXE的坑
正当我高兴时发现ipxe脚本报错，原来是网卡不支持HTTP协议..

1. 更换虚拟网卡...发现Virtual Box的网卡全不支持HTTP功能..
2. 按照ipxe官网使用[chainloading](http://ipxe.org/howto/chainloading)
3. 发现虚拟机上网卡支持ipxe却不支持HTTP协议，所以DHCP server这边判断可以支持ipxe，但是client 执行到chain http...会报错
4. 改用ISC-dhcp + tftpd
安装dhcpd与tftpd
并更改razor wiki给的脚本
`if exists user-class and option user-class = "iPXE"`
改为
``` bash
option space ipxe;
option ipxe.http code 19 = unsigned integer 8;
...
if exists ipxe.http
...IPXE
} else {
...undionly
}
...
```
通过dhcpd ipxe的扩展，判断客户端是否支持ipxe和http
启动dhcpd和tftpd
重启虚拟机，客户端在加载undionly.kpxe后再次加载bootstrap.ipxe
成功!!

这时bootstrap.ipxe脚本会请求razor server
确认其中url指向docker host的8080端口(这里也可以随意映射到任意端口)
我们的razor container也在正常启动的话就可以看到ipxe界面上下载microkernel
在docker hosts上输入razor nodes正常的话会看到虚拟机
全部成功！！

#### 感想

1. iPXE和razor官方推荐的都是dhcpd(isc-dhcp)，并且dhcpd支持更多的选项和ipxe扩展，相比dnsmasq应优先使用isc-dhcp
2. 我在docker的razor镜像中加入了配置链接外部postgreSQL的支持razor-server下载的各种OS镜像可以通过挂在volume来放在host上，但用起来(个人开发)还是感觉直接部署在虚拟机上更加简单。之后打算继续尝试DHCP和razor server都放在虚拟机的方法
3. 在OSX上做linux相关的东西还是很麻烦
4. mac的launchd好难用，看个log都这么麻烦，比systemd差多了
5. mac的内存管理好差，开virtual box + dhcpd经常爆内存
6. 有点想在macbook上装centos用..
