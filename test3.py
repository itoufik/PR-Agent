# async def analyze_file_changes(
#     base_branch: str = "main",
#     include_diff: bool = True,
#     max_diff_lines: int = 500,
#     working_directory: Optional[str] = None
# ) -> str:
#     """Get the full diff and list of changed files in the current git repository.
    
#     Args:
#         base_branch: Base branch to compare against (default: main)
#         include_diff: Include the full diff content (default: true)
#         max_diff_lines: Maximum number of diff lines to include (default: 500)
#         working_directory: Directory to run git commands in (default: current directory)
#     """
#     try:
#         # Try to get working directory from roots first
#         if working_directory is None:
#             try:
#                 context = mcp.get_context()
#                 roots_result = await context.session.list_roots()
#                 # Get the first root - Claude Code sets this to the CWD
#                 root = roots_result.roots[0]
#                 # FileUrl object has a .path property that gives us the path directly
#                 working_directory = root.uri.path
#             except Exception:
#                 # If we can't get roots, fall back to current directory
#                 pass
        
#         # Use provided working directory or current directory
#         cwd = working_directory if working_directory else os.getcwd()
        
#         # Debug output
#         debug_info = {
#             "provided_working_directory": working_directory,
#             "actual_cwd": cwd,
#             "server_process_cwd": os.getcwd(),
#             "server_file_location": str(Path(__file__).parent),
#             "roots_check": None
#         }
        
#         # Add roots debug info
#         try:
#             context = mcp.get_context()
#             roots_result = await context.session.list_roots()
#             debug_info["roots_check"] = {
#                 "found": True,
#                 "count": len(roots_result.roots),
#                 "roots": [str(root.uri) for root in roots_result.roots]
#             }
#         except Exception as e:
#             debug_info["roots_check"] = {
#                 "found": False,
#                 "error": str(e)
#             }
        
#         # Get list of changed files
#         files_result = subprocess.run(
#             ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
#             capture_output=True,
#             text=True,
#             check=True,
#             cwd=cwd
#         )
        
#         # Get diff statistics
#         stat_result = subprocess.run(
#             ["git", "diff", "--stat", f"{base_branch}...HEAD"],
#             capture_output=True,
#             text=True,
#             cwd=cwd
#         )
        
#         # Get the actual diff if requested
#         diff_content = ""
#         truncated = False
#         if include_diff:
#             diff_result = subprocess.run(
#                 ["git", "diff", f"{base_branch}...HEAD"],
#                 capture_output=True,
#                 text=True,
#                 cwd=cwd
#             )
#             diff_lines = diff_result.stdout.split('\n')
            
#             # Check if we need to truncate
#             if len(diff_lines) > max_diff_lines:
#                 diff_content = '\n'.join(diff_lines[:max_diff_lines])
#                 diff_content += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
#                 diff_content += "\n... Use max_diff_lines parameter to see more ..."
#                 truncated = True
#             else:
#                 diff_content = diff_result.stdout
        
#         # Get commit messages for context
#         commits_result = subprocess.run(
#             ["git", "log", "--oneline", f"{base_branch}..HEAD"],
#             capture_output=True,
#             text=True,
#             cwd=cwd
#         )
        
#         analysis = {
#             "base_branch": base_branch,
#             "files_changed": files_result.stdout,
#             "statistics": stat_result.stdout,
#             "commits": commits_result.stdout,
#             "diff": diff_content if include_diff else "Diff not included (set include_diff=true to see full diff)",
#             "truncated": truncated,
#             "total_diff_lines": len(diff_lines) if include_diff else 0,
#             "_debug": debug_info
#         }
        
#         return json.dumps(analysis, indent=2)