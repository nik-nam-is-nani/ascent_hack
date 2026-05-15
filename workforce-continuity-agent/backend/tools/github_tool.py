from typing import List, Dict, Optional
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


# Mock GitHub data
pull_requests: List[PullRequest] = []
commits: List[GitCommit] = []
pr_counter = 1


def create_pull_request(
    title: str,
    description: str,
    branch: str,
    base_branch: str = "main",
    author: str = "AgentExecutor"
) -> PullRequest:
    """Create a mock pull request"""
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


def create_branch(branch_name: str, base_branch: str = "main") -> Dict:
    """Create a mock branch"""
    return {
        "name": branch_name,
        "base": base_branch,
        "created_at": datetime.now().isoformat()
    }


def commit_changes(
    branch: str,
    message: str,
    files: Dict[str, str],
    author: str = "AgentExecutor"
) -> GitCommit:
    """Commit changes to a mock branch"""
    commit = GitCommit(
        id=f"COMMIT-{len(commits) + 1:04d}",
        message=message,
        author=author,
        branch=branch,
        files_changed=list(files.keys())
    )
    commits.append(commit)
    return commit


def get_pull_requests_by_author(author: str) -> List[PullRequest]:
    """Get all PRs by an author"""
    return [pr for pr in pull_requests if pr.author == author]


def get_open_pull_requests() -> List[PullRequest]:
    """Get all open PRs"""
    return [pr for pr in pull_requests if pr.status == "open"]


def merge_pull_request(pr_id: str) -> PullRequest:
    """Merge a PR"""
    for pr in pull_requests:
        if pr.id == pr_id:
            pr.status = "merged"
            return pr
    return None


def get_repository_stats() -> Dict:
    """Get mock repository stats"""
    return {
        "total_prs": len(pull_requests),
        "open_prs": len([pr for pr in pull_requests if pr.status == "open"]),
        "merged_prs": len([pr for pr in pull_requests if pr.status == "merged"]),
        "total_commits": len(commits)
    }


def get_code_review_comments(pr_id: str) -> List[Dict]:
    """Get mock code review comments for a PR"""
    return [
        {
            "id": "COMMENT-001",
            "author": "reviewer",
            "body": "LGTM!",
            "created_at": datetime.now().isoformat()
        }
    ]