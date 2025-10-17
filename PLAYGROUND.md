# Playwright Auto-Fix Playground

This repository contains tiered test suites designed for experimenting with AI-powered test fixing. Perfect for:
- **Benchmarking AI models** (GPT-4, Claude, DeepSeek, etc.)
- **Testing confidence scoring algorithms**
- **Validating auto-fix capabilities**
- **Learning Playwright best practices**

## Test Structure

### Difficulty Tiers

Tests are organized by difficulty to benchmark AI model performance:

| Tier | Confidence | Success Rate | Pattern Types |
|------|-----------|--------------|---------------|
| **Easy** ⭐ | 90-95% | 95%+ | Missing `await`, simple typos, wrong values |
| **Medium** ⭐⭐ | 70-85% | 70-80% | Timing issues, race conditions, async patterns |
| **Hard** ⭐⭐⭐ | 50-70% | 50-60% | Complex state, nested async, error handling |

### Test Files

```
tests/
├── easy-fixes.spec.js          # 8 simple, high-confidence failures
├── medium-fixes.spec.js        # 10 moderate difficulty failures
├── hard-fixes.spec.js          # 10 complex, low-confidence failures
└── solutions/
    ├── easy-fixes-solution.spec.js
    ├── medium-fixes-solution.spec.js
    └── hard-fixes-solution.spec.js
```

## Quick Start

### Running Tests

```bash
# Run tests by difficulty
npm run test:easy           # Easy fixes (should AI fix: YES)
npm run test:medium         # Medium fixes (should AI fix: MAYBE)
npm run test:hard           # Hard fixes (should AI fix: REVIEW)

# Run all difficulty levels
npm run test:all-difficulties

# Run solutions (all passing)
npm run test:easy-solution
npm run test:medium-solution
npm run test:hard-solution
npm run test:all-solutions
```

### Generating Fix Attempts

```bash
# Use Dagger to attempt fixes
cd dagger

# Easy fixes (expect high success)
dagger call attempt-fix \
  --repo-dir=.. \
  --failures-json-path=../playwright-report/results.json \
  --ai-model=gpt-4o-mini \
  --min-confidence=0.90

# Medium fixes (moderate success expected)
dagger call attempt-fix \
  --repo-dir=.. \
  --failures-json-path=../playwright-report/results.json \
  --ai-model=gpt-4o-mini \
  --min-confidence=0.75

# Hard fixes (low success expected)
dagger call attempt-fix \
  --repo-dir=.. \
  --failures-json-path=../playwright-report/results.json \
  --ai-model=gpt-4o-mini \
  --min-confidence=0.60
```

## Benchmarking AI Models

### Comparison Workflow

1. **Run tests** to generate failures:
   ```bash
   npm run test:easy          # Generates easy-fixes failures
   ```

2. **Attempt fixes** with different models:
   ```bash
   # GPT-4o-mini
   dagger call attempt-fix --ai-model=gpt-4o-mini --repo-dir=.. --failures-json-path=../playwright-report/results.json > results-gpt4o-mini.json

   # GPT-4o
   dagger call attempt-fix --ai-model=gpt-4o --repo-dir=.. --failures-json-path=../playwright-report/results.json > results-gpt4o.json

   # Claude 3.5 Sonnet
   dagger call attempt-fix --ai-model=claude-3-5-sonnet-20240620 --repo-dir=.. --failures-json-path=../playwright-report/results.json > results-claude.json

   # DeepSeek
   dagger call attempt-fix --ai-model=deepseek/deepseek-chat --repo-dir=.. --failures-json-path=../playwright-report/results.json > results-deepseek.json
   ```

3. **Compare results**:
   ```bash
   # Extract metrics
   cat results-*.json | jq '.fixes_generated, .average_confidence, .model'
   ```

### Expected Performance

Based on difficulty tier:

**Easy Fixes:**
- GPT-4o: 95%+ success, 0.92 avg confidence
- GPT-4o-mini: 90%+ success, 0.88 avg confidence
- Claude 3.5: 95%+ success, 0.91 avg confidence
- DeepSeek: 85%+ success, 0.80 avg confidence

**Medium Fixes:**
- GPT-4o: 75-85% success, 0.80 avg confidence
- GPT-4o-mini: 70-80% success, 0.75 avg confidence
- Claude 3.5: 75-85% success, 0.78 avg confidence
- DeepSeek: 65-75% success, 0.70 avg confidence

**Hard Fixes:**
- GPT-4o: 55-65% success, 0.65 avg confidence
- GPT-4o-mini: 50-60% success, 0.60 avg confidence
- Claude 3.5: 55-65% success, 0.63 avg confidence
- DeepSeek: 45-55% success, 0.55 avg confidence

## Pattern Library

### Easy Patterns

1. **missing_await** - Missing `await` keyword
   ```javascript
   // BROKEN
   page.click('button');

   // FIXED
   await page.click('button');
   ```

2. **selector_typo** - Simple typo in selector
   ```javascript
   // BROKEN
   page.locator('h11')  // Should be 'h1'

   // FIXED
   page.locator('h1')
   ```

3. **assertion_mismatch** - Wrong expected value
   ```javascript
   // BROKEN
   await expect(page.locator('h1')).toHaveText('Wrong');

   // FIXED
   await expect(page.locator('h1')).toHaveText('Example Domain');
   ```

### Medium Patterns

4. **navigation_timing** - Not waiting for navigation
5. **missing_wait** - No wait before interaction
6. **improper_wait** - Using `waitForTimeout` instead of proper wait
7. **selector_error** - Complex/ambiguous selector

### Hard Patterns

8. **race_condition** - Multiple conflicting async operations
9. **state_dependency** - Assuming state without verification
10. **async_coordination** - Improper sequencing of operations
11. **error_handling** - Missing try/catch or validation

## Experimentation Ideas

### 1. Model Comparison
Fork this repo and run your preferred models against each tier. Track:
- Fix success rate
- Average confidence
- Time per fix
- Cost per fix

### 2. Confidence Tuning
Adjust confidence thresholds and see how it affects:
- PR creation rate
- False positive rate
- Manual review burden

### 3. Pattern Development
Add new patterns to test:
- API mocking issues
- Mobile-specific failures
- Accessibility problems
- Network timing issues

### 4. Custom Difficulty Tiers
Create your own tiers based on your application:
- Framework-specific issues (React, Vue, Angular)
- Domain-specific patterns (e-commerce, forms, auth)
- Company-specific test patterns

## Contributing Patterns

To add a new test pattern:

1. **Choose difficulty tier** based on AI fix success rate:
   - Easy: AI fixes correctly >90% of time
   - Medium: AI fixes correctly 70-85% of time
   - Hard: AI fixes correctly 50-70% of time

2. **Add to appropriate test file**:
   ```javascript
   test('your pattern name', async ({ page }) => {
     // BUG: Description of what's wrong
     // Expected fix: What should be changed
     // Difficulty: ⭐⭐ Medium - Pattern: your_pattern_name
     // ... broken test code
   });
   ```

3. **Add solution** to `tests/solutions/`:
   ```javascript
   test('your pattern name', async ({ page }) => {
     // SOLUTION: Explanation of fix
     // ... corrected test code
   });
   ```

4. **Test it**:
   ```bash
   npm run test:medium          # Should fail
   npm run test:medium-solution # Should pass
   ```

5. **Submit PR** with benchmark results from 2+ AI models

## API Keys Setup

Set environment variables for AI providers:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# OpenRouter (fallback)
export OPENROUTER_API_KEY="sk-or-v1-..."
```

## Cost Estimates

Approximate costs per fix attempt (as of 2024):

| Model | Input Cost | Output Cost | Avg per Fix |
|-------|-----------|-------------|-------------|
| GPT-4o | $2.50/1M | $10.00/1M | $0.005-0.01 |
| GPT-4o-mini | $0.15/1M | $0.60/1M | $0.001-0.002 |
| Claude 3.5 | $3.00/1M | $15.00/1M | $0.006-0.012 |
| DeepSeek | $0.14/1M | $0.28/1M | $0.0005-0.001 |

**Tip:** Use cheaper models (GPT-4o-mini, DeepSeek) for easy/medium fixes, reserve expensive models for hard fixes.

## Best Practices

1. **Start with easy fixes** - Validate your setup works
2. **Compare multiple models** - Different models excel at different patterns
3. **Track metrics** - Log success rates and confidence scores
4. **Review all fixes** - Even 95% confidence should be human-reviewed
5. **Iterate on patterns** - Add real failures from your codebase

## Troubleshooting

**Q: Tests timing out?**
A: Increase timeout in playwright.config.js or individual tests

**Q: Dagger can't find module?**
A: Use `dagger -m dagger call` from repo root

**Q: API key errors?**
A: Verify environment variables are set: `echo $OPENAI_API_KEY`

**Q: Low confidence scores?**
A: This is expected! Medium/hard fixes should have lower confidence

**Q: Fixes not applying?**
A: Check test-results/ for actual Dagger container output

## Resources

- [Playwright Failure Analyzer](https://github.com/decision-crafters/playwright-failure-analyzer)
- [Dagger Documentation](https://docs.dagger.io)
- [Original Demo README](./README.md)
- [Implementation Details](./CLAUDE.md)

## License

MIT - Feel free to fork and experiment!
