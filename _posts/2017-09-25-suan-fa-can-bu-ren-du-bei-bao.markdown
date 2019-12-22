---
layout: post
title: "算法惨不忍睹-背包"
data: 2017-09-25 19:56
comments: true
---

看了道 leetcode 题目
https://leetcode.com/problems/ones-and-zeroes/description/

这其实是一道背包问题，使用背包的状态转移方程可以简单解决

轻轻松松试了下手，果断翻车了...

我发现并不是题目难，而是我一直没能真正理解背包算法为何会这样来设计？
每次看到解答都会感觉反直觉，无法将直觉思路联系到这种解法，而网上的解题过程也大多由结果出发，没有掌握到 why

看题目时我的直觉是对每一个字符串判断需不需要，然后利用递归计算，算法如下。

``` ruby
def find_max_form(strs, m, n)
    str = strs.first # 当前字符串
    strs = strs[1..-1] # 剩余部分
    m1 = str&.count('0')
    n1 = str&.count('1')
    if str.nil?
        0
    elsif m1 > m || n1 > n
        # 放弃不满足条件的当前字符串
        find_max_form(strs, m, n)
    else
        # 选择构成当前的字符串时的数量 find_max_form(strs, m - m1, n - n1) + 1
        # 选择不构成当前字符串时的数量 find_max_form(strs, m, n)
        # 取大的作为真正解
        [find_max_form(strs, m - m1, n - n1) + 1, find_max_form(strs, m, n)].max
    end
end
```

很符合直觉的递归，结果是执行超时。

主要问题是其计算过程是自上而下，每次计算都会需要两个子递归运算的结果，最后递归的数量是 2 的 N(strs长度) 次方。

而正解巧妙的修复了这个问题，思路就是将自上而下的算法巧妙的转换为自下而上，让每个子计算的结果都被重复利用。

``` ruby
def find_max_form(strs, m, n)
    dp = Array.new(strs.size + 1){Array.new(m + 1){Array.new(n + 1)}}
    (strs.size + 1).times do |i|
        str = strs[i - 1]
        s0 = str.count('0')
        s1 = str.count('1')
        (m + 1).times do |j|
            (n + 1).times do |k|
                if i == 0
                    dp[i][j][k] = 0
                elsif j >= s0 && k >= s1
                    dp[i][j][k] = [dp[i - 1][j - s0][k - s1] + 1, dp[i - 1][j][k]].max
                else
                    dp[i][j][k] = dp[i - 1][j][k]
                end
            end
        end
    end
    dp[strs.size][m][n]
end
```

正解很聪明的将“第N个包”放不放的问题，转换为保存“前N个包的最优解”，从而让每个计算都可以利用之前的结果。
