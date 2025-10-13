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

## 🚀 Try It Yourself!

### Option 1: Fork and Run

1. **Fork this repository**
2. **Enable Actions**: Go to Actions tab → Enable workflows
3. **Trigger workflow**: Actions → "Test with Intentional Failures" → Run workflow
4. **Check Issues tab** for automatically created issue!

### Option 2: Use as Template

Copy `playwright.config.js` and workflows to your repository.

---

## 📖 What You'll See

When the action runs, it creates a comprehensive GitHub issue:

### Issue Contents
- ✅ Test run summary (total/passed/failed/skipped)
- ✅ Failure details with error messages and stack traces
- ✅ File locations and line numbers
- ✅ Debug information (commit, workflow, Playwright version)
- ✅ Suggested next steps

---

## 📚 Learn More

- **[Action Repository](https://github.com/decision-crafters/playwright-failure-analyzer)**
- **[How It Works](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/docs/HOW_IT_WORKS.md)**
- **[Configuration Guide](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/docs/CONFIGURATION.md)**
- **[Troubleshooting](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/docs/TROUBLESHOOTING.md)**

---

## 🛠️ Repository Structure

```
playwright-failure-analyzer-demo/
├── .github/workflows/
│   ├── test-intentional-failures.yml
│   └── test-all-passing.yml
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

---

## 📄 License

MIT License - See [LICENSE](https://github.com/decision-crafters/playwright-failure-analyzer/blob/main/LICENSE)

---

<div align="center">

**Made with ❤️ by the Decision Crafters team**

[⭐ Star the Action](https://github.com/decision-crafters/playwright-failure-analyzer) |
[📖 Docs](https://github.com/decision-crafters/playwright-failure-analyzer#readme)

</div>