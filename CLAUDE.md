# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **demo repository** for the [Playwright Failure Analyzer](https://github.com/decision-crafters/playwright-failure-analyzer) GitHub Action. It demonstrates automated test failure analysis with two approaches:

1. **Basic Analysis** - Structured failure reports without AI
2. **AI-Enhanced Analysis** - Intelligent analysis using DeepSeek via direct API integration

The repository contains intentionally failing tests to showcase the action's capabilities.

## Commands

### Running Tests

```bash
# Run all tests
npm test

# Run intentionally failing tests
npm run test:fail

# Run passing tests
npm run test:pass
```

### Playwright Commands

```bash
# Install Playwright browsers
npx playwright install --with-deps chromium

# Run Playwright tests with specific options
npx playwright test                    # All tests
npx playwright test sample-fail        # Only failing tests
npx playwright test sample-pass        # Only passing tests
npx playwright test --reporter=list    # With list reporter
```

### Single Test Execution

```bash
# Run a specific test file
npx playwright test tests/sample-fail.spec.js

# Run a specific test by name (using grep)
npx playwright test -g "timeout failure"
npx playwright test -g "assertion failure"
```

### Local Development with Python 3.11

For local development and testing of the analyzer action itself:

```bash
# Create and activate Python 3.11 virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if running the action locally)
pip install -r requirements.txt  # If testing the action locally

# Run tests in the venv context
npm test
```

**Note:** The demo repository itself only requires Node.js. Python 3.11 venv is only needed if you're developing or testing the analyzer action locally or working with the Dagger module.

### Dagger Commands

The repository includes a Dagger module for **AI-powered automatic fixing** of test failures:

```bash
# Navigate to Dagger module directory
cd dagger

# Test basic Dagger module functionality
dagger call hello

# Attempt to generate fixes for failures
dagger call attempt-fix \
  --repo-dir=.. \
  --failures-json-path=playwright-report/results.json \
  --ai-model=gpt-4o-mini \
  --min-confidence=0.75

# Generate fixes AND create a PR (full auto-fix workflow)
dagger call fix-and-create-pr \
  --repo-dir=.. \
  --failures-json-path=playwright-report/results.json \
  --issue-number=123 \
  --github-token=env:GITHUB_TOKEN \
  --ai-model=gpt-4o-mini \
  --min-confidence=0.75

# Install Dagger module dependencies
cd dagger
pip install -e .

# Run Dagger module tests
pytest tests/
```

**Available AI Models:**
- `gpt-4o` or `gpt-4o-mini` (OpenAI)
- `claude-3-5-sonnet-20240620` (Anthropic)
- `deepseek/deepseek-chat` or `deepseek/deepseek-coder` (DeepSeek direct)
- `openrouter/deepseek/deepseek-chat` (DeepSeek via OpenRouter)

## Critical Configuration Requirements

### JSON Reporter is Required

The Playwright Failure Analyzer **requires** the JSON reporter to be configured in `playwright.config.js`:

```javascript
reporter: [
  ['json', { outputFile: 'playwright-report/results.json' }]
]
```

**This configuration is critical** - the action parses `playwright-report/results.json` to analyze failures. Do not remove or modify this reporter configuration.

## Repository Architecture

### Test Structure

The repository has **two test suites** serving different purposes:

1. **`tests/sample-fail.spec.js`** - Contains 5 intentionally failing tests:
   - Timeout failures (element not found)
   - Assertion failures (wrong values)
   - Navigation timeouts (invalid domains)
   - Selector errors (nonexistent elements)
   - Text content mismatches

2. **`tests/sample-pass.spec.js`** - Contains 5 passing tests that verify basic functionality

These tests are designed to demonstrate different failure scenarios that the analyzer can detect and report.

### Workflow Architecture

Three GitHub Actions workflows demonstrate different aspects of the analyzer:

#### 1. Basic Failure Analysis (`test-intentional-failures.yml`)

- Runs on: push to main, PRs, manual trigger, and every 12 hours
- Uses `decision-crafters/playwright-failure-analyzer@v1`
- **No AI configuration required**
- Creates issues labeled: `demo`, `automated`, `expected-failure`
- Demonstrates core functionality without AI costs

**Key workflow pattern:**
```yaml
- name: Run failing tests
  id: tests
  run: |
    set +e  # Don't exit on test failure
    npx playwright test sample-fail
    TEST_EXIT_CODE=$?
    echo "test-failed=$([ $TEST_EXIT_CODE -ne 0 ] && echo 'true' || echo 'false')" >> $GITHUB_OUTPUT
    exit $TEST_EXIT_CODE
  continue-on-error: true

- name: Analyze failures
  if: steps.tests.outputs.test-failed == 'true'
  uses: decision-crafters/playwright-failure-analyzer@v1
```

The `set +e` pattern is critical - it allows capturing the test exit code without failing the workflow, enabling conditional analysis.

#### 2. AI-Enhanced Analysis (`test-with-ai-analysis.yml`)

- Runs on: push to main, PRs, and manual trigger
- Uses `decision-crafters/playwright-failure-analyzer@v1.1.0` with `ai-analysis: true`
- **Requires `DEEPSEEK_API_KEY` secret**
- Creates issues labeled: `demo`, `automated`, `ai-analyzed`
- Provides root cause analysis, suggested fixes, and priority recommendations

**Critical environment variables:**
```yaml
env:
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  AI_MODEL: 'deepseek/deepseek-chat'
```

**Note:** This workflow uses the **direct DeepSeek API** (not OpenRouter). The action supports multiple AI providers through LiteLLM. See `.github/AI_SETUP.md` for alternative configurations.

#### 3. All Passing Tests (`test-all-passing.yml`)

- Runs on: manual trigger and weekly schedule (Mondays)
- Demonstrates that no issues are created when tests pass
- Validation workflow for the analyzer's conditional logic

#### 4. Auto-Fix Workflow (`auto-fix.yml`)

**NEW: Dagger-powered automatic fixing of test failures**

- Runs on: Issues with `auto-fix-ready` label
- Uses the Dagger module at `dagger/`
- **Requires `OPENROUTER_API_KEY` or `OPENAI_API_KEY` secret**
- Creates PRs with automated fixes
- Labels: `automated-fix`, `needs-review`

**Workflow trigger pattern:**
```yaml
on:
  issues:
    types: [opened, labeled]

jobs:
  attempt-auto-fix:
    if: contains(github.event.issue.labels.*.name, 'auto-fix-ready')
```

**How it works:**
1. Analyzer detects test failures and creates an issue with structured JSON
2. Issue is labeled with `auto-fix-ready` (manually or automatically)
3. Dagger module reads the failures JSON
4. AI generates code fixes for each failure
5. Fixes are tested in isolated Playwright containers
6. If confidence threshold is met, a PR is created automatically
7. PR links back to the original issue for context

### Permissions Required

All workflows need these permissions to create GitHub issues:

```yaml
permissions:
  issues: write
  contents: read
```

For the auto-fix workflow, additional permissions are required:

```yaml
permissions:
  contents: write      # To create branches and commits
  issues: write        # To comment on issues
  pull-requests: write # To create PRs
```

## Dagger Auto-Fix Module

### Architecture Overview

The Dagger module (`dagger/`) provides AI-powered automatic fixing of Playwright test failures. It consists of several components:

**Core Components:**

1. **`src/main.py`** - Main Dagger module entry point
   - `attempt_fix()` - Generates fixes without creating PRs
   - `fix_and_create_pr()` - Full workflow: fix generation + PR creation

2. **`src/fix_generator.py`** - AI-powered fix generation
   - Pattern-specific prompts for different error types
   - Uses LiteLLM for multi-provider AI support
   - Extracts code context around failures
   - Parses AI responses into structured fixes

3. **`src/test_runner.py`** - Test execution in isolated containers
   - Runs tests in Playwright containers (`mcr.microsoft.com/playwright`)
   - Applies fixes before testing
   - Validates that fixes actually work
   - Returns structured test results

4. **`src/confidence_scorer.py`** - Enhanced confidence calculation
   - Applies model-specific multipliers (GPT-4: 1.0, DeepSeek: 0.70-0.75)
   - Boosts confidence when tests pass (+0.15)
   - Pattern-based confidence adjustments
   - Recommends action: `CREATE_PR`, `CREATE_DRAFT_PR`, `COMMENT_ONLY`, or `SKIP`

5. **`src/pr_creator.py`** - GitHub PR automation
   - Creates branches with fixes
   - Commits changes with detailed messages
   - Creates PRs with comprehensive descriptions
   - Links PRs to original issues

**Directory Structure:**
```
dagger/
├── dagger.json                  # Dagger module configuration
├── pyproject.toml               # Python dependencies
├── src/
│   ├── main.py                  # Main entry point
│   ├── fix_generator.py         # AI fix generation
│   ├── confidence_scorer.py     # Confidence scoring
│   ├── test_runner.py           # Container-based testing
│   └── pr_creator.py            # PR creation
└── tests/
    ├── test_fix_generator.py
    ├── test_confidence.py
    └── test_integration.py
```

### Confidence Scoring System

The auto-fix module uses a sophisticated confidence scoring system:

**Model Multipliers:**
- `gpt-4o`: 1.0
- `gpt-4o-mini`: 0.85
- `claude-3.5-sonnet`: 1.0
- `deepseek-chat`: 0.70
- `deepseek-coder`: 0.75

**Confidence Boosts:**
- Test passes after fix: +0.15
- High-confidence patterns (e.g., `missing_await`): +0.10
- Simple fixes (1-5 lines): No penalty
- Complex fixes (10+ lines): -30% penalty

**Action Thresholds:**
- ≥ 90%: Create regular PR
- ≥ 75%: Create draft PR
- ≥ 50%: Add comment only
- < 50%: Skip (don't apply fix)

### Supported Fix Patterns

The module can automatically fix these common Playwright issues:

1. **`missing_await`** - Missing `await` keywords before async operations
2. **`selector_timeout`** - Timeout waiting for selectors to appear
3. **`navigation_timeout`** - Page navigation timeouts
4. **`type_mismatch`** - Type assertion failures
5. **`module_not_found`** - Import/module resolution errors

See `NEW_FEATURE.md` for the complete implementation guide and `docs/PATTERN_LIBRARY.md` (when created) for detailed pattern examples.

### Working with the Dagger Module

**Environment Variables:**

The Dagger module requires these environment variables:

```bash
# AI Provider (choose one)
export OPENROUTER_API_KEY="sk-or-v1-..."  # For OpenRouter
export OPENAI_API_KEY="sk-..."            # For OpenAI
export ANTHROPIC_API_KEY="sk-ant-..."     # For Anthropic
export DEEPSEEK_API_KEY="sk-..."          # For DeepSeek direct

# GitHub (for PR creation)
export GITHUB_TOKEN="ghp_..."
export GITHUB_REPOSITORY="owner/repo"
```

**Testing Locally:**

```bash
# 1. Set up environment
cd dagger
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# 2. Run with sample data
cd ..
npm test -- sample-fail  # Generate failures
cd dagger
dagger call attempt-fix \
  --repo-dir=.. \
  --failures-json-path=../playwright-report/results.json \
  --ai-model=gpt-4o-mini
```

**Minimum Confidence Threshold:**

The default minimum confidence is `0.75` (75%). You can adjust this:

- **Higher (0.85-0.95)**: Fewer PRs, higher quality, less risk
- **Lower (0.60-0.70)**: More PRs, more manual review needed
- **Production recommendation**: Start with `0.80`

## Working with This Repository

### Adding New Test Scenarios

When adding test scenarios to demonstrate new failure types:

1. Add tests to `tests/sample-fail.spec.js` for failures
2. Add corresponding passing variants to `tests/sample-pass.spec.js`
3. Use short timeouts (2-3 seconds) to keep demo workflows fast
4. Document the failure type in the test name
5. Target `https://example.com` for consistency

### Modifying Workflows

When updating workflow configurations:

1. **Never remove the JSON reporter** from `playwright.config.js`
2. Keep the `set +e` pattern for capturing test exit codes
3. Maintain the `continue-on-error: true` on test steps
4. Use the `test-failed` output to conditionally run the analyzer
5. Set appropriate `max-failures` to limit issue size (default: 10)

### AI Configuration

The AI workflow uses **DeepSeek directly** (not via OpenRouter). To switch providers:

**For OpenRouter:**
```yaml
env:
  OPENROUTER_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  AI_MODEL: 'openrouter/deepseek/deepseek-chat'
```

**For OpenAI:**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  AI_MODEL: 'gpt-4o-mini'
```

See `.github/AI_SETUP.md` for complete setup instructions and provider comparisons.

## Playwright Configuration Notes

- **Base URL**: Set to `https://example.com` for demo tests
- **Retries**: 2 retries in CI, 0 locally
- **Workers**: 1 worker in CI (sequential execution), parallel locally
- **Artifacts**: Screenshots on failure, videos retained on failure, traces on first retry
- **Browser**: Chromium only (keeps demo simple and fast)

## Important Constraints

### What NOT to Change

1. **Do not modify the JSON reporter configuration** - it's required by the analyzer and Dagger module
2. **Do not remove the `set +e` pattern** - it's critical for workflow control flow
3. **Do not change test file names** without updating workflow files
4. **Keep intentional failures in `sample-fail.spec.js`** - they're the demo's purpose
5. **Do not modify `playwright-report/results.json` location** - both analyzer and Dagger depend on this path

### Dagger Module Constraints

When working with the Dagger auto-fix module:

1. **Always test fixes in containers** - Never skip the container testing step
2. **Respect confidence thresholds** - Don't create PRs for low-confidence fixes
3. **Validate AI responses** - Always parse and validate JSON from AI models
4. **Limit concurrent fixes** - Process maximum 5 failures at a time to avoid API rate limits
5. **Use specific patterns** - Don't attempt generic fixes; match specific error patterns

### Deduplication Behavior

The basic workflow has `deduplicate: false` to create a new issue for each run (better for demo purposes). In production usage, you'd typically enable deduplication to update existing issues instead of creating duplicates.

## Demo vs Production Usage

This is a **demonstration repository**. For production usage:

1. Enable `deduplicate: true` to avoid duplicate issues
2. Remove `expected-failure` labels
3. Adjust `max-failures` based on your needs
4. Use more specific issue titles without run numbers
5. Set appropriate workflow triggers (not scheduled demos)
6. Configure appropriate issue labels for your workflow

### Dagger Auto-Fix in Production

Additional considerations for production use of the Dagger auto-fix module:

1. **Start with high confidence threshold** (0.85-0.90) and gradually lower based on results
2. **Review all automated PRs** - Never merge auto-fix PRs without human review
3. **Monitor success metrics** - Track fix success rate, time saved, pattern coverage
4. **Set up rate limits** - Limit to 3-5 fix attempts per issue to avoid API costs
5. **Use draft PRs initially** - Start with draft PRs until confidence in the system is high
6. **Implement rollback procedures** - Have a plan to revert automated changes if issues arise
7. **Cost monitoring** - Track AI API costs; typical cost is $0.001-0.01 per fix attempt
8. **Pattern tuning** - Regularly update fix patterns based on what works/fails
9. **Test suite coverage** - Ensure comprehensive tests before enabling auto-fix
10. **Manual approval workflow** - Consider requiring explicit approval before auto-fix runs

## Dagger Integration Flow

### End-to-End Workflow

```
1. Developer pushes code
   ↓
2. GitHub Actions runs Playwright tests
   ↓
3. Tests fail
   ↓
4. Failure Analyzer creates issue with structured JSON
   ↓
5. Issue labeled with 'auto-fix-ready' (manual or automatic)
   ↓
6. Auto-fix workflow triggers
   ↓
7. Dagger module:
   - Reads failures JSON
   - Generates AI-powered fixes
   - Tests fixes in isolated containers
   - Calculates confidence scores
   ↓
8. If confidence ≥ threshold:
   - Creates branch with fixes
   - Opens PR with detailed explanation
   - Links PR to original issue
   ↓
9. Developer reviews PR
   ↓
10. PR merged or closed based on review
```

### Best Practices for Dagger Development

When developing or extending the Dagger module:

1. **Isolated testing** - Always test fixes in fresh containers, never on host
2. **Prompt versioning** - Version control prompt templates; track what works
3. **Error handling** - Gracefully handle AI timeouts, API errors, malformed responses
4. **Logging** - Log all AI interactions for debugging and improvement
5. **Cost optimization** - Use cheaper models (gpt-4o-mini, deepseek) for initial fixes
6. **Pattern specificity** - Narrowly scope fix patterns to avoid incorrect fixes
7. **Test coverage** - Each fix pattern should have comprehensive tests
8. **Rollback safety** - Always preserve original code in PR description
9. **Incremental fixes** - Fix one issue per PR when possible
10. **CI/CD integration** - Run Dagger tests in CI before merging module changes

## Related Documentation

### Analyzer Documentation

- Main action repository: https://github.com/decision-crafters/playwright-failure-analyzer
- AI setup guide: `.github/AI_SETUP.md`
- Configuration options: See action repository's `docs/CONFIGURATION.md`
- Troubleshooting: See action repository's `docs/TROUBLESHOOTING.md`

### Dagger Auto-Fix Documentation

- **Implementation guide**: `NEW_FEATURE.md` - Complete 4-phase implementation plan
- **Dagger module README**: `dagger/README.md` - Module overview and quick start (when created)
- **Setup instructions**: `docs/DAGGER_SETUP.md` - Detailed setup guide (when created)
- **Pattern library**: `docs/PATTERN_LIBRARY.md` - Supported patterns with examples (when created)
- **Auto-fix examples**: `docs/AUTO_FIX_EXAMPLES.md` - Real examples from demo repo (when created)
- **Official Dagger docs**: https://docs.dagger.io
- **Dagger LLM features**: https://docs.dagger.io/features/llm

### Key Implementation Files

When implementing or modifying the Dagger module:
- `dagger/src/main.py` - Main module entry point and workflow orchestration
- `dagger/src/fix_generator.py` - AI prompt engineering and response parsing
- `dagger/src/confidence_scorer.py` - Confidence calculation logic
- `dagger/src/test_runner.py` - Container-based test execution
- `dagger/src/pr_creator.py` - GitHub PR automation
- `.github/workflows/auto-fix.yml` - Auto-fix workflow trigger
