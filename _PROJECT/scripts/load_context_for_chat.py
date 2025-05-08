#!/usr/bin/env python3
"""
Context Loader for AI Chat Sessions

This script prepares the PROJECT_CONTEXT.md file and recent decision logs
for easy attachment to AI chat sessions.
"""
import os
import re
import json
import datetime
import argparse
import sys
from pathlib import Path

def load_context_for_chat(include_decisions=True, include_blueprints=True, 
                          output_file=None, max_tokens=8000):
    """
    Prepare project context for AI chat sessions.
    
    Args:
        include_decisions: Whether to include recent decisions
        include_blueprints: Whether to include active blueprint summaries
        output_file: Output file path, if None outputs to console
        max_tokens: Maximum approximate tokens to include
        
    Returns:
        str: Formatted context content
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # Load PROJECT_CONTEXT.md
    context_file = os.path.join(project_dir, "PROJECT_CONTEXT.md")
    if not os.path.exists(context_file):
        print(f"Error: {context_file} not found")
        return None
    
    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()
    
    # Collect the sections we want to include
    sections = []
    
    # Add the header section (metadata, overview)
    header_end = context_content.find("## 1.")
    if header_end > 0:
        header = context_content[:header_end].strip()
        sections.append(("Header", header))
    
    # Add current focus section
    focus_start = context_content.find("## 1. Current Focus")
    if focus_start > 0:
        next_section = context_content.find("## 2.", focus_start)
        if next_section > 0:
            focus = context_content[focus_start:next_section].strip()
            sections.append(("Current Focus", focus))
    
    # Add agent profile section
    agent_start = context_content.find("## 2. Agent Profile")
    if agent_start > 0:
        next_section = context_content.find("## 3.", agent_start)
        if next_section > 0:
            agent = context_content[agent_start:next_section].strip()
            sections.append(("Agent Profile", agent))
    
    # Add project scope section
    scope_start = context_content.find("## 3. Project Scope")
    if scope_start > 0:
        next_section = context_content.find("## 4.", scope_start)
        if next_section > 0:
            scope = context_content[scope_start:next_section].strip()
            sections.append(("Project Scope", scope))
    
    # Add architecture section
    arch_start = context_content.find("## 4. System Architecture")
    if arch_start > 0:
        next_section = context_content.find("## 5.", arch_start)
        if next_section > 0:
            arch = context_content[arch_start:next_section].strip()
            sections.append(("System Architecture", arch))
    
    # Add decision log if requested
    if include_decisions:
        decision_start = context_content.find("## 12. Decision Log")
        if decision_start > 0:
            decisions = context_content[decision_start:].strip()
            sections.append(("Decision Log", decisions))
        
        # Also check for separate decisions log file
        decisions_file = os.path.join(project_dir, "DECISIONS_LOG.md")
        if os.path.exists(decisions_file):
            with open(decisions_file, "r", encoding="utf-8") as f:
                decisions_content = f.read()
                
            # Extract the most recent decisions (first 5)
            decisions_table_start = decisions_content.find("| Date | Component | Decision | Rationale |")
            if decisions_table_start > 0:
                table_start = decisions_content.find("|---", decisions_table_start)
                if table_start > 0:
                    rows_start = decisions_content.find("\n|", table_start)
                    if rows_start > 0:
                        # Get the first 5 rows
                        lines = decisions_content[rows_start:].strip().split("\n")
                        recent_decisions = "\n".join(lines[:6])  # Header + 5 rows
                        sections.append(("Recent Decisions", 
                                        "## Recent Architectural Decisions\n\n" + recent_decisions))
    
    # Add blueprint summaries if requested
    if include_blueprints:
        blueprints_dir = os.path.join(project_dir, "_BMPRSS/_BLUEPRINTS")
        if os.path.exists(blueprints_dir):
            blueprint_files = list(Path(blueprints_dir).glob("**/*.md"))
            
            if blueprint_files:
                recent_blueprints = sorted(
                    blueprint_files, 
                    key=os.path.getmtime, 
                    reverse=True
                )[:3]  # Get 3 most recent blueprints
                
                blueprint_summaries = ["## Active Blueprints\n"]
                
                for bp_file in recent_blueprints:
                    with open(bp_file, "r", encoding="utf-8") as f:
                        bp_content = f.read()
                    
                    # Extract title and overview
                    title_match = re.search(r'^# (.+)$', bp_content, re.MULTILINE)
                    title = title_match.group(1) if title_match else os.path.basename(bp_file)
                    
                    # Extract overview section
                    overview = ""
                    overview_start = bp_content.find("## Overview")
                    if overview_start > 0:
                        next_section = re.search(r'^## ', bp_content[overview_start+10:], re.MULTILINE)
                        if next_section:
                            end_pos = overview_start + 10 + next_section.start()
                            overview = bp_content[overview_start:end_pos].strip()
                        else:
                            overview = bp_content[overview_start:].strip()
                    
                    if not overview:
                        # Just take the first 300 characters after the title
                        first_section = re.search(r'^## ', bp_content, re.MULTILINE)
                        if first_section:
                            overview = bp_content[first_section.start():first_section.start()+300].strip()
                        else:
                            overview = bp_content[:300].strip()
                    
                    blueprint_summaries.append(f"### {title}\n\n{overview}\n")
                
                sections.append(("Blueprints", "\n\n".join(blueprint_summaries)))
    
    # Create final context content with all sections
    final_content = []
    token_estimate = 0
    
    for section_name, section_content in sections:
        # Estimate tokens (rough approximation: 4 chars ≈ 1 token)
        section_tokens = len(section_content) // 4
        
        if token_estimate + section_tokens > max_tokens:
            # Don't add this section if it would exceed the max tokens
            print(f"Skipping {section_name} section to stay within token limit")
            continue
            
        final_content.append(section_content)
        token_estimate += section_tokens
    
    combined_content = "\n\n---\n\n".join(final_content)
    
    # Add a note about tokenization
    note = f"\n\n<!-- Approximate token count: {token_estimate} -->"
    combined_content += note
    
    # Write to file or output to console
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined_content)
        print(f"Context written to {output_file}")
    else:
        print("\n" + "="*80)
        print("PROJECT CONTEXT FOR CHAT SESSION")
        print("="*80 + "\n")
        print(combined_content)
    
    return combined_content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load project context for AI chat sessions")
    parser.add_argument("--no-decisions", action="store_false", dest="include_decisions",
                      help="Exclude decision logs")
    parser.add_argument("--no-blueprints", action="store_false", dest="include_blueprints",
                      help="Exclude blueprint summaries")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--max-tokens", "-m", type=int, default=8000,
                      help="Maximum approximate tokens to include")
    args = parser.parse_args()
    
    content = load_context_for_chat(
        include_decisions=args.include_decisions,
        include_blueprints=args.include_blueprints,
        output_file=args.output,
        max_tokens=args.max_tokens
    )
    
    if content is None:
        sys.exit(1) 