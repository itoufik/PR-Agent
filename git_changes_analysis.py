import subprocess
import os
import json
from pathlib import Path

# PR template directory (shared between starter and solution)
TEMPLATES_DIR = Path(__file__).parent/ "templates"

# Default PR templates
DEFAULT_TEMPLATES = {
    "bug.md": "Bug Fix",
    "feature.md": "Feature",
    "docs.md": "Documentation",
    "refactor.md": "Refactor",
    "test.md": "Test",
    "performance.md": "Performance",
    "security.md": "Security"
}

# Type mapping for PR templates
TYPE_MAPPING = {
    "bug": "bug.md",
    "fix": "bug.md",
    "feature": "feature.md",
    "enhancement": "feature.md",
    "docs": "docs.md",
    "documentation": "docs.md",
    "refactor": "refactor.md",
    "cleanup": "refactor.md",
    "test": "test.md",
    "testing": "test.md",
    "performance": "performance.md",
    "optimization": "performance.md",
    "security": "security.md"
}

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

def get_pr_templates() -> str:
    """List available PR templates with their content."""
    templates = [
        {
            "filename": filename,
            "type": template_type,
            "content": (TEMPLATES_DIR / filename).read_text()
        }
        for filename, template_type in DEFAULT_TEMPLATES.items()
    ]
    
    return json.dumps(templates, indent=2)

def summerize_change():
    # This will take all the output of analyse file change and the output change summary and change type
    # TODO
    pass

def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template.
    
    Args:
        changes_summary: Your analysis of what the changes do
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
    """
    
    # Get available templates
    templates_response = get_pr_templates()
    templates = json.loads(templates_response)
    
    # Find matching template
    template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
    selected_template = next(
        (t for t in templates if t["filename"] == template_file),
        templates[0]  # Default to first template if no match
    )
    
    suggestion = {
        "recommended_template": selected_template,
        "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
        "template_content": selected_template["content"],
        "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR."
    }
    
    return json.dumps(suggestion, indent=2)

if __name__ =="__main__":
    res = analyze_file_changes()
    print(res)