import os
import subprocess
import shutil
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel


class PullRequest(BaseModel):
    id: str
    number: int
    title: str
    description: str
    author: str
    branch: str
    status: str  # open, merged, closed
    created_at: datetime
    url: Optional[str] = None


class GitCommit(BaseModel):
    id: str
    message: str
    author: str
    branch: str
    files_changed: List[str] = []


# In-memory tracking (for API responses)
pull_requests: List[PullRequest] = []
commits: List[GitCommit] = []
pr_counter = 1


def _run_git(args: List[str], cwd: str = None) -> Tuple[bool, str]:
    """Run a git command and return (success, output)"""
    if cwd is None:
        from .workspace_tool import WORKSPACE_ROOT
        cwd = WORKSPACE_ROOT

    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Git command timed out"
    except Exception as e:
        return False, str(e)


def _ensure_auth_remote(token: str) -> bool:
    """Ensure the remote URL includes the auth token"""
    if not token:
        print("[GIT] _ensure_auth_remote: no token provided", flush=True)
        return False

    from .workspace_tool import WORKSPACE_ROOT

    if not os.path.exists(os.path.join(WORKSPACE_ROOT, ".git")):
        print("[GIT] _ensure_auth_remote: not a git repo", flush=True)
        return False

    success, current_url = _run_git(["remote", "get-url", "origin"])
    if not success:
        print(f"[GIT] _ensure_auth_remote: failed to get URL: {current_url}", flush=True)
        return False

    if "github.com" in current_url:
        # Always rebuild the URL with the token to be safe
        clean_url = current_url
        if "@" in clean_url:
            parts = clean_url.split("@")
            clean_url = "https://" + parts[1]

        auth_url = f"https://{token}@{clean_url.replace('https://', '')}"
        _run_git(["remote", "set-url", "origin", auth_url])
        print(f"[GIT] Remote URL set (has token: {token[:10]}...)", flush=True)
        return True

    print(f"[GIT] _ensure_auth_remote: URL doesn't contain github.com: {current_url[:50]}", flush=True)
    return False


def pull_from_github(token: str = None, branch: str = "main") -> Tuple[bool, str]:
    """Pull latest changes from GitHub remote"""
    if token:
        _ensure_auth_remote(token)

    success, output = _run_git(["fetch", "origin"])
    if not success:
        return False, f"Fetch failed: {output}"

    success, output = _run_git(["pull", "origin", branch, "--rebase"])
    if not success:
        # Try without rebase
        success, output = _run_git(["pull", "origin", branch])
        if not success:
            return False, f"Pull failed: {output}"

    return True, "Pull successful"


def create_feature_branch(branch_name: str, base_branch: str = "main") -> Tuple[bool, str]:
    """Create and checkout a new feature branch from base"""
    from .workspace_tool import WORKSPACE_ROOT

    if not os.path.exists(os.path.join(WORKSPACE_ROOT, ".git")):
        print("[GIT] create_feature_branch: not a git repo", flush=True)
        return False, "Not a git repository"

    print(f"[GIT] Creating branch '{branch_name}' from '{base_branch}'", flush=True)

    # Ensure we're on the base branch
    ok, out = _run_git(["checkout", base_branch])
    print(f"[GIT] checkout {base_branch}: {ok}", flush=True)
    _run_git(["pull", "origin", base_branch])

    # Delete local branch if it exists (from previous run)
    _run_git(["branch", "-D", branch_name])

    # Delete remote branch if it exists (from previous run)
    _run_git(["push", "origin", "--delete", branch_name])

    # Create and checkout new branch
    success, output = _run_git(["checkout", "-b", branch_name])
    if not success:
        print(f"[GIT] checkout -b failed: {output}", flush=True)
        return False, f"Failed to create branch: {output}"

    print(f"[GIT] Branch '{branch_name}' created", flush=True)
    return True, f"Branch '{branch_name}' ready"


def commit_and_push(
    branch: str,
    message: str,
    files: Dict[str, str],
    token: str = None,
    author: str = "AgentExecutor"
) -> Tuple[bool, str, GitCommit]:
    """Write files, commit, and push to GitHub — all in one operation"""
    from .workspace_tool import WORKSPACE_ROOT, write_to_workspace

    print(f"[GIT] commit_and_push: {len(files)} files on branch '{branch}'", flush=True)

    # 1. Write all files to disk
    for path, content in files.items():
        write_to_workspace(path, content)
        print(f"[GIT]   wrote: {path} ({len(content)} bytes)", flush=True)

    # 2. Stage all changes
    success, output = _run_git(["add", "."])
    if not success:
        print(f"[GIT] add failed: {output}", flush=True)
        return False, f"Git add failed: {output}", None

    # 3. Check if there are changes to commit
    success, status = _run_git(["status", "--porcelain"])
    if not status.strip():
        print(f"[GIT] No changes to commit", flush=True)
        return True, "No changes to commit", GitCommit(
            id="NOOP", message="No changes", author=author, branch=branch
        )

    # 4. Commit
    success, output = _run_git(["commit", "-m", message, "--author", f"{author} <agent@ascent.ai>"])
    if not success:
        print(f"[GIT] commit failed: {output}", flush=True)
        return False, f"Git commit failed: {output}", None
    print(f"[GIT] Committed: {message}", flush=True)

    # 5. Push
    if token:
        _ensure_auth_remote(token)

    print(f"[GIT] Pushing to origin/{branch}...", flush=True)
    success, output = _run_git(["push", "-u", "origin", branch])
    if not success:
        print(f"[GIT] Push failed, trying force push...", flush=True)
        success, output = _run_git(["push", "-f", "origin", branch])
        if not success:
            print(f"[GIT] Force push also failed: {output}", flush=True)
            return False, f"Git push failed: {output}", None

    print(f"[GIT] Push successful to origin/{branch}", flush=True)

    # Track commit
    commit = GitCommit(
        id=f"COMMIT-{len(commits) + 1:04d}",
        message=message,
        author=author,
        branch=branch,
        files_changed=list(files.keys())
    )
    commits.append(commit)

    return True, "Push successful", commit


def create_pull_request(
    title: str,
    description: str,
    branch: str,
    base_branch: str = "main",
    author: str = "AgentExecutor"
) -> PullRequest:
    """Create a PR record (in-memory for dashboard tracking)"""
    global pr_counter
    pr = PullRequest(
        id=f"PR-{pr_counter:04d}",
        number=pr_counter,
        title=title,
        description=description,
        author=author,
        branch=branch,
        status="open",
        created_at=datetime.now(),
        url=f"https://github.com/company/project/pull/{pr_counter}"
    )
    pull_requests.append(pr)
    pr_counter += 1
    return pr


def get_repo_status() -> Dict:
    """Get current git repository status"""
    from .workspace_tool import WORKSPACE_ROOT

    if not os.path.exists(os.path.join(WORKSPACE_ROOT, ".git")):
        return {"is_repo": False, "error": "Not a git repository"}

    _, branch = _run_git(["branch", "--show-current"])
    _, status = _run_git(["status", "--short"])
    _, log = _run_git(["log", "--oneline", "-5"])
    _, remote = _run_git(["remote", "get-url", "origin"])

    return {
        "is_repo": True,
        "current_branch": branch,
        "working_tree_status": status.split("\n") if status else [],
        "recent_commits": log.split("\n") if log else [],
        "remote_url": remote,
        "total_tracked_commits": len(commits),
        "total_prs": len(pull_requests)
    }


def get_pull_requests_by_author(author: str) -> List[PullRequest]:
    return [pr for pr in pull_requests if pr.author == author]


def get_open_pull_requests() -> List[PullRequest]:
    return [pr for pr in pull_requests if pr.status == "open"]


def merge_pull_request(pr_id: str) -> Optional[PullRequest]:
    for pr in pull_requests:
        if pr.id == pr_id:
            pr.status = "merged"
            return pr
    return None


def get_repository_stats() -> Dict:
    return {
        "total_prs": len(pull_requests),
        "open_prs": len([pr for pr in pull_requests if pr.status == "open"]),
        "merged_prs": len([pr for pr in pull_requests if pr.status == "merged"]),
        "total_commits": len(commits)
    }
