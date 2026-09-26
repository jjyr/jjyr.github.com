---
title: "What Directions Are Left for Coding Agents?"
date: 2026-03-22T10:00:00+08:00
draft: false
---

In March 2026, AI agents can run continuously for hours generating high-quality code, yet they might still make blatantly foolish decisions on minor design details. Coding agents like Claude Code, Codex, and OpenCode have nearly conquered the market, but personal and self-hosted coding agents continue to emerge.

I am also experimenting with writing my own coding agent. This article explores which directions are still worth pursuing for coding agents at this juncture.

## Task Orchestration

The "Big Three" (Claude Code, Codex, OpenCode) all support multi-agent orchestration.

We can use workflow orchestration plugins such as `superpowers`, `compound-engineering-plugin/`, etc., to manage the brainstorm -> plan -> execute -> review lifecycle, and assign multiple agents to act as distinct team members collaborating at specific stages.

Multi-agent setups prove more effective in many scenarios: assigning each agent a single domain maximizes context utilization while reducing overall run time. However, such orchestration remains largely linear—quite different from what I envision.

In my view, task orchestration should more closely resemble real-world software engineering workflows, decomposing tasks along two dimensions:
1. Decomposing the feature across domains.
2. Letting the agent responsible for each domain further break down tasks within that domain.

Tasks across domains could be developed in parallel on separate branches / worktrees and submitted individually. An overall reviewer and verifier would then perform final validation before merging into the main branch. Domain agents remain alive throughout the process to handle rework on demand.

This maximizes context efficiency while parallel execution saves substantial time.

## Memory

ChatGPT introduced memory early on. I once discussed an indie game development idea with ChatGPT, which it remembered; for over a year afterward, every programming question I asked was framed using game development analogies. This left me feeling guilty about the abandoned project, and I ultimately had to wipe the memory to fix it.

I see two primary roles for a memory system:

The first is contextual memory, supplementing the prompt context. For instance, remembering what the user is working on reduces repetitive input. I use a global `AGENTS.md` to record login procedures and purposes for remote machines, allowing ChatGPT to retain this context automatically. Since we are discussing purpose rather than implementation (which constantly evolves), I consider `AGENTS.md` a form of memory.

The second is behavioral memory—recording user habits and using historical actions to inform decisions. Recently, Codex added agent-assisted review approvals to automatically permit low-risk actions. This comes close to my expectation for decision support, though currently each review approval appears to exist in isolated context without connecting to a unified memory system.

A proper memory system must record, update, and decay memories automatically. Adding instructions to a global `AGENTS.md` and updating it periodically achieves similar results today, but still frequently relies on manual prompt triggers. A superior memory system would enable users to define memory policies and adapt memories more proactively.

## Scheduled Tasks

The latest Claude Code supports scheduled tasks, though I can no longer use it.

I frequently combine agents with cron jobs to manage servers.

Operating system cron jobs inspect application logs daily and generate reports.
An AI agent analyzes the report to determine application health. If unexpected conditions occur, it summarizes them into a bug report, which a coding agent later fixes. Afterward, an AI agent analyzes whether our cron scripts should be updated to observe additional areas.

Collect logs -> Agent summarizes -> Detect anomalies -> Generate bug report -> Optimize script next iteration

I regularly prompt the AI with essentially identical instructions; native agent support for scheduled tasks makes this workflow far more automated.

## Introspection

The sections on memory and scheduled tasks already touched upon introspection. When we instruct a coding agent to optimize code further, double-check errors, or refine a workflow, it often provides actionable suggestions.

Optimizing a coding agent is true metaprogramming: every improvement immediately benefits all projects and subsequent development cycles.

Introspection should be integrated directly into the workflow, eliminating repeated manual prompting.

## Omakase

In the distant future, upcoming features from Claude Code / Codex may flatten differentiation across coding agents. But until models approach perfection, the areas discussed here—and potentially many more—leave ample room for personalized agent specialization.

> *Omakase* refers to leaving the menu entirely to the chef; even within the bounds of traditional Japanese cuisine, there is ample room for distinct expression.
