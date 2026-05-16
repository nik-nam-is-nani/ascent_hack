import os
import subprocess
import shutil
import time
from typing import Dict, List, Tuple

WORKSPACE_ROOT = os.path.join(os.getcwd(), "simulated_workspace")

def _force_delete(path):
    """Force delete a directory or file, handling read-only git files"""
    if not os.path.exists(path):
        return
    
    def handle_error(func, path, exc_info):
        import stat
        try:
            os.chmod(path, stat.S_IWUSR)
            func(path)
        except:
            pass

    if os.path.isdir(path):
        shutil.rmtree(path, onerror=handle_error)
    else:
        try:
            os.chmod(path, 0o777)
            os.remove(path)
        except:
            pass

def clone_repository(repo_url: str, token: str = None) -> Tuple[bool, str]:
    """Clone a real repository into the simulated workspace with extreme robustness"""
    temp_clone_dir = os.path.join(os.getcwd(), "temp_clone_ascent")
    
    try:
        # 1. Prepare clean temp directory
        if os.path.exists(temp_clone_dir):
            _force_delete(temp_clone_dir)
        os.makedirs(temp_clone_dir, exist_ok=True)
        
        # 2. Authenticated URL Preparation
        if token and "github.com" in repo_url:
            clean_url = repo_url.replace("https://", "").replace("http://", "")
            auth_url = f"https://{token}@{clean_url}"
        else:
            auth_url = repo_url

        print(f"[WORKSPACE] Cloning {repo_url} into temp dir", flush=True)
        print(f"[WORKSPACE] Auth URL starts with: {auth_url[:40]}...", flush=True)

        # 3. Execute Clone into temp dir
        result = subprocess.run(
            ["git", "clone", "--depth", "1", auth_url, "."],
            cwd=temp_clone_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"[WORKSPACE] Clone exit code: {result.returncode}", flush=True)
        if result.stdout: print(f"[WORKSPACE] stdout: {result.stdout[:200]}", flush=True)
        if result.stderr: print(f"[WORKSPACE] stderr: {result.stderr[:200]}", flush=True)

        if result.returncode != 0:
            err = result.stderr.strip()
            print(f"[WORKSPACE] Depth clone failed, trying full clone...", flush=True)
            # Try without depth 1
            result = subprocess.run(["git", "clone", auth_url, "."], cwd=temp_clone_dir, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                 print(f"[WORKSPACE] Full clone also failed: {result.stderr[:200]}", flush=True)
                 return False, f"Git Error: {result.stderr.strip()}"
        
        # 4. Move temp to Workspace Root
        if os.path.exists(WORKSPACE_ROOT):
            _force_delete(WORKSPACE_ROOT)
        
        # Move everything from temp to root
        os.makedirs(WORKSPACE_ROOT, exist_ok=True)
        for item in os.listdir(temp_clone_dir):
            shutil.move(os.path.join(temp_clone_dir, item), os.path.join(WORKSPACE_ROOT, item))
            
        # 5. Cleanup temp
        _force_delete(temp_clone_dir)
        
        # 6. Configure Identity
        subprocess.run(["git", "config", "user.email", "agent@ascent.ai"], cwd=WORKSPACE_ROOT)
        subprocess.run(["git", "config", "user.name", "AgentExecutor"], cwd=WORKSPACE_ROOT)
        
        return True, "Success"
    except Exception as e:
        return False, str(e)

def pull_from_remote(token: str = None, branch: str = "main") -> Tuple[bool, str]:
    """Pull latest changes from remote repository"""
    if not os.path.exists(os.path.join(WORKSPACE_ROOT, ".git")):
        return False, "Workspace is not a git repository"

    if token:
        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
        if res.returncode == 0:
            current_url = res.stdout.strip()
            if "github.com" in current_url:
                clean_url = current_url
                if "@" in clean_url:
                    clean_url = "https://" + clean_url.split("@")[1]
                auth_url = clean_url.replace("https://", f"https://{token}@")
                subprocess.run(["git", "remote", "set-url", "origin", auth_url], cwd=WORKSPACE_ROOT, check=True)

    result = subprocess.run(["git", "pull", "origin", branch], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return False, f"Pull failed: {result.stderr.strip()}"
    return True, "Pull successful"


def push_to_github(branch_name: str, token: str = None) -> bool:
    """Actually push to GitHub if token is provided"""
    if not token:
        print("Push skipped: missing GitHub token")
        return False
        
    try:
        if not os.path.exists(os.path.join(WORKSPACE_ROOT, ".git")):
            print("Push failed: workspace is not a git repository")
            return False

        # Ensure remote has token
        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
        if res.returncode == 0:
            current_url = res.stdout.strip()
            if "github.com" in current_url and "@" not in current_url:
                auth_url = current_url.replace("https://", f"https://{token}@")
                subprocess.run(["git", "remote", "set-url", "origin", auth_url], cwd=WORKSPACE_ROOT, check=True)

        # Force push branch
        result = subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            # Try with -f if it failed (already exists or conflicts)
            fallback = subprocess.run(["git", "push", "-f", "origin", branch_name], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
            if fallback.returncode != 0:
                print(f"Push failed: {fallback.stderr.strip()}")
                return False
            
        return True
    except Exception as e:
        print(f"Push failed: {e}")
        return False

def write_to_workspace(file_path: str, content: str):
    """Write a file and its directory structure"""
    full_path = os.path.join(WORKSPACE_ROOT, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return full_path

def get_workspace_files():
    """Get a list of all files in the workspace"""
    files = []
    if not os.path.exists(WORKSPACE_ROOT):
        return []
        
    for root, _, filenames in os.walk(WORKSPACE_ROOT):
        if ".git" in root: continue
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), WORKSPACE_ROOT)
            files.append(rel_path.replace("\\", "/"))
    return files
