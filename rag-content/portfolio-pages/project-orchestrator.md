> What if AI could execute your entire development plan autonomously -- and you only had to review the finished work?

## The Problem

Working with AI coding assistants is powerful, but it comes with a hidden cost: you are the bottleneck. Every file change needs your approval, every test run waits on your confirmation, every step requires a human in the loop. For a solo founder juggling product, marketing, and family, that means "AI-assisted development" still eats your entire afternoon. The value of AI drops dramatically when the human cost of supervising it stays high.

## My Role

I designed the full system architecture, defined the communication protocol between orchestrator and executor agents, and built the implementation plan and tooling.

## The Approach

The key insight was separating planning from execution. Planning is where human judgment matters -- choosing what to build, defining the approach, setting constraints. Execution is where AI excels -- following a well-defined plan methodically, running tests, committing code. So I designed a two-tier agent system: a strategic orchestrator that works with me to plan and monitor, and tactical executor instances that receive those plans and work through them autonomously inside isolated virtual machines.

The hard trade-off was safety versus autonomy. Giving AI unrestricted filesystem and network access is dangerous. But requiring permission for every `npm install` defeats the purpose. I solved this with Vagrant VM isolation -- each project runs in a sandboxed environment where the AI has full permissions but zero access to the host system, secrets, or other projects. The plans themselves act as guardrails: executor agents follow pre-approved TDD plans mechanically, and if they hit something unexpected, they stop and flag it rather than improvising.

I enforced Test-Driven Development (RED-GREEN-REFACTOR) at the plan level, not just as a suggestion. Every code change in a plan is structured as: write a failing test, verify it fails, write minimal code to pass, verify it passes, refactor. This means the AI is continuously validating its own work as it goes.

## What I Built

- **Two-tier agent architecture** -- strategic orchestrator for planning and monitoring; tactical executor for autonomous implementation
- **File-based async communication protocol** -- plan files, status JSON, and sentinel files (.complete, .blocked) enable agents to coordinate without real-time connections
- **TDD plan generator skill** -- transforms high-level designs into granular, mechanically executable plans with explicit RED-GREEN-REFACTOR cycles for every code change
- **Isolated execution environments** -- Vagrant VMs with filesystem and network sandboxing, so autonomous agents can run with full permissions safely
- **Project lifecycle commands** -- `/setup` (create project), `/delegate` (start autonomous work), `/progress` (monitor), `/workon` (interactive session), `/stop` (halt and review)
- **Git safety model** -- all autonomous work happens on feature branches, never main; the human reviews and merges completed work
- **Blocker detection** -- executor agents self-report when stuck, halting work and surfacing the issue for human intervention rather than guessing

## The Result

The Project Orchestrator is in active development. The architecture, communication protocol, TDD plan skill, and command framework are designed and partially implemented. The system demonstrates that the hardest problem in AI-assisted development is not the AI's coding ability -- it is designing the right boundary between human judgment and machine execution. The approach I built here inverts the typical AI workflow: instead of the human supervising every step, the human defines the plan and reviews the output.

## Tech Stack

- **Orchestration:** Claude Code (Anthropic)
- **Isolation:** Vagrant VMs with VirtualBox
- **Communication:** Markdown plan files, JSON status, filesystem sentinel signals
- **Methodology:** Test-Driven Development (enforced at plan level)
- **Version control:** Git with feature branch safety model