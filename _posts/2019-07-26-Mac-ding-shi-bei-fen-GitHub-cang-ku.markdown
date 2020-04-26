---
layout: post
title: "Mac 定时备份 GitHub 仓库"
data: 2019-07-26 23:38
comments: true
tags: git mac
---

GitHub 身为一家在美国的公司，随时有可能不出乎意料的由于不可抗原因停止对用户的服务。

### 1. 安装备份脚本

[python-github-backup](https://github.com/josegonzalez/python-github-backup) 提供了足够多的备份选择 repos, issues, PR 等等，几乎 GitHub 上有价值的信息都可以备份，而且还支持从 MacOS KeyChain 里读取 GitHub token

安装最新版 python-github-backup，README 中表示支持 python3，但我使用时仍遇到了些兼容问题，使用 python2 可以正常运行

`pip install git+https://github.com/josegonzalez/python-github-backup.git#egg=github-backup`

安装完成，执行命令试一试能否成功备份

### 2. 申请 GitHub personal access token

去 GitHub 申请 [personal access token](https://github.blog/2013-05-16-personal-api-tokens/)

尝试执行命令，替换 `jjyr` 为自己的用户名，`access_token` 为实际 token，以及替换备份目录路径

`github-backup jjyr -t access_token --output-directory /Users/jiangjinyang/github_backups --repositories`

执行后会把所有 repos clone 到备份目录下，我只有备份 repos 的需求, 其他选项详见 [python-github-backup](https://github.com/josegonzalez/python-github-backup)

### 3. 在 Mac 上设置定时任务

按照 Apple 推荐使用 launchd 来设置定时任务

我们在 `~/Library/LaunchAgents/` 下新建一个 plist 文件 `~/Library/LaunchAgents/github-backup.plist`

> 在 `~/Library/LaunchAgents` 下的 plist 只会当前用户有效，
> plist 的配置和 launchd 其他用法详见[官方文档](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html#//apple_ref/doc/uid/TP40001762-104142)

文件内容为

``` plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jiangjinyang.github-backup</string>
    <key>KeepAlive</key>
    <false/>
    <key>RunAtLoad</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
      <key>http_proxy</key>
      <string>http://127.0.0.1:1087</string>
      <key>https_proxy</key>
      <string>http://127.0.0.1:1087</string>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/jiangjinyang/github_backups/backup.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jiangjinyang/github_backups/backup.err.log</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/github-backup</string>
        <string>jjyr</string>
        <string>-t</string>
        <string>access_token</string>
        <string>--output-directory</string>
        <string>/Users/jiangjinyang/github_backups</string>
        <string>--repositories</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>6</integer>
        <key>Hour</key>
        <integer>00</integer>
        <key>Minute</key>
        <integer>03</integer>
    </dict>
</dict>
</plist>
```

* 把 Label 改为自己喜欢的服务名，这里我用的 `com.jiangjinyang.github-backup`
* 把 EnvironmentVariables 中的环境变量改为自己使用的网络加速服务，如果没有则删掉这段
* StandardOutPath 和 StandardErrorPath 是备份服务输出日志的路径，改为自己喜欢的路径
* ProgramArguments 中改为自己使用的命令参数
* 调整 StartCalendarInterval 中的定时参数，示例中是每周备份一次

保存文件并加载备份服务到 launchd，注意因为放在 `~/Library/LaunchAgents` 下面不需要用 `sudo`

`launchctl load -w ~/Library/LaunchAgents/github-backup.plist`

用 `list` 命令输入服务名查看服务信息

`launchctl list com.jiangjinyang.github-backup`

使用 `start` 命令调用服务

`launchctl start com.jiangjinyang.github-backup`

这时再用 `list` 命令可以看到服务的 PID

看到日志文件输出，repos 正常备份后，代表我们的配置成功，服务会定时来备份 GitHub

再无后顾之忧
