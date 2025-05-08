#!/usr/bin/env python3
"""
Update TSKMaster Project Context

This script updates the TSKMaster_CONTEXT.md file based on the latest project state.
"""

import os
import re
import json
import datetime
import argparse
import sys
from pathlib import Path

def update_project_context(update_level="standard", force=False):
    """
    Update the project context file with the latest information.
    
    Args:
        update_level: "minimal", "standard", or "deep"
        force: If True, update even if no changes detected
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    workspace_root = os.path.dirname(project_dir)
    
    context_file = os.path.join(project_dir, "TSKMaster_CONTEXT.md")
    if not os.path.exists(context_file):
        print(f"Error: {context_file} not found")
        return False
        
    print(f"Updating project context (level: {update_level})")
    
    # Load the content
    with open(context_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # First update the last updated date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    updated_content = re.sub(
        r'\*\*Last Updated: .+\*\*',
        f'**Last Updated: {today}**',
        content
    )
    
    # Update specific sections based on update level
    if update_level == "minimal":
        # Only update Project Focus and Agent Profile
        updated_content = update_current_focus(updated_content, project_dir)
        updated_content = update_agent_profile(updated_content)
    elif update_level == "standard":
        # Update all main sections
        updated_content = update_current_focus(updated_content, project_dir)
        updated_content = update_agent_profile(updated_content)
        updated_content = update_component_status(updated_content, workspace_root)
        updated_content = update_known_issues(updated_content, project_dir)
    elif update_level == "deep":
        # Deep scan of all project files and reconciliation
        updated_content = update_current_focus(updated_content, project_dir)
        updated_content = update_agent_profile(updated_content)
        updated_content = update_component_status(updated_content, workspace_root)
        updated_content = update_known_issues(updated_content, project_dir)
        updated_content = update_code_patterns(updated_content, workspace_root)
    
    # Check if any changes were made
    if updated_content == content and not force:
        print("No changes detected in project context")
        return True
    
    # Write the updated content
    with open(context_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    # Also update the main PROJECT_CONTEXT.md
    main_context_file = os.path.join(project_dir, "PROJECT_CONTEXT.md")
    with open(main_context_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print("Project context updated successfully")
    return True

def update_current_focus(content, project_dir):
    """Update the current focus section based on recent changes."""
    focus_start = content.find("## 2. Project Focus")
    if focus_start < 0:
        return content
    
    focus_end = content.find("## 3.", focus_start)
    if focus_end < 0:
        return content
    
    # Keep the existing focus content for now - in a more advanced version,
    # we could scan for recent changes in the codebase to update the focus
    
    return content

def update_agent_profile(content):
    """Update the agent profile section with recent changes."""
    agent_start = content.find("## 3. Agent Profile")
    if agent_start < 0:
        return content
    
    agent_end = content.find("## 4.", agent_start)
    if agent_end < 0:
        return content
    
    # Update the session start date to today
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    updated_agent_content = re.sub(
        r'Session Start: [0-9]{4}-[0-9]{2}-[0-9]{2}',
        f'Session Start: {today}',
        content[agent_start:agent_end]
    )
    
    # Replace the agent section in the content
    updated_content = content[:agent_start] + updated_agent_content + content[agent_end:]
    return updated_content

def update_component_status(content, workspace_root):
    """Update component status based on latest code state."""
    component_start = content.find("## 7. Implementation Status")
    if component_start < 0:
        return content
    
    component_end = content.find("## 8.", component_start)
    if component_end < 0:
        return content
    
    # This is where we'd add more sophisticated code scanning
    # For now, just keep the existing content
    
    return content

def update_known_issues(content, project_dir):
    """Update known issues section with latest information."""
    issues_start = content.find("## 8. Known Issues")
    if issues_start < 0:
        return content
    
    issues_end = content.find("## 9.", issues_start)
    if issues_end < 0:
        return content
    
    # This is where we'd scan issue tracking or update based on recent changes
    # For now, just keep the existing content
    
    return content

def update_code_patterns(content, workspace_root):
    """Update code patterns section with latest examples from codebase."""
    patterns_start = content.find("## 9. Code Patterns")
    if patterns_start < 0:
        return content
    
    patterns_end = content.find("## 10.", patterns_start)
    if patterns_end < 0:
        return content
    
    # This is where we'd scan the codebase to find updated patterns
    # For now, just keep the existing content
    
    return content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update TSKMaster project context")
    parser.add_argument("--level", choices=["minimal", "standard", "deep"], 
                      default="standard", help="Update level")
    parser.add_argument("--force", action="store_true", 
                      help="Force update even if no changes detected")
    args = parser.parse_args()
    
    if not update_project_context(args.level, args.force):
        sys.exit(1) 