import os
from typing import Dict

WORKSPACE_ROOT = os.path.join(os.getcwd(), "simulated_workspace")

def write_to_workspace(file_path: str, content: str):
    """Write a file to the simulated workspace"""
    full_path = os.path.join(WORKSPACE_ROOT, file_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return full_path

def get_workspace_files():
    """Get a list of all files in the workspace"""
    files = []
    for root, _, filenames in os.walk(WORKSPACE_ROOT):
        for filename in filenames:
            rel_dir = os.path.relpath(root, WORKSPACE_ROOT)
            rel_file = os.path.join(rel_dir, filename) if rel_dir != "." else filename
            files.append(rel_file)
    return files
