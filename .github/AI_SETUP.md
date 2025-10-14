# Setting Up AI Analysis in the Demo Repository

This guide explains how to add AI-powered failure analysis to the `playwright-failure-analyzer-demo` repository using DeepSeek.

## Overview

The demo repository now has **two workflows**:

1. **`test-intentional-failures.yml`** - Basic failure analysis (no AI required)
2. **`test-with-ai-analysis.yml`** - AI-powered failure analysis with DeepSeek (NEW)

This dual setup allows users to:
- See the analyzer working without AI configuration
- Compare basic vs AI-enhanced failure reports
- Choose their preferred approach

---

## Setup Instructions

### Step 1: Copy the AI Workflow File

Copy the file from this repository to the demo repo:

```bash
# From: playwright-failure-analyzer/.github/DEMO_REPO_AI_WORKFLOW.yml
# To: playwright-failure-analyzer-demo/.github/workflows/test-with-ai-analysis.yml
```

### Step 2: Get a DeepSeek API Key

**Option A: OpenRouter (Recommended - Easiest)**
1. Sign up at https://openrouter.ai
2. Add credits (starting at $5)
3. Create an API key
4. Cost: ~$0.0003 per analysis

**Option B: Direct DeepSeek API**
1. Sign up at https://platform.deepseek.com
2. Add credits
3. Create an API key
4. Slightly more complex setup

### Step 3: Add Secret to GitHub Repository

1. Go to: https://github.com/decision-crafters/playwright-failure-analyzer-demo/settings/secrets/actions
2. Click **"New repository secret"**
3. Add secret:
   - **Name**: `DEEPSEEK_API_KEY`
   - **Value**: Your API key (starts with `sk-or-v1-...` for OpenRouter)
4. Click **"Add secret"**

### Step 4: Test the Workflow

Trigger the workflow:
```bash
# Push a commit to main
git commit --allow-empty -m "Test AI workflow"
git push origin main

# OR manually trigger via GitHub Actions UI
# Go to: Actions → "Test with AI Analysis (DeepSeek)" → "Run workflow"
```

### Step 5: Verify AI Analysis

1. Wait for workflow to complete (~2-3 minutes)
2. Check the created issue (labeled `ai-analyzed`)
3. Look for the **"🤖 AI Analysis"** section with:
   - Root cause analysis
   - Suggested fixes
   - Priority assessment

---

## Comparing the Two Workflows

### Basic Workflow (`test-intentional-failures.yml`)

**Pros:**
- No API key required
- Free to run
- Faster execution (~30 seconds)
- Good for basic failure reporting

**What you get:**
- Test failure details
- Error messages and stack traces
- File paths and line numbers
- Retry information

**Example issue:** Standard failure report with structured data

---

### AI Workflow (`test-with-ai-analysis.yml`)

**Pros:**
- Intelligent analysis of failure patterns
- Root cause identification
- Actionable fix suggestions
- Priority recommendations

**Cons:**
- Requires API key and credits
- Slightly slower (~extra 5-10 seconds)
- Small cost per analysis (~$0.0003)

**What you get (in addition to basic):**
- **Root Cause Analysis**: Why tests are failing
- **Suggested Fixes**: Concrete steps to resolve
- **Priority Assessment**: Which failures to fix first
- **Pattern Detection**: Common issues across failures

**Example issue:** Enhanced report with AI insights section

---

## Cost Estimation

Using DeepSeek via OpenRouter:
- **Per analysis**: ~$0.0003 (less than a penny)
- **100 analyses**: ~$0.03
- **1000 analyses**: ~$0.30

This is one of the cheapest AI analysis options available.

---

## Environment Variable Options

The workflow supports multiple AI providers via LiteLLM:

### DeepSeek via OpenRouter (Recommended)
```yaml
env:
  OPENROUTER_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  AI_MODEL: 'openrouter/deepseek/deepseek-chat'
```

### Direct DeepSeek API
```yaml
env:
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  AI_MODEL: 'deepseek/deepseek-chat'
```

### OpenAI (Alternative)
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  AI_MODEL: 'gpt-4o-mini'
```

### Anthropic Claude (Premium)
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  AI_MODEL: 'claude-3-5-sonnet-20240620'
```

---

## Troubleshooting

### AI Analysis Shows "Not Configured"

**Problem:** Log shows `AI analysis failed or not configured`

**Solutions:**
1. Verify secret name is exactly `DEEPSEEK_API_KEY`
2. Check API key is valid and has credits
3. Ensure `env` section is properly configured in workflow
4. Test API key locally:
   ```bash
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY"
   ```

### API Rate Limits

**Problem:** Too many requests

**Solutions:**
- Add delays between workflow runs
- Use workflow conditions to limit triggers
- Increase API quota with provider

### Wrong AI Model

**Problem:** Model not found or invalid

**Solutions:**
- Check model name matches provider format
- For OpenRouter: prefix with `openrouter/`
- Verify model is available in your region

---

## Demo Repository Structure

```
playwright-failure-analyzer-demo/
├── .github/
│   └── workflows/
│       ├── test-intentional-failures.yml    # Basic (no AI)
│       └── test-with-ai-analysis.yml        # AI-enabled
├── tests/
│   └── sample-fail.spec.ts                  # Intentionally failing tests
├── playwright.config.ts
└── README.md
```

---

## Next Steps

After setup, you can:

1. **Compare Issues**: Look at issues created by both workflows
2. **Update README**: Document both workflow options for users
3. **Add Badge**: Show AI-enabled workflow status
4. **Cost Tracking**: Monitor API usage in your provider dashboard

---

## Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [DeepSeek Documentation](https://platform.deepseek.com/docs)
- [LiteLLM Supported Models](https://docs.litellm.ai/docs/providers)
- [Main Repository Examples](https://github.com/decision-crafters/playwright-failure-analyzer/tree/main/examples)

---

**Need Help?**

- Open an issue: https://github.com/decision-crafters/playwright-failure-analyzer/issues
- Check troubleshooting: https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/docs/TROUBLESHOOTING.md
