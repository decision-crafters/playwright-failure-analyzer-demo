"""AI-powered fix code generation."""

import json
from typing import Dict, Any, List, Optional
import litellm


class FixGenerator:
    """Generates code fixes using AI."""

    # Pattern-specific prompts for different error types
    PROMPTS = {
        "missing_await": """Fix missing await in Playwright test.

Current code at {file_path}:{line_number}:
{error_context}

Error: {error_message}

Analyze the code and fix the missing await keyword. Return ONLY valid JSON in this format:
{{
  "fixed_code": "await page.goto(url)",
  "explanation": "Added missing await keyword before async operation",
  "confidence": 0.95
}}""",

        "selector_timeout": """Fix selector timeout in Playwright test.

Current code at {file_path}:{line_number}:
{error_context}

Error: {error_message}

The selector is timing out. Possible fixes:
1. Update the selector to match actual elements
2. Increase timeout if element loads slowly
3. Wait for element to be ready before interacting

Return ONLY valid JSON in this format:
{{
  "fixed_code": "await expect(page.locator('h1')).toBeVisible()",
  "explanation": "Updated selector to match actual page element",
  "confidence": 0.85
}}""",

        "navigation_timeout": """Fix navigation timeout in Playwright test.

Current code at {file_path}:{line_number}:
{error_context}

Error: {error_message}

Navigation is timing out. Possible fixes:
1. Fix the URL if it's incorrect
2. Increase navigation timeout for slow-loading pages
3. Add proper waiting strategy

Return ONLY valid JSON in this format:
{{
  "fixed_code": "await page.goto('https://example.com', {{ timeout: 10000 }})",
  "explanation": "Fixed URL and increased timeout for navigation",
  "confidence": 0.80
}}""",

        "type_mismatch": """Fix type/assertion mismatch in Playwright test.

Current code at {file_path}:{line_number}:
{error_context}

Error: {error_message}

The assertion is failing due to value mismatch. Analyze the expected vs received values and fix the assertion.

Return ONLY valid JSON in this format:
{{
  "fixed_code": "expect(title).toBe('Example Domain')",
  "explanation": "Updated expected value to match actual page title",
  "confidence": 0.90
}}""",

        "module_not_found": """Fix module import error in test.

Current code at {file_path}:{line_number}:
{error_context}

Error: {error_message}

Module cannot be found. Possible fixes:
1. Fix import path
2. Update module name
3. Ensure dependency is installed

Return ONLY valid JSON in this format:
{{
  "fixed_code": "const {{ test, expect }} = require('@playwright/test')",
  "explanation": "Fixed import statement to use correct module path",
  "confidence": 0.88
}}""",

        "unknown": """Fix Playwright test failure.

Current code at {file_path}:{line_number}:
{error_context}

Error: {error_message}

Analyze the error and provide a fix. Return ONLY valid JSON in this format:
{{
  "fixed_code": "// fixed code here",
  "explanation": "Brief explanation of fix",
  "confidence": 0.70
}}""",
    }

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize fix generator with AI model.

        Args:
            model: AI model to use (gpt-4o-mini, claude-3-5-sonnet-20240620, etc.)
        """
        self.model = model

    async def generate_fix(
        self,
        failure: Dict[str, Any],
        file_content: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a fix for a single failure.

        Args:
            failure: Failure data from structured JSON with keys:
                - file_path: Path to failing test file
                - line_number: Line number of failure
                - error_message: Error message
                - suggested_pattern: Error pattern type
            file_content: Full file content for context

        Returns:
            Fix dict with fixed_code, explanation, confidence or None if generation fails
        """
        pattern = failure.get("suggested_pattern", "unknown")
        prompt_template = self.PROMPTS.get(pattern, self.PROMPTS["unknown"])

        # Extract code context around the failure line
        error_context = self._extract_context(
            file_content,
            failure.get("line_number")
        )

        # Build prompt
        prompt = prompt_template.format(
            file_path=failure.get("file_path", "unknown"),
            line_number=failure.get("line_number", "unknown"),
            error_message=failure.get("error_message", "Unknown error"),
            error_context=error_context,
        )

        # Call AI via LiteLLM
        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Playwright test fixing expert. Return ONLY valid JSON with fixed_code, explanation, and confidence (0.0-1.0)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Low temperature for consistent fixes
                max_tokens=500,
                timeout=30,
            )

            # Parse response
            fix_data = self._parse_response(response.choices[0].message.content)

            if fix_data:
                # Add original pattern info
                fix_data["pattern"] = pattern

            return fix_data

        except Exception as e:
            print(f"Error generating fix: {e}")
            return None

    def _extract_context(self, file_content: str, line_number: Optional[int]) -> str:
        """
        Extract 5 lines of context around the error line.

        Args:
            file_content: Full file content
            line_number: Line number where error occurred

        Returns:
            Context string with line numbers
        """
        if not line_number:
            # Return first 500 chars if no line number
            return file_content[:500] + ("..." if len(file_content) > 500 else "")

        lines = file_content.split('\n')

        # Get context: 2 lines before, error line, 2 lines after
        start = max(0, line_number - 3)
        end = min(len(lines), line_number + 2)

        context_lines = []
        for i in range(start, end):
            # Mark the error line with >>>
            prefix = ">>> " if i == line_number - 1 else "    "
            context_lines.append(f"{prefix}{i+1}: {lines[i]}")

        return '\n'.join(context_lines)

    def _parse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response JSON, handling various formats.

        Args:
            response_text: Raw AI response

        Returns:
            Parsed dict or None if parsing fails
        """
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()

            # Handle ```json blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end].strip()
            # Handle ``` blocks
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end].strip()

            # Find JSON object if embedded in other text
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                text = text[start:end]

            # Parse JSON
            data = json.loads(text)

            # Validate required fields
            if not isinstance(data, dict):
                return None

            if "fixed_code" not in data:
                return None

            # Ensure confidence is a float between 0 and 1
            if "confidence" in data:
                confidence = float(data["confidence"])
                data["confidence"] = max(0.0, min(1.0, confidence))
            else:
                data["confidence"] = 0.7  # Default confidence

            # Ensure explanation exists
            if "explanation" not in data:
                data["explanation"] = "AI-generated fix"

            return data

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Failed to parse AI response: {e}")
            print(f"Response text: {response_text[:200]}...")
            return None

    def get_supported_patterns(self) -> List[str]:
        """
        Get list of supported fix patterns.

        Returns:
            List of pattern names
        """
        return [key for key in self.PROMPTS.keys() if key != "unknown"]
