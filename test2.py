import subprocess
import os
import json
from pathlib import Path

def analyze_file_changes(base_branch: str = "master", include_diff: bool = True, max_diff_lines: int = 500,) -> str:
    """Get the full diff and list of changed files in the current git repository.
    
    Args:
        base_branch: Base branch to compare against (default: origin)
        include_diff: Include the full diff content (default: true)
        max_diff_lines: Maximum number of diff lines to include (default: 500)
    """
    cwd = str(Path(__file__).parent) # current directory
    print(cwd)
    # Get list of changed files
    files_result = subprocess.run(
        ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=cwd
    )
    
    # Get diff statistics
    stat_result = subprocess.run(
        ["git", "diff", "--stat", f"{base_branch}...HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd
    )

    # Get the actual diff if requested
    diff_content = ""
    truncated = False
    if include_diff:
        diff_result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            cwd=cwd
        )
        diff_lines = diff_result.stdout.split('\n')
                    
        # Check if we need to truncate
        if len(diff_lines) > max_diff_lines:
            diff_content = '\n'.join(diff_lines[:max_diff_lines])
            diff_content += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_content += "\n... Use max_diff_lines parameter to see more ..."
            truncated = True
        else:
            diff_content = diff_result.stdout

    # Get commit messages for context
    commits_result = subprocess.run(
        ["git", "log", "--oneline", f"{base_branch}..HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd
    )
    
    analysis = {
        "base_branch": base_branch,
        "files_changed": files_result.stdout,
        "statistics": stat_result.stdout,
        "commits": commits_result.stdout,
        "diff": diff_content if include_diff else "Diff not included (set include_diff=true to see full diff)",
        "truncated": truncated,
        "total_diff_lines": len(diff_lines) if include_diff else 0,
    }
    
    return json.dumps(analysis, indent=2)

res = analyze_file_changes()
print(res)