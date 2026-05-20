> Full Claude Code power from your phone, delivered through Slack.

## The Problem

Claude Code is incredibly powerful, but it's chained to your terminal. If you step away from your desk -- grabbing coffee, sitting on the couch, picking up the kids -- you lose access to your AI development environment entirely. For someone who builds with Claude Code daily, that's a lot of dead time where work could be moving forward.

## My Role

I designed and built the full system: the wrapper, the Slack integration, and the interaction model.

## The Approach

I built a wrapper around Claude Code that bridges it to Slack. When you run `claude-slack`, it creates a new thread in a dedicated Slack channel and routes all of Claude's output there -- messages, permission requests, multi-choice prompts, everything. Your responses in Slack flow back through the wrapper and into Claude Code as if you were typing in the terminal. The key insight was that Slack already solves most of the hard UX problems: notifications, speech-to-text, mobile-friendly input, and threaded conversations. I just needed to connect the pipes.

## What I Built

- **Slack thread orchestration** -- each `claude-slack` session spawns a dedicated thread, keeping conversations organized
- **Emoji-based quick responses** -- numbered choices from Claude get corresponding emoji reactions; tap to respond without typing
- **Speech-to-text input** -- use Slack's built-in voice messages to talk to Claude naturally from your phone
- **Push notifications** -- get a Slack ping when Claude finishes thinking, so you don't have to watch and wait
- **Full local environment** -- Claude still runs on your machine with all your skills, configs, and project context intact
- **Bidirectional message passing** -- Claude's full output streams to Slack; your Slack replies stream back to Claude

## The Result

I use this daily. It turns downtime into productive time -- I can review Claude's work, approve permission requests, and steer development from anywhere with a phone signal. The emoji reaction pattern for quick choices turned out to be surprisingly fluid; most interactions are a single tap. It also means I get notified the moment Claude needs input, eliminating the "stare at terminal waiting" problem entirely.

## Tech Stack

- Claude Code (Anthropic CLI)
- Slack API (Bot, threads, reactions, real-time messaging)
- Node.js wrapper
- Local development environment passthrough