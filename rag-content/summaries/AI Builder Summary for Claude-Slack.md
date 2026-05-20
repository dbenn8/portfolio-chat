# AI Builder Summary for Claude-Slack

## Part 1: Job Fit Analysis

### Project Overview

**claude-slack** is a bidirectional Slack integration for Claude Code that enables mobile control of AI coding sessions. It bridges the gap between a terminal-based AI coding agent and a mobile-accessible messaging platform, allowing developers to monitor, respond to, and direct Claude Code sessions from their phone.

**Why it exists:** Claude Code is a powerful AI coding agent, but it runs in a terminal. When it needs human input -- permission approvals, design decisions, clarification -- you have to be at your laptop. This project removes that constraint entirely.

### Relevance to n8n AI Product Builder Role

#### AI Building / Super Agent Workstream

**This project IS an AI agent orchestration system.** It does not just call an API; it wraps, monitors, and extends an autonomous AI coding agent with human-in-the-loop capabilities accessible from anywhere.

Key demonstrations:

1. **Agent Session Management at Scale**
   - Multi-session registry (SQLite with WAL mode) supporting unlimited concurrent Claude Code sessions
   - Each session gets its own Slack thread, Unix socket, lifecycle state machine, and output queue
   - Singleton registry pattern with thread-safe database transactions via SQLAlchemy
   - Session lifecycle with 7 states (INITIALIZING, ACTIVE, IDLE, WAITING, ENDED, CRASHED, ARCHIVED) and validated state transitions

2. **Event-Driven Hook Architecture**
   - Three hooks that tap into Claude Code's event system: `on_stop` (assistant response complete), `on_notification` (permission requests, idle prompts), `on_pretooluse` (intercepts AskUserQuestion tool calls)
   - Hooks are deployed as templates -- the launcher copies versioned hooks into each project's `.claude/hooks/` directory, with automatic version detection and updates
   - Every hook discovers its parent installation dynamically (env var, upward directory search, home directory fallback) -- portable across any project

3. **Real-Time Permission Detection and Routing**
   - PermissionDetector processes raw PTY output byte-by-byte, strips ANSI codes, identifies permission anchor keywords, extracts numbered options, reconstructs options that scrolled off-screen, and queues them via a priority-based OutputQueue
   - Permission prompts are classified by context (bash directory access, sudo, file operations, write/edit, task subagents) with 2-option vs 3-option handling
   - The notification hook enhances raw permission messages with exact tool details parsed from the transcript (command text, file paths, parameters)

4. **Bidirectional IPC Architecture**
   - Claude Code outputs flow through hooks to Slack threads (via Slack SDK WebClient)
   - Slack responses flow back through the Slack listener (Socket Mode WebSocket), which queries the registry to route threaded replies to the correct session's Unix socket
   - The PTY wrapper injects Slack responses directly into Claude's stdin with newline sanitization and Enter key simulation
   - Three transport modes with graceful degradation: registry-routed socket (Phase 3), legacy hard-coded socket (Phase 2), file-based with manual /check command (Phase 1)

5. **Self-Healing Systems**
   - Registry health checks detect hung processes, stale sockets, and dead connections -- automatically kills, cleans up, and restarts
   - Hooks self-heal missing Slack metadata by looking up the wrapper session (8-char ID) when Claude's UUID session (36-char) is missing thread data
   - Transcript parsing retries with exponential backoff (handles flush lag between Claude writing and hook reading)
   - Output buffer retry loops for permission prompt capture (10 attempts x 200ms)

6. **Developer Tooling Sensibility**
   - The launcher (`bin/claude-slack`) handles everything: ensures listener health, starts registry if needed, deploys hooks with version checking, configures `.gitignore`, sets up environment, launches the PTY wrapper
   - VibeTunnel detection and automatic mode switching (PTY mode vs no-PTY mode) for remote terminal compatibility
   - Comprehensive logging with rotation (10MB max, 5 files), debug log files per hook, and timestamped stderr output

#### AI Trust Workstream

1. **Human-in-the-Loop as Core Architecture**
   - This is not a checkbox feature -- the entire system exists to keep a human in the loop of an autonomous AI agent. Every permission request, every design decision, every "should I proceed?" gets routed to the human's phone within seconds.
   - Permission prompts include the exact tool being used, the command/file/parameters, and numbered options matching what Claude displays -- the human has full context to make an informed decision.

2. **Guardrails and Safety Patterns**
   - Hooks ALWAYS exit with code 0 -- they never block Claude Code regardless of failures (try/finally with sys.exit(0) in every hook)
   - Token redaction in all logs (SLACK_BOT_TOKEN, SLACK_APP_TOKEN never appear in debug output)
   - Process isolation: each session runs in its own process with its own socket, no cross-session data leakage
   - Dangerous command detection patterns (rm -rf, sudo, chmod 777, curl|sh) with appropriate option routing

3. **Reliability Engineering**
   - WAL mode SQLite with 10-second busy timeout and NORMAL synchronous mode for concurrent access
   - Atomic file writes using temp file + os.replace() for the output queue
   - Socket timeouts, connection limits, and 1MB request size limits on the registry server
   - Graceful degradation through three transport phases
   - Monitor process that watches Socket Mode connection health and auto-restarts on failure

4. **Auditability**
   - Every hook execution is fully logged with lifecycle markers (HOOK STARTED, HOOK EXITING)
   - Transcript parsing provides full conversation history with timestamps, UUIDs, model info, and token usage
   - Session registry maintains creation time, last activity, and state transition history
   - Debug logs capture the complete flow: environment loading, registry queries, Slack API calls, response posting

### What This Project Demonstrates About the Builder

- **Systems thinking over feature thinking**: This is not "send a Slack message." It is a session registry, lifecycle state machine, event queue, hook deployment system, PTY wrapper, and WebSocket listener -- all designed to work together as a self-healing, auto-recovering system.
- **Understanding of AI agent patterns**: Permission detection, transcript parsing, tool call interception, and response injection show deep understanding of how AI agents work internally -- not just their APIs.
- **Production engineering instincts**: WAL mode, atomic writes, exponential backoff, health checks, log rotation, socket timeouts, graceful degradation -- these are the concerns of someone who has shipped production systems.
- **Solo builder velocity**: This entire system was built by one person, iteratively, with the AI agent it was built to support. The architecture evolved through real usage (Phase 1 file-based, Phase 2 single socket, Phase 2.5 multi-session, Phase 3 registry-routed).

---

## Part 2: Case Study Draft

### Claude-Slack: Mobile Control Layer for an Autonomous AI Coding Agent

#### The Problem

AI coding agents like Claude Code are transforming how software gets built. But they have a fundamental UX gap: they run in a terminal, and they frequently need human decisions -- permission to run commands, choices between approaches, confirmation before destructive actions. If you step away from your laptop, the agent stalls. Walk the dog, commute to work, make coffee -- your AI coding session is frozen waiting for a "yes."

This is the human-in-the-loop problem applied to developer tooling. The agent is capable of autonomous work, but the approval surface is locked to a single physical device.

#### The Solution

claude-slack is a bidirectional bridge between Claude Code sessions and Slack. It turns any phone into a remote control for an AI coding agent.

**What the user experiences:**
- Start a Claude Code session on your laptop. A Slack thread appears automatically.
- Walk away. Claude keeps working. When it needs input, your phone buzzes.
- You see the exact permission request: "Claude wants to run `git push origin main`" with options "1. Yes / 2. Yes, allow git commands / 3. No."
- Tap "1" in Slack. Claude continues. Sub-second latency.
- When Claude finishes a task, the full response appears in the Slack thread.
- Run multiple sessions across different projects -- each gets its own thread.

**What happens under the hood:**

```
Terminal (PTY Wrapper)                    Slack
    |                                       |
    |-- Claude Code runs in PTY            |
    |-- Hooks fire on events:              |
    |   on_stop -> parse transcript ------->|-- Post response to thread
    |   on_notification -> detect perms --->|-- Post permission prompt
    |   on_pretooluse -> capture questions->|-- Post formatted question
    |                                       |
    |                     Listener (WSS) <--|-- User replies in thread
    |                         |             |
    |   Registry lookup: thread -> socket   |
    |                         |             |
    |<-- Inject into PTY stdin              |
    |                                       |
    |-- Claude reads input, continues       |
```

The session registry is the routing brain. It maps each Slack thread to the correct Claude session's Unix socket. Multiple sessions run concurrently, each isolated, each with its own thread. The registry uses SQLite with WAL mode for lock-free concurrent reads -- hooks, the listener, and the wrapper all access it simultaneously without blocking each other.

#### Technical Decisions That Mattered

**Unix sockets over HTTP.** The response path needs to be fast (user tapped a button on their phone, they expect instant response) and local (no network hops). Unix domain sockets give sub-millisecond IPC with zero serialization overhead. Each session gets its own socket file -- no multiplexing complexity.

**PTY wrapping over stdin proxy.** Claude Code uses terminal features (alternate screen buffer, ANSI formatting, raw mode input). A simple stdin/stdout proxy breaks these. The PTY wrapper (`pty.fork()`) gives Claude a real terminal while letting us intercept both directions. The wrapper even handles SIGWINCH (window resize) forwarding and VibeTunnel compatibility detection.

**Hooks over polling.** Claude Code's hook system fires Python scripts on specific events. Rather than polling for changes, claude-slack registers hooks that fire exactly when needed. The hooks discover their installation directory dynamically, load environment from .env, query the registry, parse the transcript, and post to Slack -- all within the hook's execution window. Every hook exits 0 regardless of success or failure to never block the agent.

**Self-healing over manual intervention.** The first version required manual setup. The current version auto-deploys hooks (with version checking), auto-starts the registry (with health checks), auto-creates Slack threads, and auto-heals missing metadata. The launcher script (`bin/claude-slack`) replaces a 15-step manual setup with a single command.

#### What I Would Build at n8n

This project demonstrates the exact thinking needed for n8n's AI product challenges:

- **Agent orchestration**: claude-slack manages autonomous agent sessions with lifecycle states, event routing, and human checkpoints. n8n's Super Agent needs the same patterns -- managing tool execution, routing between skills, maintaining context across steps.

- **Human-in-the-loop at the right granularity**: Not every action needs approval. claude-slack only interrupts for permissions and explicit questions -- everything else flows automatically. This is the balance n8n's AI Trust work needs: guardrails that protect without creating friction.

- **Developer-facing product sense**: This tool was built for developers, by a developer using the tool it extends. The UX decisions (thread-per-session, numbered options matching the terminal, sub-second injection) come from daily usage, not spec documents. n8n's builder track needs this same "eat your own dog food" approach.

- **Event-driven architecture at every level**: Hooks, WebSocket listeners, Unix socket IPC, priority queues, state machines -- this is the vocabulary of workflow automation systems. n8n's execution engine speaks this language.

#### Stack

- **Python 3** -- hooks, registry, wrapper, listener, all core modules
- **Slack SDK** -- WebClient for posting, Socket Mode for real-time message receipt
- **SQLAlchemy + SQLite (WAL)** -- session registry with concurrent access
- **Unix domain sockets** -- session-specific IPC for response injection
- **PTY (pseudo-terminal)** -- full terminal wrapping with raw mode I/O
- **Claude Code Hooks API** -- Stop, Notification, PreToolUse event integration

Open source under MIT license. Built solo as a daily-driver tool for AI-assisted development.
