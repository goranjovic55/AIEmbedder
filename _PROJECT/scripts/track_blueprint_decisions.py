#!/usr/bin/env python3
"""
Blueprint Decision Tracker

Compares original blueprint documents with current implementation
to identify and track architectural decisions and changes.
"""

import os
import re
import json
import datetime
import argparse
import difflib
import glob

def track_blueprint_decisions(blueprints_dir="_BMPRSS/_BLUEPRINTS", 
                             output_file="../DECISIONS_LOG.md"):
    """
    Compare blueprint documents with current implementation to track decisions.
    
    Args:
        blueprints_dir: Directory containing blueprints
        output_file: Output file for decisions log
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Make paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # _PROJECT directory
    workspace_root = os.path.dirname(project_root)  # Workspace root
    
    blueprints_full_path = os.path.join(project_root, blueprints_dir)
    output_full_path = os.path.join(project_root, output_file)
    
    if not os.path.exists(blueprints_full_path):
        print(f"Error: Blueprints directory '{blueprints_full_path}' not found")
        print("Create _PROJECT/_BMPRSS/_BLUEPRINTS with your blueprint documents first")
        return False
        
    print(f"Analyzing blueprints in {blueprints_full_path}...")
    
    # Track current decisions
    decisions = []
    
    # Load existing decisions if available
    existing_decisions = []
    if os.path.exists(output_full_path):
        with open(output_full_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract decisions from MD table format
            table_pattern = r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|'
            matches = re.findall(table_pattern, content)
            for match in matches:
                if len(match) >= 4:
                    existing_decisions.append({
                        "date": match[0],
                        "component": match[1],
                        "decision": match[2],
                        "rationale": match[3]
                    })
    
    # Find all blueprint files
    blueprint_files = []
    for ext in ["*.md", "*.txt", "*.json"]:
        blueprint_files.extend(glob.glob(os.path.join(blueprints_full_path, "**", ext), recursive=True))
    
    print(f"Found {len(blueprint_files)} blueprint files")
    
    # Compare blueprints with current implementation
    for blueprint_file in blueprint_files:
        relative_path = os.path.relpath(blueprint_file, blueprints_full_path)
        print(f"Analyzing {relative_path}...")
        
        with open(blueprint_file, "r", encoding="utf-8") as f:
            blueprint_content = f.read()
        
        # Extract planned components and architecture from blueprint
        components = extract_components_from_blueprint(blueprint_content)
        
        for component in components:
            # Check if component exists in implementation
            implemented_path = component.get("path")
            if implemented_path:
                # Convert to full path relative to workspace
                full_path = os.path.join(workspace_root, implemented_path)
                if os.path.exists(full_path):
                    # Component exists, check for differences
                    with open(full_path, "r", encoding="utf-8") as f:
                        implemented_content = f.read()
                    
                    changes = compare_blueprint_vs_implementation(
                        component, 
                        blueprint_content, 
                        implemented_content
                    )
                    
                    for change in changes:
                        # Check if this decision is already tracked
                        is_new = True
                        for existing in existing_decisions:
                            if (existing["component"] == change["component"] and
                                existing["decision"] == change["decision"]):
                                is_new = False
                                break
                        
                        if is_new:
                            change["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
                            decisions.append(change)
                else:
                    # Check if planned component was removed/renamed
                    print(f"  Warning: Planned component {component.get('name')} not found at {full_path}")
                    # Add a record about missing component if it's not just a directory
                    if not implemented_path.endswith('/'):
                        decisions.append({
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "component": component.get("name", "Unknown"),
                            "decision": f"Component planned at {implemented_path} not implemented",
                            "rationale": "Decision needed: Intentionally removed or moved elsewhere?"
                        })
    
    # Also scan for new components not in blueprints
    new_components = find_new_components(workspace_root, components)
    for component in new_components:
        decisions.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "component": component["name"],
            "decision": f"Added component not in original blueprints: {component['path']}",
            "rationale": "Decision needed: Document rationale for this addition"
        })
    
    # Generate decisions log
    all_decisions = existing_decisions + decisions
    
    # Sort by date (newest first)
    all_decisions.sort(key=lambda x: x["date"], reverse=True)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_full_path), exist_ok=True)
    
    # Write to output file
    with open(output_full_path, "w", encoding="utf-8") as f:
        f.write(f"# Project Architectural Decisions Log\n\n")
        f.write(f"**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("This document tracks significant architectural decisions made during implementation\n")
        f.write("that differ from the original blueprints.\n\n")
        
        f.write("| Date | Component | Decision | Rationale |\n")
        f.write("|------|-----------|----------|------------|\n")
        
        for decision in all_decisions:
            f.write(f"| {decision['date']} | {decision['component']} | {decision['decision']} | {decision['rationale']} |\n")
    
    print(f"Found {len(decisions)} new decisions")
    print(f"Decisions log written to {output_full_path}")
    print("Review the log and update the 'Rationale' column for new entries")
    
    # Update PROJECT_CONTEXT.md with decision log reference
    update_project_context_with_decisions(all_decisions)
    
    return True

def extract_components_from_blueprint(content):
    """
    Extract planned components from blueprint document.
    
    Returns:
        list: List of component dictionaries
    """
    components = []
    
    # Try to extract from JSON blocks first
    json_blocks = re.findall(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    for json_block in json_blocks:
        try:
            data = json.loads(json_block)
            if isinstance(data, dict):
                # Check if this is a component definition
                if "components" in data:
                    for comp in data["components"]:
                        components.append(comp)
                elif "name" in data and "path" in data:
                    components.append(data)
                elif "COMPONENTS" in data:
                    for name, comp in data["COMPONENTS"].items():
                        comp["name"] = name
                        components.append(comp)
        except json.JSONDecodeError:
            pass
    
    # Try to extract from headings and code blocks
    component_section = False
    current_component = {}
    
    for line in content.split('\n'):
        # Check for component section headings
        if re.match(r'#+\s*Components?|Modules?|Structure', line, re.IGNORECASE):
            component_section = True
            continue
        
        if component_section:
            # Look for component name and path in various formats
            comp_match = re.match(r'#+\s*([\w\-\.]+)\s*', line)
            if comp_match:
                if current_component and "name" in current_component:
                    components.append(current_component)
                current_component = {"name": comp_match.group(1)}
                continue
            
            # Look for path definitions
            path_match = re.search(r'(path|file|location):\s*[\'"]?([\w\-\.\/]+)[\'"]?', line, re.IGNORECASE)
            if path_match and current_component:
                current_component["path"] = path_match.group(2)
            
            # Check for Python import style paths
            if "->" in line or ":" in line:
                parts = re.split(r'\s*(?:->|:)\s*', line)
                if len(parts) >= 2:
                    if current_component and "name" in current_component:
                        components.append(current_component)
                    name = parts[0].strip()
                    path = parts[1].strip().strip("'\"")
                    current_component = {"name": name, "path": path}
    
    # Add the last component if not added
    if current_component and "name" in current_component:
        components.append(current_component)
    
    return components

def compare_blueprint_vs_implementation(component, blueprint_content, implemented_content):
    """
    Compare blueprint with implementation to identify changes.
    
    Returns:
        list: List of change dictionaries
    """
    changes = []
    component_name = component.get("name", "Unknown")
    
    # Check for implementation comments indicating changes
    decision_comments = re.findall(
        r'(?:\/\/|#)\s*DECISION:\s*(.*?)(?:\n|$)', 
        implemented_content
    )
    
    for comment in decision_comments:
        changes.append({
            "component": component_name,
            "decision": comment.strip(),
            "rationale": "Documented in code"
        })
    
    # Check for significant structural changes
    # This is a simplistic diff - could be enhanced for specific languages
    if len(changes) == 0:
        blueprint_snippets = extract_code_snippets(blueprint_content)
        
        for snippet in blueprint_snippets:
            if len(snippet) > 10:  # Ignore very short snippets
                # See if this snippet appears in implementation
                similarity = difflib.SequenceMatcher(
                    None, snippet, implemented_content
                ).ratio()
                
                if similarity < 0.7:  # Less than 70% similar
                    # Extract function names from blueprint
                    bp_functions = re.findall(r'(?:def|function)\s+(\w+)', snippet)
                    # Check if these functions exist in implementation
                    for func in bp_functions:
                        if func not in implemented_content:
                            changes.append({
                                "component": component_name,
                                "decision": f"Function '{func}' from blueprint not implemented",
                                "rationale": "Decision needed"
                            })
    
    return changes

def extract_code_snippets(content):
    """Extract code snippets from markdown."""
    snippets = []
    in_snippet = False
    current_snippet = []
    
    for line in content.split('\n'):
        if line.startswith('```'):
            if in_snippet:
                in_snippet = False
                if current_snippet:
                    snippets.append('\n'.join(current_snippet))
                    current_snippet = []
            else:
                in_snippet = True
        elif in_snippet:
            current_snippet.append(line)
    
    return snippets

def find_new_components(workspace_root, planned_components):
    """Find components in implementation not in blueprints."""
    new_components = []
    planned_paths = [c.get("path") for c in planned_components if "path" in c]
    
    # Check typical code directories
    code_dirs = ["src", "app", "lib", "components", "modules"]
    
    for code_dir in code_dirs:
        full_dir = os.path.join(workspace_root, code_dir)
        if os.path.exists(full_dir) and os.path.isdir(full_dir):
            for root, dirs, files in os.walk(full_dir):
                for file in files:
                    if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.c', '.cpp', '.h')):
                        # Get path relative to workspace root 
                        path = os.path.relpath(os.path.join(root, file), workspace_root)
                        if path not in planned_paths:
                            # Check if this path is covered by any parent dir in planned_paths
                            parent_planned = any(path.startswith(p) for p in planned_paths if p.endswith('/'))
                            if not parent_planned:
                                new_components.append({
                                    "name": os.path.splitext(file)[0],
                                    "path": path
                                })
    
    return new_components

def update_project_context_with_decisions(decisions):
    """
    Update PROJECT_CONTEXT.md to reference the decisions log.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    context_file = os.path.join(project_root, "PROJECT_CONTEXT.md")
    
    if not os.path.exists(context_file):
        return False
    
    try:
        with open(context_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find decision log section or create one
        decisions_section = content.find("## 12. Decision Log")
        
        if decisions_section > 0:
            # Section exists, check if table needs updating
            table_start = content.find("|", decisions_section)
            table_end = content.find("##", table_start)
            if table_end < 0:  # If it's the last section
                table_end = len(content)
            
            # Get recent decisions for the context
            recent_decisions = decisions[:5]  # Top 5 most recent
            
            # Create updated table
            decision_table = "| Date | Decision | Rationale | Alternatives Considered |\n"
            decision_table += "|------|----------|-----------|------------------------|\n"
            
            for decision in recent_decisions:
                decision_table += f"| {decision['date']} | {decision['decision']} | {decision['rationale']} | See DECISIONS_LOG.md |\n"
            
            # Replace the existing table
            updated_content = content[:table_start] + decision_table
            
            if table_end < len(content):
                updated_content += content[table_end:]
            
            # Write updated content
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            print(f"Updated decision log in {context_file}")
            return True
        else:
            # Section doesn't exist, check if we should add it
            print("Decision Log section not found in PROJECT_CONTEXT.md")
            print("Consider adding a '## 12. Decision Log' section")
            return False
    except Exception as e:
        print(f"Error updating PROJECT_CONTEXT.md: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track architectural decisions vs blueprints")
    parser.add_argument("--blueprints", "-b", 
                      default="_BMPRSS/_BLUEPRINTS",
                      help="Directory containing blueprint documents relative to _PROJECT")
    parser.add_argument("--output", "-o", 
                      default="../DECISIONS_LOG.md",
                      help="Output file for decisions log relative to scripts directory")
    args = parser.parse_args()
    
    track_blueprint_decisions(args.blueprints, args.output) 