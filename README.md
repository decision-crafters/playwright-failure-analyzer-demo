# Playwright Failure Analyzer - Demo Repository

[![Test with Intentional Failures](../../actions/workflows/test-intentional-failures.yml/badge.svg)](../../actions/workflows/test-intentional-failures.yml)

> Live demonstration of the [Playwright Failure Analyzer](https://github.com/decision-crafters/playwright-failure-analyzer) GitHub Action

---

## 🎯 Purpose

1. **📺 Live Demo**: See the action working with real test failures
2. **📋 Template**: Fork this repo to quickly set up the action
3. **🧪 Validation**: Automated testing environment for the action

---

## 🧪 Test Workflows

### 🔴 [Test with Intentional Failures](../../actions/workflows/test-intentional-failures.yml)

Runs tests that **intentionally fail** to demonstrate the action.

**What it does:**
- Runs 5 tests designed to fail (timeout, assertion, navigation errors)
- Action automatically creates a detailed GitHub issue
- Runs every 12 hours to keep demo active

**View Demo Issues**: [Issues with `demo` label →](../../issues?q=label%3Ademo)

### ✅ [Test All Passing](../../actions/workflows/test-all-passing.yml)

Runs tests that **all pass** to show no issues are created when tests succeed.

---

## 🎯 Demo Workflows

This repository demonstrates the Playwright Failure Analyzer with **two workflow configurations**:

### 1. Basic Failure Analysis (No AI)
**File:** `.github/workflows/test-intentional-failures.yml`

Demonstrates core functionality without requiring AI configuration:
- Automatic GitHub issue creation
- Structured failure reports
- Error messages and stack traces
- File paths and line numbers

**✅ No API key required**
**✅ Free to run**
**✅ Quick setup**

[View Example Issue](#) <!-- Link to an example issue -->

---

### 2. AI-Powered Analysis with DeepSeek
**File:** `.github/workflows/test-with-ai-analysis.yml`

Demonstrates enhanced analysis with AI insights:
- Everything from basic workflow
- **🤖 Root cause analysis**
- **🤖 Suggested fixes**
- **🤖 Priority recommendations**
- **🤖 Pattern detection**

**Requires:**
- DeepSeek API key (via OpenRouter)
- Repository secret: `DEEPSEEK_API_KEY`

**Cost:** ~$0.0003 per analysis (less than a penny)

[Setup Instructions](.github/AI_SETUP.md) | [View AI Example Issue](#) <!-- Link to AI-enhanced example -->

---

## 🚀 Try It Yourself!

### Option 1: Fork and Run

1. **Fork this repository**
2. **Enable Actions**: Go to Actions tab → Enable workflows
3. **Trigger workflow**: Actions → "Test with Intentional Failures" → Run workflow
4. **Check Issues tab** for automatically created issue!

### Option 2: Use as Template

Copy `playwright.config.js` and workflows to your repository.

---

## 🚀 Quick Start

### Try Basic Analysis (No Setup)
1. Fork this repository
2. Push a commit or create a PR
3. Check the Issues tab for automatically created failure reports

### Try AI Analysis (5-Minute Setup)
1. Get an API key from [OpenRouter](https://openrouter.ai) ($5 minimum)
2. Add secret `DEEPSEEK_API_KEY` in repository settings
3. Manually trigger the "Test with AI Analysis" workflow
4. Compare the AI-enhanced issue with the basic one

---

## 📊 Comparison

| Feature | Basic Workflow | AI Workflow |
|---------|---------------|-------------|
| Test failure detection | ✅ | ✅ |
| Error messages & stack traces | ✅ | ✅ |
| File paths & line numbers | ✅ | ✅ |
| Retry information | ✅ | ✅ |
| Root cause analysis | ❌ | ✅ |
| Suggested fixes | ❌ | ✅ |
| Priority recommendations | ❌ | ✅ |
| Pattern detection | ❌ | ✅ |
| **Setup required** | None | API key |
| **Cost per run** | Free | ~$0.0003 |
| **Execution time** | ~30s | ~40s |

---

## 🛠️ Using in Your Project

Choose the workflow that fits your needs:

### For Quick Setup (Basic)
```yaml
- name: Analyze failures
  if: steps.tests.outputs.test-failed == 'true'
  uses: decision-crafters/playwright-failure-analyzer@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

### For Enhanced Insights (AI)
```yaml
- name: Analyze failures with AI
  if: steps.tests.outputs.test-failed == 'true'
  uses: decision-crafters/playwright-failure-analyzer@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    ai-analysis: true
  env:
    OPENROUTER_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    AI_MODEL: 'openrouter/deepseek/deepseek-chat'
```

Full examples available in the [main repository](https://github.com/decision-crafters/playwright-failure-analyzer/tree/main/examples).

---

## 📖 Documentation

- [Full Setup Guide](.github/AI_SETUP.md)
- [Main Repository](https://github.com/decision-crafters/playwright-failure-analyzer)
- [Configuration Options](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/docs/CONFIGURATION.md)
- [Troubleshooting](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/docs/TROUBLESHOOTING.md)

---

## 💡 Why Two Workflows?

**Flexibility:** Users can see both options and choose what works for them

**Learning:** Compare basic vs AI-enhanced reports side by side

**Cost Control:** Not everyone wants or needs AI analysis

**Demonstration:** Shows the full capabilities without forcing AI adoption

---

## 📖 What You'll See

When the action runs, it creates a comprehensive GitHub issue:

### Issue Contents
- ✅ Test run summary (total/passed/failed/skipped)
- ✅ Failure details with error messages and stack traces
- ✅ File locations and line numbers
- ✅ Debug information (commit, workflow, Playwright version)
- ✅ Suggested next steps
- 🤖 **AI Analysis (when enabled):** Root cause analysis, suggested fixes, priority recommendations

---

## 🛠️ Repository Structure

```
playwright-failure-analyzer-demo/
├── .github/
│   ├── workflows/
│   │   ├── test-intentional-failures.yml
│   │   ├── test-all-passing.yml
│   │   └── test-with-ai-analysis.yml
│   └── AI_SETUP.md
├── tests/
│   ├── sample-fail.spec.js
│   └── sample-pass.spec.js
├── playwright.config.js
├── package.json
└── README.md
```

---

## ❓ FAQ

**Q: Why do these tests fail?**
A: Tests in `sample-fail.spec.js` are intentionally designed to fail to demonstrate the action.

**Q: How often do workflows run?**
A: Intentional failures every 12 hours, passing tests weekly on Mondays.

**Q: Can I customize this?**
A: Yes! Fork and modify test files, schedules, labels, and titles.

**Q: What's the difference between the workflows?**
A: Basic workflow provides structured failure reports. AI workflow adds intelligent analysis, root cause detection, and fix suggestions using DeepSeek.

---

## 📄 License

MIT License - See [LICENSE](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/LICENSE)

---

<div align="center">

**Made with ❤️ by the Decision Crafters team**

[⭐ Star the Action](https://github.com/decision-crafters/playwright-failure-analyzer) |
[📖 Docs](https://github.com/decision-crafters/playwright-failure-analyzer#readme)

</div>