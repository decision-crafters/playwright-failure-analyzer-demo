"""GitHub PR creation for auto-fixes."""

import os
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime


class PRCreator:
    """Creates GitHub PRs with auto-fixes."""

    def __init__(self, token: str, repository: str):
        """
        Initialize PR creator.

        Args:
            token: GitHub token with repo and PR permissions
            repository: Repository in format "owner/repo"
        """
        self.token = token
        self.repository = repository
        self.owner, self.repo = repository.split('/')

    def create_pr(
        self,
        fixes: List[Dict[str, Any]],
        issue_number: int,
        branch_name: str,
        confidence: float,
        base_branch: str = "main",
        draft: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a PR with fixes.

        Args:
            fixes: List of fix dicts with file, pattern, fix, explanation, etc.
            issue_number: Related issue number
            branch_name: Branch name for PR
            confidence: Overall confidence score (0.0-1.0)
            base_branch: Base branch to merge into (default: main)
            draft: Whether to create as draft PR

        Returns:
            PR details dict with success status, pr_url, branch, etc.
        """
        print(f"🔧 Creating PR for issue #{issue_number}")
        print(f"   Branch: {branch_name}")
        print(f"   Fixes: {len(fixes)}")
        print(f"   Confidence: {confidence:.0%}")

        # Create PR title and body
        title = self._format_pr_title(issue_number, fixes)
        body = self._format_pr_body(fixes, issue_number, confidence)

        # Build gh CLI command
        cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--body", body,
            "--head", branch_name,
            "--base", base_branch,
            "--repo", self.repository,
        ]

        # Add labels
        cmd.extend(["--label", "automated-fix"])
        cmd.extend(["--label", "needs-review"])

        # Check if should be draft based on confidence
        if draft or confidence < 0.90:
            cmd.append("--draft")
            print(f"   Creating as DRAFT PR (confidence < 90%)")

        # Set environment with token
        env = os.environ.copy()
        env['GH_TOKEN'] = self.token

        try:
            print(f"🚀 Running: gh pr create...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )

            pr_url = result.stdout.strip()
            print(f"✅ PR created: {pr_url}")

            return {
                "success": True,
                "pr_url": pr_url,
                "branch": branch_name,
                "issue_number": issue_number,
                "fixes_count": len(fixes),
                "confidence": confidence,
                "is_draft": draft or confidence < 0.90,
            }

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"❌ Failed to create PR: {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "branch": branch_name,
                "issue_number": issue_number,
            }

    def create_branch_and_commit(
        self,
        fixes: List[Dict[str, Any]],
        branch_name: str,
        base_branch: str = "main",
    ) -> Dict[str, Any]:
        """
        Create a branch and commit fixes.

        Args:
            fixes: List of fix dicts
            branch_name: Branch name to create
            base_branch: Base branch to branch from

        Returns:
            Dict with success status and details
        """
        env = os.environ.copy()
        env['GH_TOKEN'] = self.token

        try:
            # Create and checkout new branch
            print(f"🌿 Creating branch: {branch_name}")
            subprocess.run(
                ["git", "checkout", "-b", branch_name, base_branch],
                check=True,
                capture_output=True,
                env=env,
            )

            # Apply each fix
            for fix in fixes:
                file_path = fix.get("file")
                fixed_code = fix.get("fix")

                if file_path and fixed_code:
                    print(f"   Writing fix to {file_path}")
                    with open(file_path, 'w') as f:
                        f.write(fixed_code)

                    # Stage the file
                    subprocess.run(
                        ["git", "add", file_path],
                        check=True,
                        capture_output=True,
                        env=env,
                    )

            # Create commit
            commit_message = self._format_commit_message(fixes)
            print(f"💾 Committing changes...")

            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                capture_output=True,
                env=env,
            )

            # Push branch
            print(f"📤 Pushing to remote...")
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                check=True,
                capture_output=True,
                env=env,
            )

            print(f"✅ Branch created and pushed")

            return {
                "success": True,
                "branch": branch_name,
                "files_modified": len(fixes),
            }

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            print(f"❌ Failed to create branch: {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "branch": branch_name,
            }

    def add_comment_to_issue(
        self,
        issue_number: int,
        fixes: List[Dict[str, Any]],
        confidence: float,
    ) -> bool:
        """
        Add a comment to an issue with fix suggestions.

        Used when confidence is too low for PR but worth mentioning.

        Args:
            issue_number: Issue number
            fixes: List of fix dicts
            confidence: Overall confidence score

        Returns:
            True if comment added successfully
        """
        env = os.environ.copy()
        env['GH_TOKEN'] = self.token

        comment = self._format_issue_comment(fixes, confidence)

        try:
            print(f"💬 Adding comment to issue #{issue_number}")

            subprocess.run(
                [
                    "gh", "issue", "comment", str(issue_number),
                    "--body", comment,
                    "--repo", self.repository,
                ],
                check=True,
                capture_output=True,
                env=env,
            )

            print(f"✅ Comment added")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to add comment: {e.stderr}")
            return False

    def _format_pr_title(self, issue_number: int, fixes: List[Dict[str, Any]]) -> str:
        """
        Format PR title.

        Args:
            issue_number: Issue number
            fixes: List of fixes

        Returns:
            PR title string
        """
        # Get primary pattern
        patterns = [f.get("pattern", "unknown") for f in fixes]
        primary_pattern = patterns[0] if patterns else "unknown"

        # Count unique patterns
        unique_patterns = len(set(patterns))

        if unique_patterns == 1:
            pattern_desc = primary_pattern.replace("_", " ").title()
        else:
            pattern_desc = f"{unique_patterns} issues"

        return f"🤖 Auto-fix: {pattern_desc} (Issue #{issue_number})"

    def _format_pr_body(
        self,
        fixes: List[Dict[str, Any]],
        issue_number: int,
        confidence: float,
    ) -> str:
        """
        Format PR description.

        Args:
            fixes: List of fix dicts
            issue_number: Issue number
            confidence: Overall confidence score

        Returns:
            Formatted PR body (markdown)
        """
        lines = [
            f"# 🤖 Automated Fix",
            "",
            f"Fixes #{issue_number}",
            "",
            "## Summary",
            "",
            f"This PR contains **{len(fixes)} automated fix(es)** for test failures.",
            "",
            f"**Overall Confidence**: {confidence:.0%}",
            "",
        ]

        # Add quick stats
        patterns = [f.get("pattern", "unknown") for f in fixes]
        pattern_counts = {}
        for p in patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1

        lines.append("**Patterns Fixed**:")
        for pattern, count in pattern_counts.items():
            pattern_name = pattern.replace("_", " ").title()
            lines.append(f"- {pattern_name}: {count}")
        lines.append("")

        # Add changes section
        lines.append("## Changes Made")
        lines.append("")

        for i, fix in enumerate(fixes, 1):
            test_passed = "✅ Passed" if fix.get("test_passed") else "⚠️ Not verified"

            lines.extend([
                f"### {i}. {fix.get('test_name', 'Unknown test')}",
                "",
                f"**File**: `{fix.get('file', 'unknown')}`",
                f"**Pattern**: `{fix.get('pattern', 'unknown')}`",
                f"**Confidence**: {fix.get('final_confidence', 0):.0%}",
                f"**Test Result**: {test_passed}",
                "",
                "**Explanation**:",
                fix.get('explanation', 'No explanation provided'),
                "",
                "<details>",
                "<summary>View fix code</summary>",
                "",
                "```javascript",
                fix.get('fix', '// No fix code')[:500],  # Truncate long fixes
                "```",
                "</details>",
                "",
                "---",
                "",
            ])

        # Add testing section
        lines.extend([
            "## Testing",
            "",
            "- [x] Fixes generated by AI",
            "- [x] Fixes tested in isolated containers",
        ])

        # Add pass/fail info
        passed_tests = sum(1 for f in fixes if f.get("test_passed"))
        if passed_tests == len(fixes):
            lines.append("- [x] All fixes passed tests in containers ✅")
        elif passed_tests > 0:
            lines.append(f"- [x] {passed_tests}/{len(fixes)} fixes passed tests")
        else:
            lines.append("- [ ] Fixes need manual testing")

        lines.extend([
            "- [ ] Manual review completed",
            "- [ ] Full test suite verified",
            "",
        ])

        # Add important notice
        lines.extend([
            "## ⚠️ Important",
            "",
            "This is an **automated fix** generated by AI. Please:",
            "",
            "1. ✅ **Review the changes carefully** - AI can make mistakes",
            "2. 🧪 **Run the full test suite locally** - Container tests are isolated",
            "3. 🔍 **Verify no regressions** - Check related functionality",
            "4. 🎯 **Test edge cases** - Automated tests may not cover everything",
            "",
            f"💬 Questions? Comment on issue #{issue_number}",
            "",
            "---",
            "",
            f"🤖 Generated by [Playwright Auto-Fixer](https://github.com/{self.repository})",
            f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        ])

        return "\n".join(lines)

    def _format_commit_message(self, fixes: List[Dict[str, Any]]) -> str:
        """
        Format commit message.

        Args:
            fixes: List of fix dicts

        Returns:
            Commit message
        """
        patterns = [f.get("pattern", "unknown") for f in fixes]
        primary_pattern = patterns[0] if patterns else "unknown"

        # Format pattern name
        pattern_desc = primary_pattern.replace("_", " ")

        lines = [
            f"fix: auto-fix {pattern_desc} ({len(fixes)} file(s))",
            "",
            "Automated fixes generated by Playwright Auto-Fixer:",
            "",
        ]

        for fix in fixes:
            file_name = os.path.basename(fix.get("file", "unknown"))
            pattern = fix.get("pattern", "unknown").replace("_", " ")
            lines.append(f"- {file_name}: {pattern}")

        lines.extend([
            "",
            "🤖 Generated with AI",
            "Co-Authored-By: Playwright Auto-Fixer <noreply@github.com>",
        ])

        return "\n".join(lines)

    def _format_issue_comment(
        self,
        fixes: List[Dict[str, Any]],
        confidence: float,
    ) -> str:
        """
        Format issue comment for low-confidence fixes.

        Args:
            fixes: List of fix dicts
            confidence: Overall confidence score

        Returns:
            Comment body (markdown)
        """
        lines = [
            "## 🤖 Auto-Fix Suggestions",
            "",
            f"I analyzed the test failures and generated **{len(fixes)} potential fix(es)**.",
            "",
            f"**Confidence**: {confidence:.0%} (below threshold for automatic PR)",
            "",
            "### Suggested Fixes",
            "",
        ]

        for i, fix in enumerate(fixes, 1):
            lines.extend([
                f"#### {i}. {fix.get('test_name', 'Unknown')}",
                "",
                f"**Pattern**: `{fix.get('pattern', 'unknown')}`",
                f"**Confidence**: {fix.get('final_confidence', 0):.0%}",
                "",
                f"**Explanation**: {fix.get('explanation', 'N/A')}",
                "",
                "<details>",
                "<summary>View suggested fix</summary>",
                "",
                "```javascript",
                fix.get('fix', '// No fix')[:300],
                "```",
                "</details>",
                "",
            ])

        lines.extend([
            "---",
            "",
            "⚠️ These fixes have **lower confidence** and should be reviewed carefully.",
            "",
            "To apply these fixes manually:",
            "1. Review each suggestion",
            "2. Test thoroughly",
            "3. Adjust as needed",
            "",
            f"🤖 Generated by Playwright Auto-Fixer",
        ])

        return "\n".join(lines)
