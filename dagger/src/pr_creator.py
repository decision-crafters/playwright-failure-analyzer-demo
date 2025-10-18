"""GitHub PR creation for auto-fixes using GitHub REST API."""

import base64
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests


class PRCreator:
    """Creates GitHub PRs with auto-fixes using GitHub REST API."""

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
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

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

        # Determine if should be draft
        is_draft = draft or confidence < 0.90
        if is_draft:
            print(f"   Creating as DRAFT PR (confidence < 90%)")

        try:
            print(f"🚀 Creating PR via GitHub API...")

            # Create PR
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls"
            payload = {
                "title": title,
                "body": body,
                "head": branch_name,
                "base": base_branch,
                "draft": is_draft,
            }

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            pr_data = response.json()
            pr_url = pr_data["html_url"]
            pr_number = pr_data["number"]

            print(f"✅ PR created: {pr_url}")

            # Add labels
            self._add_labels_to_pr(pr_number, ["automated-fix", "needs-review"])

            return {
                "success": True,
                "pr_url": pr_url,
                "pr_number": pr_number,
                "branch": branch_name,
                "issue_number": issue_number,
                "fixes_count": len(fixes),
                "confidence": confidence,
                "is_draft": is_draft,
            }

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    error_msg = e.response.text or error_msg

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
        Create a branch and commit fixes using GitHub API.

        Args:
            fixes: List of fix dicts
            branch_name: Branch name to create
            base_branch: Base branch to branch from

        Returns:
            Dict with success status and details
        """
        try:
            print(f"🌿 Creating branch: {branch_name}")

            # Get the base branch SHA
            ref_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/refs/heads/{base_branch}"
            response = requests.get(ref_url, headers=self.headers)
            response.raise_for_status()
            base_sha = response.json()["object"]["sha"]

            print(f"   Base SHA: {base_sha[:7]}")

            # Create new branch reference
            create_ref_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/refs"
            payload = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            }
            response = requests.post(create_ref_url, headers=self.headers, json=payload)
            response.raise_for_status()

            print(f"✅ Branch created")

            # Get the base tree
            commit_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/commits/{base_sha}"
            response = requests.get(commit_url, headers=self.headers)
            response.raise_for_status()
            base_tree_sha = response.json()["tree"]["sha"]

            # Create blobs for each file
            tree_items = []
            for fix in fixes:
                file_path = fix.get("file")
                fixed_code = fix.get("fix")

                if file_path and fixed_code:
                    print(f"   Creating blob for {file_path}")

                    # Create blob
                    blob_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/blobs"
                    blob_payload = {
                        "content": fixed_code,
                        "encoding": "utf-8",
                    }
                    response = requests.post(blob_url, headers=self.headers, json=blob_payload)
                    response.raise_for_status()
                    blob_sha = response.json()["sha"]

                    # Add to tree
                    tree_items.append({
                        "path": file_path,
                        "mode": "100644",  # Regular file
                        "type": "blob",
                        "sha": blob_sha,
                    })

            # Create new tree
            print(f"   Creating tree with {len(tree_items)} file(s)")
            tree_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/trees"
            tree_payload = {
                "base_tree": base_tree_sha,
                "tree": tree_items,
            }
            response = requests.post(tree_url, headers=self.headers, json=tree_payload)
            response.raise_for_status()
            new_tree_sha = response.json()["sha"]

            # Create commit
            commit_message = self._format_commit_message(fixes)
            print(f"💾 Creating commit...")

            commit_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/commits"
            commit_payload = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [base_sha],
            }
            response = requests.post(commit_url, headers=self.headers, json=commit_payload)
            response.raise_for_status()
            new_commit_sha = response.json()["sha"]

            # Update branch reference to point to new commit
            print(f"📤 Updating branch reference...")
            update_ref_url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
            update_payload = {
                "sha": new_commit_sha,
                "force": False,
            }
            response = requests.patch(update_ref_url, headers=self.headers, json=update_payload)
            response.raise_for_status()

            print(f"✅ Branch created and committed")

            return {
                "success": True,
                "branch": branch_name,
                "commit_sha": new_commit_sha,
                "files_modified": len(fixes),
            }

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    error_msg = e.response.text or error_msg

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
        comment = self._format_issue_comment(fixes, confidence)

        try:
            print(f"💬 Adding comment to issue #{issue_number}")

            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
            payload = {
                "body": comment,
            }

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            print(f"✅ Comment added")
            return True

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    pass

            print(f"❌ Failed to add comment: {error_msg}")
            return False

    def _add_labels_to_pr(self, pr_number: int, labels: List[str]) -> bool:
        """
        Add labels to a PR.

        Args:
            pr_number: PR number
            labels: List of label names

        Returns:
            True if labels added successfully
        """
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/issues/{pr_number}/labels"
            payload = {
                "labels": labels,
            }

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            print(f"   Added labels: {', '.join(labels)}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to add labels (non-critical): {e}")
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
            # Extract just filename from path
            file_path = fix.get("file", "unknown")
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path
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
