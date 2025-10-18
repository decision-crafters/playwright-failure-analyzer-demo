#!/usr/bin/env node
/**
 * Transform Playwright's native results.json into structured failures format
 * expected by the Dagger auto-fix module.
 */

const fs = require('fs');
const path = require('path');

// Read Playwright results
const resultsPath = process.argv[2] || 'playwright-report/results.json';
const outputPath = process.argv[3] || 'playwright-report/structured-failures.json';

console.log(`📖 Reading Playwright results from: ${resultsPath}`);

const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));

// Helper: Extract pattern from error message
function detectPattern(errorMessage, errorType) {
  const msg = errorMessage.toLowerCase();

  if (msg.includes('missing await') || msg.includes('promise') && msg.includes('resolve')) {
    return 'missing_await';
  }
  if (msg.includes('navigation timeout') || msg.includes('goto')) {
    return 'navigation_timeout';
  }
  if (msg.includes('timeout') && (msg.includes('locator') || msg.includes('selector'))) {
    return 'selector_timeout';
  }
  if (errorType === 'AssertionError' || msg.includes('expected') && msg.includes('received')) {
    return 'type_mismatch';
  }
  if (msg.includes('module not found') || msg.includes('cannot find module')) {
    return 'module_not_found';
  }

  return 'unknown';
}

// Helper: Calculate confidence based on error clarity
function calculateConfidence(pattern, errorMessage) {
  const baseConfidence = {
    'missing_await': 0.95,
    'navigation_timeout': 0.80,
    'selector_timeout': 0.85,
    'type_mismatch': 0.90,
    'module_not_found': 0.88,
    'unknown': 0.70
  };

  let confidence = baseConfidence[pattern] || 0.70;

  // Boost confidence if error is very specific
  if (errorMessage.includes('line') || errorMessage.includes('at ')) {
    confidence += 0.05;
  }

  return Math.min(0.99, confidence);
}

// Extract failures from nested Playwright structure
const failures = [];

function traverseSuites(suites, filepath = '') {
  for (const suite of suites) {
    // Handle nested suites
    if (suite.suites && suite.suites.length > 0) {
      traverseSuites(suite.suites, filepath);
    }

    // Process specs
    if (suite.specs) {
      for (const spec of suite.specs) {
        // Convert absolute path to relative path from repo root
        let specFile = spec.file || filepath;

        // If it's an absolute path, extract the relative portion
        if (specFile.includes('/tests/')) {
          specFile = specFile.substring(specFile.indexOf('/tests/') + 1);
        } else if (specFile.includes('\\tests\\')) {
          // Handle Windows paths
          specFile = specFile.substring(specFile.indexOf('\\tests\\') + 1).replace(/\\/g, '/');
        }

        for (const test of spec.tests || []) {
          // Only process unexpected (failed/timed out) tests
          // In Playwright JSON, test.status is 'unexpected' for failures
          if (test.status === 'unexpected') {
            const result = test.results?.[0];
            if (!result) continue;

            const errorMessage = result.error?.message || 'Unknown error';
            const errorType = result.error?.name || 'Error';
            const stackTrace = result.error?.stack || '';

            // Get file path from error location (has full path) or spec.file
            let filePath = specFile;
            if (result.error?.location?.file) {
              filePath = result.error.location.file;
              // Convert absolute path to relative path from repo root
              if (filePath.includes('/tests/')) {
                filePath = filePath.substring(filePath.indexOf('/tests/') + 1);
              } else if (filePath.includes('\\tests\\')) {
                filePath = filePath.substring(filePath.indexOf('\\tests\\') + 1).replace(/\\/g, '/');
              }
            }

            // Try to extract line number from error location or stack trace
            let lineNumber = result.error?.location?.line || null;
            if (!lineNumber) {
              const lineMatch = stackTrace.match(/\.spec\.[jt]s:(\d+):/);
              if (lineMatch) {
                lineNumber = parseInt(lineMatch[1], 10);
              }
            }

            const pattern = detectPattern(errorMessage, errorType);
            const confidence = calculateConfidence(pattern, errorMessage);

            failures.push({
              test_name: spec.title || test.title || 'Unknown test',
              file_path: filePath,
              line_number: lineNumber,
              error_message: errorMessage.substring(0, 500), // Truncate long messages
              error_type: errorType,
              stack_trace: stackTrace.substring(0, 1000), // Truncate long stacks
              suggested_pattern: pattern,
              confidence: confidence,
            });
          }
        }
      }
    }
  }
}

// Traverse the suite tree
traverseSuites(results.suites || []);

// Build structured output
const output = {
  run_metadata: {
    timestamp: new Date().toISOString(),
    total_tests: results.stats?.expected || 0,
    passed: results.stats?.ok || 0,
    failed: results.stats?.unexpected || 0,
    playwright_version: results.config?.version || 'unknown',
  },
  failures: failures,
};

// Write output
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

console.log(`✅ Transformed ${failures.length} failures`);
console.log(`📝 Written to: ${outputPath}`);
console.log(`\nPattern breakdown:`);

const patternCounts = failures.reduce((acc, f) => {
  acc[f.suggested_pattern] = (acc[f.suggested_pattern] || 0) + 1;
  return acc;
}, {});

for (const [pattern, count] of Object.entries(patternCounts)) {
  console.log(`  - ${pattern}: ${count}`);
}

// Exit with code 0 if we found failures, 1 if no failures
process.exit(failures.length > 0 ? 0 : 1);
