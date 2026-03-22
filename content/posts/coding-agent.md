---
title: "Coding agent 还有哪些方向可以做？"
date: 2026-03-22T10:00:00+08:00
draft: false
---

2026 年 3 月，现在的 AI agent 可以持续几个小时运作去生成高质量代码，也可能在一个细节设计上做出明显愚蠢的决策。Claude code, Codex, Opencode 等 coding agent 几乎占领市场，但个人自用的 coding agent 也层出不穷。

笔者也在尝试写自己的 coding agent, 本文探讨笔者认为在当下时间点 coding agent 仍然值得做的方向。

## 任务编排

御三家(Claude code, Codex, Opencode) 都支持多 agent 编排。

我们可以使用 Workflow 编排插件如 `superpowers`, `compound-engineering-plugin/` 等来完成 brainstorm -> plan -> 执行 -> review 的流程，以及在其中某些环节让多 agent 作为不同的团队成员角色去合作完成。

多 agent 在很多场景都能做到更有效，每个 agent 负责一个 domain 可以做到高效的利用 context，且让 coding agent 整体耗时更短。但是这种编排仍然是线性的，和笔者想象中的编排差别很大。

笔者想象中的任务编排应该更像实际的开发流程，这个开发流程应该从两个维度去分解任务：
1. 这个功能如何按照 domain 拆分
2. 每个 domain 中的任务应该交给负责对应 domain 的 agent 去进一步拆分

每个 domain 的任务可以并行在不同的 branch / worktree 开发，并最终分别提交，由整体的 reviewer 以及验证者来做最终的验证并合并到 main branch。Domain agent 在整个流程中保持存活以便随时返工。

这样的方式能最大化利用 context ，而且并行执行节省时间。

## 记忆

ChatGPT 很早就已经支持了记忆，笔者曾经和 ChatGPT 聊过开发独立游戏的 idea，并被 ChatGPT 记住，因此在之后的一年多，每次询问编程相关话题都要用游戏开发举例子，让笔者为放弃的 idea 深感内疚，最终只能删除记忆解决。

记忆系统在笔者看有两个作用

第一个作用是作为 context 的补充，比如 ChatGPT 能记住用户在做些什么减少用户的重复输入，笔者会用全局的 `AGENTS.md` 记录远程机器的登陆方式，以及用途，这样 ChatGPT 可以自动保持这些上下文。这里我们探讨的是作用而非具体实现方式(实现方式总会一直变化)，因此笔者认为通过 `AGENTS.md` 也可以算作记忆。

第二个作用是记住用户行为，从已知的用户行为来帮助决策。最近 Codex 支持通过 agent 来 review
 approval 自动通过低风险的授权，这个功能有接近我预期的辅助决策，只是目前似乎每次 review approval 都是独立的上下文，尚未接入记忆系统。

记忆系统需要能做到自动记录、更新、以及衰减记忆。目前通过增加一部分的提示词到全局 `AGENTS.md` 并定期去更新 `AGENTS.md` 可以做到类似的效果，但仍经常需要手动提示词来触发。一个更好的记忆系统应该允许用户自定义记忆管理的策略，并更加主动的去调整记忆。

## 定时任务

最新的 `claude code` 支持定时任务，但是笔者已经无缘使用。

笔者经常使用 agent + 定时任务的方式来管理服务器。

通过操作系统定时任务每天检查服务器中应用运行日志并生成 report。
通过 AI agent 去分析 report, 并判断应用程序是否足够健康，如果服务器上发现了一些非预期情况就自动总结为 bug report, 之后再由 coding agent 去修复。

修复后通过 AI agent 分析我们的定时脚本是否需要优化，去覆盖更多需要观察的部分。

笔者定期 prompt AI，每次的提示词都差不多，agent 支持定时任务可以让这些工作更加自动化。

## 自省

在记忆、定时任务两个章节已经包含了关于“自省”的讨论，我们对 coding agent 说再优化一下代码，再检查一下错误，优化一下流程，coding agent 往往会给出有效的建议，自省应该被集成到流程中，避免手动重复。

## 元编程

优化 coding agent 是真正的元编程

每次对 agent 优化都会直接作用到所有的项目中，以及后续的开发流程中。可能未来 Claude code / Codex 扩展的新功能会抹平一切 coding agent 的独特性，但是在逼近完美之前我相信仍有足够的时间和空间可以去尝试。
