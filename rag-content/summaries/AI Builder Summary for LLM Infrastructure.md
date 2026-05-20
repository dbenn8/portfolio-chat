# AI Builder Summary: LLM Infrastructure

## Part 1: Job Fit

### What This Project Demonstrates

This workspace is a production-grade local LLM infrastructure running on a MacBook Pro M2 Max (64GB). It serves ~20 models across two runtimes (llama.cpp via msty.studio and MLX), exposed over Tailscale for mobile/remote access. The infrastructure supports multiple AI agent frameworks (Claude Code, Goose, Marvin) and includes custom tooling for model serving, stream compatibility, and operational reliability.

This is not a toy setup. It is a working system that handles the same problems n8n's AI product team faces daily: model serving, latency management, cost optimization, and making agentic workflows reliable.

### AI Building / Super Agent Workstream

**Custom proxy for agentic compatibility (mlx_v1_proxy.py)**
The MLX v1 Proxy is a FastAPI reverse proxy that sits between local MLX model servers and OpenAI-compatible agent clients. It solves three real problems:

1. **Path rewriting**: MLX VLM server exposes `/chat/completions`; most agent frameworks expect `/v1/chat/completions`. The proxy rewrites paths transparently.
2. **Model aliasing**: Agent configs use friendly names like `Qwen3.5-27B-5bit`; the upstream server needs full snapshot paths. The proxy maintains an alias map and rewrites request bodies in-flight.
3. **SSE stream coalescing**: MLX emits one-token-at-a-time SSE events. Agents like Goose render these as jittery single-word output. The proxy buffers tokens and flushes on paragraph boundaries, character thresholds (1250 chars), or latency limits (15s) -- whichever comes first. This is the kind of UX-aware infrastructure work that separates working agent systems from demos.

**GPU proxy for safe model loading (lms-proxy/proxy.py)**
A second proxy intercepts OpenAI-compatible API requests to LM Studio, pre-loads GGUF models with `--gpu max` via CLI, then forwards to the model server. This works around a real LM Studio bug (#1463) where JIT model loading ignores GPU config and can lock up a 64GB machine by loading a 25GB model entirely on CPU with 30% REPACK overhead. The proxy has 17 tests and a config lookup chain (registry JSON -> per-model configs -> safe defaults).

**Multi-framework agent support**
The infrastructure serves Claude Code, Goose Desktop, and Marvin (a custom agent with Blitzit task management integration). The Goose recipe (`marvin-recipe.yaml`) configures a local Qwen3.5-27B-5bit model as the provider, demonstrating practical local-model agent orchestration with tool use.

**Claude Code skills as operational automation**
Three custom skills encode operational knowledge as executable procedures:
- `/configure_model` -- analyzes a GGUF file, detects architecture type (MoE, dense, vision, embedding), calculates memory budget against the 64GB hardware profile, and generates ready-to-paste config YAML
- `/setup-llm-model` -- inspects HuggingFace models without downloading weights, detects vision/tool-calling/RoPE scaling, outputs LM Studio commands and Tailscale access instructions, manages a model registry
- `/troubleshoot-lms` -- symptom-based diagnostic runbook covering GPU offload failures, JIT bugs, machine lockups, architecture limitations, and remote access issues

These skills are the kind of "custom memory" the job description calls for: domain knowledge encoded as repeatable, agent-executable procedures rather than one-off prompts.

### AI Trust Workstream

**Reliability engineering**
- The MSty config system overwrites `config.yaml` on every service restart. The workspace documents exactly which settings persist (context size via UI, mmproj via directory convention) and which don't (`--embedding` flag). This is the kind of "gotcha" documentation that prevents hours of debugging.
- The troubleshoot-lms skill is structured as a symptom-to-fix lookup table -- the same pattern used in production SRE runbooks.
- Only one large model can run at a time on 64GB. The workspace enforces this with explicit GPU conflict checks and JIT auto-evict documentation.

**Cost optimization through quantization literacy**
The model library spans Q4_K_M through Q8_0 quantizations, 5-bit MLX, and F16 (for projectors only). The model_config_tips document contains precise memory budgets:
- MoE 30B (Mamba hybrid): 128-256K context safe, KV cache ~0.8GB at 128K due to only 6 attention layers
- Dense 14B: 32K context, ~11GB model weight
- Vision 8B + projector: 8K context, ~5GB total

This is not theoretical knowledge. The config tips include KV cache formulas (`2 x layers x kv_heads x head_dim x ctx x bytes`) and real measurements from this hardware.

**Latency management**
- The SSE coalescing in mlx_v1_proxy.py directly addresses perceived latency. Raw token-by-token streaming is technically lower latency but creates worse UX in agent interfaces. The proxy trades 15s max buffering for coherent paragraph-level output.
- The Tailscale serve config exposes four endpoints (standalone llama.cpp, msty llama-swap, tools, remote) for zero-config remote access from any device on the tailnet. WireGuard handles auth.

**Debugging infrastructure**
- The MLX Server Runbook includes an end-to-end connectivity checklist: core server health -> proxy health -> model list -> test chat with alias. Each step has a curl command and expected output.
- Log locations are documented for both the MLX server and proxy, with `tail -f` commands ready to paste.
- The troubleshoot-lms skill covers 12 distinct failure modes with diagnostic commands and fixes.

### Why This Matters for n8n

n8n's AI Product Builder role requires "harness literacy" -- understanding how LLM infrastructure actually works, not just how to call APIs. This workspace demonstrates:

1. **Model serving is not just an API call.** Path rewriting, model aliasing, stream format differences, and GPU memory management are all real problems when you run models yourself.
2. **Agent reliability requires infrastructure.** The GPU proxy exists because a platform bug can lock up a machine. The SSE coalescer exists because raw token streaming breaks agent UX. These are the kinds of reliability problems that show up when you ship AI products to real users.
3. **Operational knowledge compounds.** The skills, runbooks, and config tips represent months of debugging crystallized into reusable procedures. This is exactly the pattern n8n needs for making AI workflows reliable at scale.
4. **Local models teach you what cloud APIs hide.** Running your own inference means understanding quantization tradeoffs, KV cache sizing, context window limits, and memory pressure -- all of which inform better decisions when building on top of any model provider.

---

## Part 2: Case Study Draft

### Building Reliable Local LLM Infrastructure for Multi-Agent Workflows

**Problem**
I needed to run multiple AI agents (Claude Code, Goose, a custom Marvin agent) against local models on a single MacBook Pro M2 Max with 64GB unified memory. Each agent framework expected a slightly different API surface. Models ranged from 5GB embedding models to 31GB MoE architectures. Failures were catastrophic -- a misconfigured GPU offload could lock up the entire machine for 5+ minutes.

**Architecture**

```
Agent Frameworks            Proxies                  Model Servers
-----------------          ---------                 --------------
Claude Code      ------>   (direct)    ---------->   msty.studio llama-swap
Goose Desktop    ------>   mlx_v1_proxy (7778) --->  MLX VLM server (7777)
Marvin/Blitzit   ------>   GPU proxy (1235) ------->  LM Studio (1234)
Mobile (msty)    ------>   Tailscale serve -------->  All of the above
```

Three model runtimes serve different needs:
- **msty.studio llama-swap**: GGUF models with automatic model swapping, persistent config via UI
- **MLX VLM server**: Apple Silicon-native inference for MLX-quantized models (Qwen3.5-27B-5bit)
- **LM Studio**: Broad model support with GUI, but with GPU offload bugs requiring a proxy workaround

**Key Technical Decisions**

*SSE stream coalescing* -- MLX emits tokens one at a time. Agent frameworks that render streaming output showed jittery, word-by-word text. I built a coalescing layer in the proxy that buffers tokens and flushes on three conditions: paragraph boundary detected, 1250 character threshold reached, or 15 seconds elapsed. This preserves streaming responsiveness while delivering coherent text blocks to the agent UI.

*GPU proxy for safe model loading* -- LM Studio's JIT loading ignores per-model GPU configuration (bug #1463). On Apple Silicon, this means a 25GB GGUF model can load entirely on CPU with ~30% REPACK overhead, consuming 33GB+ and locking up the machine. The GPU proxy intercepts API requests, pre-loads models with explicit `--gpu max` via CLI, then forwards the request. It consults a model registry for optimal context sizes and falls back to safe defaults.

*Operational knowledge as executable skills* -- Instead of maintaining wiki pages about model configuration, I encoded the knowledge as Claude Code skills. `/configure_model` takes a GGUF filename and outputs recommended settings. `/setup-llm-model` inspects HuggingFace metadata without downloading weights. `/troubleshoot-lms` provides symptom-based diagnosis. These skills are used by the AI agent itself -- the agent that helps me manage models can read and apply the same operational procedures I would follow manually.

*Memory-aware model management* -- With 64GB total and ~39-44GB available for models, every model load is a resource allocation decision. The workspace maintains a quick-reference table mapping model type and size to safe context windows, with KV cache formulas for precise estimation. The system enforces single-model-at-a-time for large models and documents the JIT auto-evict trap (manually loaded models don't get evicted, so JIT-loading a second large model causes OOM).

**Results**
- Three agent frameworks running against local models with zero cloud API cost for inference
- Mobile access to any local model via Tailscale with zero additional auth configuration
- Zero machine lockups since implementing the GPU proxy (previously ~2-3 per week during model experimentation)
- Model configuration time reduced from ~30 minutes of trial and error to ~2 minutes using the configure_model skill
- Operational runbooks that are both human-readable and agent-executable

**What I Would Do Differently**
- Start with the GPU proxy from day one rather than discovering the JIT bug through repeated lockups
- Build a unified model registry earlier -- having config scattered across msty's internal database, LM Studio's per-model configs, and the llama-swap YAML created confusion
- Add health check monitoring that alerts when a model server goes down rather than discovering it when an agent request fails

**Relevance to n8n**
This project is a microcosm of the problems n8n faces with AI workflow reliability. Model serving compatibility, stream format differences, GPU resource management, and operational debugging are all challenges that scale up, not go away, when you move from a single laptop to a platform serving thousands of workflows. The skills-as-operational-knowledge pattern maps directly to how n8n could encode best practices for AI node configuration, model selection, and failure recovery into the product itself.
