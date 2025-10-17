"""Enhanced confidence scoring for auto-fix decisions."""

from typing import Dict, Any


class ConfidenceScorer:
    """Calculates confidence scores for fixes."""

    # Model-based multipliers (aligned with analyzer)
    MODEL_MULTIPLIERS = {
        'gpt-4': 1.0,
        'gpt-4o': 1.0,
        'gpt-4o-mini': 0.85,
        'gpt-4-turbo': 1.0,
        'claude-3-5-sonnet': 1.0,
        'claude-3-sonnet': 0.95,
        'claude-3-opus': 1.0,
        'deepseek-chat': 0.70,
        'deepseek-coder': 0.75,
        'deepseek/deepseek-chat': 0.70,
        'deepseek/deepseek-coder': 0.75,
    }

    # Pattern-based confidence boosts
    PATTERN_BOOSTS = {
        "missing_await": 0.10,      # Very clear pattern
        "module_not_found": 0.10,   # Usually straightforward
        "type_mismatch": 0.08,      # Clear mismatch
        "selector_timeout": 0.05,   # More context-dependent
        "navigation_timeout": 0.05, # Could have multiple causes
    }

    def calculate_confidence(
        self,
        ai_confidence: float,
        test_passed: bool,
        pattern: str,
        model: str,
        fix_complexity: int = 1,
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score for a fix.

        Args:
            ai_confidence: AI's raw confidence (0.0-1.0)
            test_passed: Whether test passed after fix
            pattern: Error pattern detected (e.g., "missing_await")
            model: AI model used (e.g., "gpt-4o-mini")
            fix_complexity: Number of lines changed

        Returns:
            Dict with:
                - confidence: float - Final confidence score (0.0-1.0)
                - raw_confidence: float - Original AI confidence
                - model_multiplier: float - Model adjustment factor
                - test_boost: float - Boost from test passing
                - pattern_boost: float - Boost from pattern confidence
                - complexity_penalty: float - Penalty for complex fixes
                - recommendation: str - Action to take
        """
        # Ensure AI confidence is valid
        ai_confidence = max(0.0, min(1.0, float(ai_confidence)))

        # Get model multiplier
        model_key = self._normalize_model_name(model)
        model_multiplier = self.MODEL_MULTIPLIERS.get(model_key, 0.60)

        # Apply model multiplier to AI confidence
        adjusted_confidence = ai_confidence * model_multiplier

        # Boost if test passed (significant indicator of success)
        test_boost = 0.15 if test_passed else 0.0
        adjusted_confidence = min(adjusted_confidence + test_boost, 1.0)

        # Pattern-based boost (some patterns are easier to fix)
        pattern_boost = self._get_pattern_boost(pattern)
        adjusted_confidence = min(adjusted_confidence + pattern_boost, 1.0)

        # Complexity penalty (complex fixes are riskier)
        complexity_penalty = self._calculate_complexity_penalty(fix_complexity)
        adjusted_confidence *= (1.0 - complexity_penalty)

        # Ensure final confidence is in valid range
        adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))

        # Determine recommended action
        recommendation = self._get_recommendation(adjusted_confidence)

        return {
            "confidence": adjusted_confidence,
            "raw_confidence": ai_confidence,
            "model_multiplier": model_multiplier,
            "test_boost": test_boost,
            "pattern_boost": pattern_boost,
            "complexity_penalty": complexity_penalty,
            "recommendation": recommendation,
        }

    def _normalize_model_name(self, model: str) -> str:
        """
        Normalize model name for lookup.

        Args:
            model: Model name (may include provider prefix)

        Returns:
            Normalized model name
        """
        model_lower = model.lower()

        # Remove provider prefixes (openrouter/, anthropic/, etc.)
        if '/' in model_lower:
            parts = model_lower.split('/')
            model_lower = parts[-1]  # Take last part

        # Check for matches
        for key in self.MODEL_MULTIPLIERS.keys():
            if key in model_lower or model_lower in key:
                return key

        # Unknown model - use conservative multiplier
        return "unknown"

    def _get_pattern_boost(self, pattern: str) -> float:
        """
        Get confidence boost based on error pattern.

        Args:
            pattern: Error pattern type

        Returns:
            Boost value (0.0-0.10)
        """
        return self.PATTERN_BOOSTS.get(pattern, 0.0)

    def _calculate_complexity_penalty(self, lines_changed: int) -> float:
        """
        Calculate penalty based on fix complexity.

        More complex fixes (more lines changed) are riskier.

        Args:
            lines_changed: Number of lines in the fix

        Returns:
            Penalty percentage (0.0-0.30)
        """
        if lines_changed <= 1:
            return 0.0  # No penalty for single-line fixes
        elif lines_changed <= 5:
            return 0.0  # Simple multi-line fixes
        elif lines_changed <= 10:
            return 0.15  # Moderate complexity
        else:
            return 0.30  # High complexity - significant penalty

    def _get_recommendation(self, confidence: float) -> str:
        """
        Get action recommendation based on confidence score.

        Args:
            confidence: Final confidence score (0.0-1.0)

        Returns:
            One of: CREATE_PR, CREATE_DRAFT_PR, COMMENT_ONLY, SKIP
        """
        if confidence >= 0.90:
            return "CREATE_PR"
        elif confidence >= 0.75:
            return "CREATE_DRAFT_PR"
        elif confidence >= 0.50:
            return "COMMENT_ONLY"
        else:
            return "SKIP"

    def get_model_multiplier(self, model: str) -> float:
        """
        Get the multiplier for a specific model.

        Args:
            model: Model name

        Returns:
            Multiplier value
        """
        model_key = self._normalize_model_name(model)
        return self.MODEL_MULTIPLIERS.get(model_key, 0.60)

    def get_supported_models(self) -> Dict[str, float]:
        """
        Get all supported models and their multipliers.

        Returns:
            Dict of model names to multipliers
        """
        return self.MODEL_MULTIPLIERS.copy()

    def should_create_pr(self, confidence: float, min_threshold: float = 0.75) -> bool:
        """
        Determine if a PR should be created based on confidence.

        Args:
            confidence: Confidence score
            min_threshold: Minimum threshold to create PR

        Returns:
            True if PR should be created
        """
        return confidence >= min_threshold

    def get_recommendation_details(self, recommendation: str) -> Dict[str, Any]:
        """
        Get detailed information about a recommendation.

        Args:
            recommendation: Recommendation type

        Returns:
            Dict with details about the recommendation
        """
        details = {
            "CREATE_PR": {
                "action": "Create pull request",
                "description": "High confidence - create regular PR for review",
                "draft": False,
                "min_confidence": 0.90,
            },
            "CREATE_DRAFT_PR": {
                "action": "Create draft pull request",
                "description": "Good confidence - create draft PR for careful review",
                "draft": True,
                "min_confidence": 0.75,
            },
            "COMMENT_ONLY": {
                "action": "Add comment to issue",
                "description": "Moderate confidence - suggest fix in comment only",
                "draft": False,
                "min_confidence": 0.50,
            },
            "SKIP": {
                "action": "Skip fix",
                "description": "Low confidence - do not apply fix",
                "draft": False,
                "min_confidence": 0.0,
            },
        }

        return details.get(recommendation, details["SKIP"])
