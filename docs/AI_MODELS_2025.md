# AI Models for Auto-Fix (2025)

This document describes the latest AI models available for automatic test fixing in the Playwright Failure Analyzer demo.

## Available Models

### 🏆 Claude Sonnet 4.5 (Default)

**Model ID:** `claude-sonnet-4.5-20250929`
**Provider:** Anthropic
**Released:** September 2025
**Cost:** $$ (Medium)

**Best For:**
- Balanced performance and cost
- General code fixing tasks
- Current default for Claude.ai

**Strengths:**
- Excellent coding capabilities
- Strong reasoning with hybrid architecture
- Good at understanding test failures

---

### 🥇 Claude Opus 4

**Model ID:** `claude-opus-4-20250522`
**Provider:** Anthropic
**Released:** May 2025
**Cost:** $$$ (High)

**Best For:**
- Maximum quality and success rate
- Complex refactoring tasks
- Mission-critical fixes

**Strengths:**
- **72.5% SWE-bench** (best coding model in the world)
- **43.2% Terminal-bench**
- Best at understanding complex codebases
- Highest confidence scores

---

### 🚀 GPT-5-Codex

**Model ID:** `gpt-5-codex`
**Provider:** OpenAI
**Released:** September 2025
**Cost:** $$$$ (Very High)

**Best For:**
- Complex multi-file refactoring
- Autonomous coding tasks (can work 7+ hours)
- Systematic codebase modifications

**Strengths:**
- **51.3% accuracy** on code refactoring (vs 33.9% for GPT-5)
- Adaptive reasoning - adjusts thinking time dynamically
- Excellent for navigating repositories
- Superior code review capabilities

**Note:** GPT-5-Codex is optimized for agentic coding and can operate autonomously for extended periods.

---

### 🧠 o3-mini

**Model ID:** `o3-mini`
**Provider:** OpenAI
**Released:** January 2025
**Cost:** $ (Low-Medium)

**Best For:**
- Cost-effective reasoning
- Structured problem-solving
- Quick fixes with good quality

**Strengths:**
- **20% fewer errors** than o1
- Free daily usage tier available
- Good balance of cost and quality
- Enhanced reasoning abilities

---

### ⚡ Codex Mini Latest

**Model ID:** `codex-mini-latest`
**Provider:** OpenAI
**Released:** 2025
**Cost:** $ (Low)

**Best For:**
- Code-specific tasks
- Fast iteration
- High-volume fixing

**Strengths:**
- Specialized for code
- Fast inference
- Free daily usage tier (up to 10M tokens/day)
- Uses different endpoint (v1/responses)

---

### 💰 DeepSeek R1

**Model ID:** `deepseek-r1`
**Provider:** DeepSeek
**Released:** January 2025
**Cost:** $ (Very Low - 50-85% cheaper than o1)

**Best For:**
- Budget-conscious operations
- High-volume benchmarking
- Algorithmic/structured problems

**Strengths:**
- **96% Codeforces** success rate
- Open-weight model (MIT license)
- Trained with reinforcement learning
- Excellent at competitive programming
- Developed for under $6M (vs $100M for GPT-4)

**Note:** Best value proposition - reasoning comparable to GPT-4 at tiny fraction of cost.

---

### 📦 Legacy Models (Still Supported)

#### gpt-4o-mini
- Cost-effective OpenAI option
- Good for testing and development

#### gpt-4o
- Previous generation flagship
- Reliable but surpassed by newer models

#### claude-3-5-sonnet-20240620
- Previous Claude generation
- Stable and well-tested

#### deepseek/deepseek-chat
- Earlier DeepSeek model
- Good baseline for comparison

#### deepseek/deepseek-coder
- Code-specialized earlier version

---

## Recommendations by Use Case

### Maximum Success Rate
**Use:** `claude-opus-4-20250522`

Leading SWE-bench at 72.5%, this is the most capable coding model available.

### Best Value
**Use:** `deepseek-r1`

Exceptional performance at 50-85% lower cost than alternatives. Open-source with MIT license.

### Balanced (Recommended)
**Use:** `claude-sonnet-4.5-20250929` (Default)

Excellent performance-to-cost ratio, currently the default model for this workflow.

### Complex Refactoring
**Use:** `gpt-5-codex`

Autonomous operation for up to 7 hours, best at systematic multi-file modifications.

### Budget-Conscious Testing
**Use:** `o3-mini` or `codex-mini-latest`

Free daily tiers available, good quality for experimentation.

---

## Cost Estimates (Per Fix Attempt)

| Model | Estimated Cost | Notes |
|-------|---------------|-------|
| DeepSeek R1 | $0.001-0.003 | Best value |
| Codex Mini | $0.002-0.005 | Free tier available |
| o3-mini | $0.010-0.030 | Free tier available |
| Claude Sonnet 4.5 | $0.005-0.015 | Recommended default |
| GPT-4o-mini | $0.005-0.010 | Legacy fallback |
| Claude Opus 4 | $0.015-0.050 | Premium quality |
| GPT-5-Codex | $0.050-0.150 | Premium agentic coding |

**Note:** Costs are approximate and vary based on prompt length, response length, and specific API pricing at time of use.

---

## Model Selection in Workflows

### Auto-Fix Workflow

Default: `claude-sonnet-4.5-20250929`

To use a different model, select from the dropdown when manually triggering the workflow.

### Benchmark Workflow

Automatically tests all models in the matrix:
- claude-sonnet-4.5-20250929
- claude-opus-4-20250522
- gpt-5-codex
- o3-mini
- codex-mini-latest
- deepseek-r1
- gpt-4o-mini

Results are posted to the benchmark tracking issue for comparison.

---

## API Keys Required

Set these as repository secrets:

- `ANTHROPIC_API_KEY` - For Claude models
- `OPENAI_API_KEY` - For OpenAI models (GPT, o3, Codex)
- `DEEPSEEK_API_KEY` - For DeepSeek models (optional, can also use OpenRouter)

**Note:** The Dagger module uses LiteLLM, which automatically routes to the correct provider based on model ID.

---

## Performance Expectations

### Easy Difficulty Tests (90-95% confidence target)

| Model | Expected Success Rate |
|-------|----------------------|
| Claude Opus 4 | 90-95% |
| Claude Sonnet 4.5 | 85-90% |
| GPT-5-Codex | 85-90% |
| o3-mini | 80-85% |
| DeepSeek R1 | 80-85% |
| Codex Mini | 75-80% |
| GPT-4o-mini | 70-75% |

### Medium Difficulty Tests (70-85% confidence target)

| Model | Expected Success Rate |
|-------|----------------------|
| Claude Opus 4 | 80-85% |
| GPT-5-Codex | 75-80% |
| Claude Sonnet 4.5 | 70-75% |
| o3-mini | 65-70% |
| DeepSeek R1 | 65-70% |

### Hard Difficulty Tests (50-70% confidence target)

| Model | Expected Success Rate |
|-------|----------------------|
| Claude Opus 4 | 65-70% |
| GPT-5-Codex | 60-65% |
| Claude Sonnet 4.5 | 55-60% |
| o3-mini | 50-55% |

---

## Recent Benchmark Results

See the [benchmark tracking issue](https://github.com/decision-crafters/playwright-failure-analyzer-demo/labels/benchmark) for latest results comparing all models.

**Last Updated:** October 2025
