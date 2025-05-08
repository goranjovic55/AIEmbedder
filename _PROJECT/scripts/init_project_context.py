#!/usr/bin/env python3
"""
TSKMaster Project Context Initialization Script
Prepares the PROJECT_CONTEXT.md file structure for TSKMaster
"""
import os
import json
import datetime
import shutil
import argparse
import sys
import re

def initialize_project_context(project_name=None, force=False):
    """
    Initialize the project context system for TSKMaster.
    
    Args:
        project_name: Optional name for the project
        force: If True, overwrite existing metadata
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)  # _PROJECT directory
    
    # Check if PROJECT_CONTEXT.md exists
    context_file = os.path.join(project_dir, "TSKMaster_CONTEXT.md")
    if not os.path.exists(context_file):
        print(f"Error: {context_file} not found")
        print("Please ensure TSKMaster_CONTEXT.md template file exists in the _PROJECT directory")
        return False

    # Update the metadata section
    with open(context_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find metadata section
    meta_start = content.find("### Metadata")
    meta_json_start = content.find("```json", meta_start)
    meta_json_end = content.find("```", meta_json_start + 7)
    
    if meta_start > 0 and meta_json_start > 0 and meta_json_end > 0:
        # Extract current metadata
        metadata_str = content[meta_json_start+7:meta_json_end].strip()
        try:
            metadata = json.loads(metadata_str)
            
            # Check if already initialized and force not specified
            if "initialized_date" in metadata and metadata["initialized_date"] != "YYYY-MM-DD" and not force:
                print(f"Project context already initialized on {metadata['initialized_date']}")
                print("Use --force to reinitialize")
                return False
            
            # Update metadata
            metadata["initialized_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Get project name if not provided
            if not project_name:
                if "project_id" in metadata and metadata["project_id"] != "PROJECT_NAME":
                    project_name = metadata["project_id"]
                else:
                    project_name = input("Enter project name: ").strip()
            
            if project_name:
                metadata["project_id"] = project_name
            else:
                metadata["project_id"] = "TSKMaster"
                
            # Replace metadata in content
            new_metadata = json.dumps(metadata, indent=2)
            new_content = (
                content[:meta_json_start+7] + 
                "\n" + new_metadata + "\n" + 
                content[meta_json_end:]
            )
            
            # Update project name in title
            project_title_pattern = re.compile(r'^# (.+) Project Context', re.MULTILINE)
            new_content = project_title_pattern.sub(f'# {metadata["project_id"]} Project Context', new_content)
            
            # Update last updated date
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            new_content = new_content.replace(
                "**Last Updated: 2025-04-03**",
                f"**Last Updated: {today}**"
            )
            
            # Write updated content
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            # Also update the main PROJECT_CONTEXT.md file
            main_context_file = os.path.join(project_dir, "PROJECT_CONTEXT.md")
            with open(main_context_file, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print(f"Project context initialized for: {metadata['project_id']}")
            return True
        except json.JSONDecodeError as e:
            print(f"Error parsing metadata JSON: {e}")
            return False
    else:
        print("Could not locate metadata section in PROJECT_CONTEXT.md")
        return False

def setup_git_hooks():
    """Set up Git hooks for context maintenance."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    workspace_root = os.path.dirname(project_dir)
    hooks_dir = os.path.join(workspace_root, ".git/hooks")
    
    if not os.path.exists(os.path.join(workspace_root, ".git")):
        print("Warning: .git directory not found. Is this a Git repository?")
        return False
    
    os.makedirs(hooks_dir, exist_ok=True)
    
    # Copy pre-commit hook template
    pre_commit_content = """#!/bin/bash

# Check if key project files were modified
key_files_changed=$(git diff --cached --name-only | grep -E '(src/|app/|_PROJECT/|README.md)')

if [ -n "$key_files_changed" ]; then
  echo "Warning: You've modified key project files that may require updating PROJECT_CONTEXT.md:"
  echo "$key_files_changed"
  echo "Please consider updating _PROJECT/TSKMaster_CONTEXT.md to reflect these changes."
fi

exit 0
"""
    pre_commit_path = os.path.join(hooks_dir, "pre-commit")
    try:
        with open(pre_commit_path, "w") as f:
            f.write(pre_commit_content)
        
        # Make executable
        try:
            os.chmod(pre_commit_path, 0o755)
            print("Git hooks set up successfully")
            return True
        except:
            print("Warning: Could not set executable permission on Git hook")
            print(f"Please manually make the hook executable: chmod +x {pre_commit_path}")
            return False
    except Exception as e:
        print(f"Warning: Could not create Git hook: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize TSKMaster project context")
    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--force", action="store_true", help="Force reinitialization")
    args = parser.parse_args()
    
    success = initialize_project_context(project_name=args.project_name, force=args.force)
    if success:
        setup_git_hooks()
    else:
        sys.exit(1) 