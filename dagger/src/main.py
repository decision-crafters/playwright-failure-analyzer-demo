"""Playwright Auto-Fixer Dagger Module - Main Integration."""

import dagger
from dagger import dag, function, object_type
import json
import os
from typing import Optional

from .fix_generator import FixGenerator
from .test_runner import TestRunner
from .confidence_scorer import ConfidenceScorer


@object_type
class PlaywrightAutoFixer:
    """Auto-fix Playwright test failures using AI and isolated containers."""

    @function
    async def hello(self) -> str:
        """Test function to verify module works."""
        return "Playwright Auto-Fixer v1.0.0 - Phase 3 Complete ✓\nFeatures: Fix Generation, Container Testing, PR Creation"

    @function
    async def attempt_fix(
        self,
        repo_dir: dagger.Directory,
        failures_json_path: str,
        ai_model: str = "gpt-4o-mini",
        min_confidence: float = 0.75,
        max_failures: int = 5,
        openai_api_key: Optional[dagger.Secret] = None,
        anthropic_api_key: Optional[dagger.Secret] = None,
        deepseek_api_key: Optional[dagger.Secret] = None,
    ) -> str:
        """
        Attempt to fix test failures automatically.

        Args:
            repo_dir: Repository directory
            failures_json_path: Path to structured failures JSON
            ai_model: AI model to use for fix generation
            min_confidence: Minimum confidence threshold (0.0-1.0)
            max_failures: Maximum number of failures to process
            openai_api_key: OpenAI API key (for GPT models)
            anthropic_api_key: Anthropic API key (for Claude models)
            deepseek_api_key: DeepSeek API key (for DeepSeek models)

        Returns:
            JSON string with fix results
        """
        # Set API keys in environment if provided
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = await openai_api_key.plaintext()
        if anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = await anthropic_api_key.plaintext()
        if deepseek_api_key:
            os.environ["DEEPSEEK_API_KEY"] = await deepseek_api_key.plaintext()
        print(f"🚀 Starting auto-fix with model: {ai_model}")
        print(f"📊 Confidence threshold: {min_confidence}")

        # Read failures JSON
        failures_data = await self._read_failures(repo_dir, failures_json_path)

        if not failures_data or not failures_data.get("failures"):
            return json.dumps({
                "status": "no_failures",
                "message": "No failures found in JSON",
                "fixes": []
            })

        # Initialize components
        fix_generator = FixGenerator(model=ai_model)
        test_runner = TestRunner()
        confidence_scorer = ConfidenceScorer()

        print(f"📝 Found {len(failures_data['failures'])} failures")

        results = []
        failures_to_process = failures_data["failures"][:max_failures]

        # Process each failure
        for idx, failure in enumerate(failures_to_process, 1):
            print(f"\n🔧 Processing failure {idx}/{len(failures_to_process)}: {failure.get('test_name', 'Unknown')}")

            try:
                # Read file content
                file_path = failure.get("file_path")
                if not file_path:
                    print(f"⚠️  No file path in failure data")
                    continue

                file_content = await self._read_file(repo_dir, file_path)
                if not file_content:
                    print(f"⚠️  Could not read file: {file_path}")
                    continue

                print(f"📄 Read file: {file_path}")

                # Generate fix
                print(f"🤖 Generating fix with AI...")
                fix_data = await fix_generator.generate_fix(failure, file_content)

                if not fix_data:
                    print(f"❌ Failed to generate fix")
                    continue

                print(f"✅ Fix generated (AI confidence: {fix_data.get('confidence', 0):.2%})")

                # Apply fix and run test
                print(f"🧪 Testing fix in container...")
                test_result = await test_runner.run_test(
                    repo_dir,
                    file_path,
                    fix_data["fixed_code"]
                )

                test_passed = test_result.get("passed", False)
                print(f"{'✅' if test_passed else '❌'} Test {'passed' if test_passed else 'failed'}")

                # Calculate confidence
                fix_complexity = len(fix_data["fixed_code"].split('\n'))
                confidence_result = confidence_scorer.calculate_confidence(
                    ai_confidence=fix_data.get("confidence", 0.7),
                    test_passed=test_passed,
                    pattern=failure.get("suggested_pattern", "unknown"),
                    model=ai_model,
                    fix_complexity=fix_complexity
                )

                final_confidence = confidence_result["confidence"]
                recommendation = confidence_result["recommendation"]

                print(f"📊 Final confidence: {final_confidence:.2%} -> {recommendation}")

                # Store result if confidence meets threshold
                if final_confidence >= min_confidence:
                    results.append({
                        "test_name": failure.get("test_name", "Unknown"),
                        "file": file_path,
                        "line_number": failure.get("line_number"),
                        "pattern": failure.get("suggested_pattern"),
                        "fix": fix_data["fixed_code"],
                        "explanation": fix_data.get("explanation"),
                        "ai_confidence": fix_data.get("confidence"),
                        "final_confidence": final_confidence,
                        "recommendation": recommendation,
                        "test_passed": test_passed,
                        "test_duration_ms": test_result.get("duration_ms", 0),
                    })
                    print(f"✅ Fix accepted (meets threshold)")
                else:
                    print(f"⚠️  Fix rejected (below threshold: {final_confidence:.2%} < {min_confidence:.2%})")

            except Exception as e:
                print(f"❌ Error processing {failure.get('file_path')}: {e}")
                continue

        # Calculate summary statistics
        total_processed = len(failures_to_process)
        total_accepted = len(results)
        avg_confidence = sum(r["final_confidence"] for r in results) / len(results) if results else 0.0

        print(f"\n📊 Summary:")
        print(f"   Total failures: {len(failures_data['failures'])}")
        print(f"   Processed: {total_processed}")
        print(f"   Accepted: {total_accepted}")
        print(f"   Avg confidence: {avg_confidence:.2%}")

        return json.dumps({
            "status": "completed",
            "total_failures": len(failures_data["failures"]),
            "processed": total_processed,
            "fixes_generated": total_accepted,
            "average_confidence": avg_confidence,
            "model": ai_model,
            "threshold": min_confidence,
            "fixes": results
        }, indent=2)

    @function
    async def fix_and_create_pr(
        self,
        repo_dir: dagger.Directory,
        failures_json_path: str,
        issue_number: int,
        github_token: dagger.Secret,
        ai_model: str = "gpt-4o-mini",
        min_confidence: float = 0.75,
        repository: str = "",
        base_branch: str = "main",
        openai_api_key: Optional[dagger.Secret] = None,
        anthropic_api_key: Optional[dagger.Secret] = None,
        deepseek_api_key: Optional[dagger.Secret] = None,
    ) -> str:
        """
        Attempt fixes and create PR if successful.

        Args:
            repo_dir: Repository directory
            failures_json_path: Path to failures JSON
            issue_number: GitHub issue number
            github_token: GitHub token (secret)
            ai_model: AI model to use
            min_confidence: Minimum confidence threshold
            repository: GitHub repository (owner/repo), defaults to GITHUB_REPOSITORY env
            base_branch: Base branch to merge into (default: main)
            openai_api_key: OpenAI API key (for GPT models)
            anthropic_api_key: Anthropic API key (for Claude models)
            deepseek_api_key: DeepSeek API key (for DeepSeek models)

        Returns:
            JSON with PR details
        """
        from .pr_creator import PRCreator

        print(f"\n🚀 Starting fix-and-create-PR workflow")
        print(f"   Issue: #{issue_number}")
        print(f"   Model: {ai_model}")
        print(f"   Threshold: {min_confidence}")

        # Generate fixes (reuse attempt_fix logic)
        results_json = await self.attempt_fix(
            repo_dir,
            failures_json_path,
            ai_model,
            min_confidence,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            deepseek_api_key=deepseek_api_key
        )

        results = json.loads(results_json)

        if results["status"] != "completed" or not results["fixes"]:
            print(f"❌ No fixes generated")
            return json.dumps({
                "status": "no_fixes_generated",
                "message": "No fixes met the confidence threshold",
                "issue_number": issue_number
            })

        # Get GitHub token value
        token_value = await github_token.plaintext()

        # Get repository from env if not provided
        if not repository:
            repository = os.getenv("GITHUB_REPOSITORY", "")
            if not repository:
                return json.dumps({
                    "status": "error",
                    "message": "GITHUB_REPOSITORY environment variable not set"
                })

        print(f"📦 Repository: {repository}")

        # Create PR creator
        pr_creator = PRCreator(
            token=token_value,
            repository=repository
        )

        # Calculate overall confidence
        fixes = results["fixes"]
        overall_confidence = sum(f["final_confidence"] for f in fixes) / len(fixes)

        print(f"📊 Overall confidence: {overall_confidence:.2%}")

        # Determine action based on highest recommendation
        recommendations = [f.get("recommendation", "SKIP") for f in fixes]
        top_recommendation = "SKIP"

        if "CREATE_PR" in recommendations:
            top_recommendation = "CREATE_PR"
        elif "CREATE_DRAFT_PR" in recommendations:
            top_recommendation = "CREATE_DRAFT_PR"
        elif "COMMENT_ONLY" in recommendations:
            top_recommendation = "COMMENT_ONLY"

        print(f"🎯 Action: {top_recommendation}")

        # Handle different recommendations
        if top_recommendation == "SKIP":
            return json.dumps({
                "status": "skipped",
                "message": "All fixes below confidence threshold",
                "issue_number": issue_number,
                "fixes_count": len(fixes),
                "average_confidence": overall_confidence,
            })

        elif top_recommendation == "COMMENT_ONLY":
            # Add comment to issue
            success = pr_creator.add_comment_to_issue(
                issue_number=issue_number,
                fixes=fixes,
                confidence=overall_confidence,
            )

            return json.dumps({
                "status": "comment_added" if success else "comment_failed",
                "message": "Fix suggestions added as comment (confidence too low for PR)",
                "issue_number": issue_number,
                "fixes_count": len(fixes),
                "average_confidence": overall_confidence,
            })

        else:
            # CREATE_PR or CREATE_DRAFT_PR - create the PR
            # Generate branch name
            primary_pattern = fixes[0].get("pattern", "unknown")
            branch_name = f"autofix/issue-{issue_number}-{primary_pattern}"

            print(f"🌿 Branch: {branch_name}")

            # Create PR
            is_draft = (top_recommendation == "CREATE_DRAFT_PR" or overall_confidence < 0.90)

            pr_result = pr_creator.create_pr(
                fixes=fixes,
                issue_number=issue_number,
                branch_name=branch_name,
                confidence=overall_confidence,
                base_branch=base_branch,
                draft=is_draft,
            )

            if pr_result.get("success"):
                print(f"✅ PR created successfully!")
                return json.dumps({
                    "status": "pr_created",
                    "pr_url": pr_result["pr_url"],
                    "branch": branch_name,
                    "issue_number": issue_number,
                    "fixes_applied": len(fixes),
                    "average_confidence": overall_confidence,
                    "is_draft": is_draft,
                }, indent=2)
            else:
                print(f"❌ PR creation failed")
                return json.dumps({
                    "status": "pr_failed",
                    "error": pr_result.get("error", "Unknown error"),
                    "issue_number": issue_number,
                    "fixes_count": len(fixes),
                }, indent=2)

    async def _read_failures(
        self,
        repo_dir: dagger.Directory,
        path: str
    ) -> Optional[dict]:
        """
        Read and parse failures JSON.

        Args:
            repo_dir: Repository directory
            path: Path to failures JSON file

        Returns:
            Parsed JSON dict or None if read fails
        """
        try:
            content = await repo_dir.file(path).contents()
            return json.loads(content)
        except Exception as e:
            print(f"❌ Error reading failures: {e}")
            return None

    async def _read_file(
        self,
        repo_dir: dagger.Directory,
        path: str
    ) -> str:
        """
        Read a file from the repository.

        Args:
            repo_dir: Repository directory
            path: File path

        Returns:
            File contents or empty string if read fails
        """
        try:
            return await repo_dir.file(path).contents()
        except Exception as e:
            print(f"❌ Error reading file {path}: {e}")
            return ""

    @function
    async def list_supported_patterns(self) -> str:
        """
        List supported fix patterns.

        Returns:
            JSON string with pattern information
        """
        fix_generator = FixGenerator()
        patterns = fix_generator.get_supported_patterns()

        return json.dumps({
            "supported_patterns": patterns,
            "count": len(patterns)
        }, indent=2)

    @function
    async def list_supported_models(self) -> str:
        """
        List supported AI models and their confidence multipliers.

        Returns:
            JSON string with model information
        """
        confidence_scorer = ConfidenceScorer()
        models = confidence_scorer.get_supported_models()

        return json.dumps({
            "supported_models": models,
            "count": len(models),
            "note": "Values are confidence multipliers (higher = more reliable)"
        }, indent=2)
