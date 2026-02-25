#!/usr/bin/env python3
"""
Changelog Manager Script for todo-manager skill

Usage:
    python scripts/changelog_manager.py --action add_entry --file CHANGELOG.md --task-title "Task Title" --completed "Description of work"
    python scripts/changelog_manager.py --action add_verified --file CHANGELOG.md --task-title "Task Title"
"""

import argparse
import os
from datetime import datetime

def get_timestamp() -> str:
    """Get current timestamp for changelog"""
    return datetime.utcnow().strftime("%Y-%m-%d")

def add_changelog_entry(filepath: str, task_title: str, completed: str, notes: str = None) -> bool:
    """Add a new entry to CHANGELOG.md following Common Changelog format"""
    timestamp = get_timestamp()
    
    # Build the entry
    entry = f"## {timestamp} - Task: {task_title}\n\n"
    entry += f"### Completed\n- {completed}\n"
    
    if notes:
        entry += f"\n### Notes\n- {notes}\n"
    
    entry += "\n---\n\n"
    
    # Read existing content
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find the position after the first "---" and before existing entries
        separator_pos = content.find('---')
        if separator_pos != -1:
            # Insert after the separator
            insert_pos = content.find('\n', separator_pos) + 1
            new_content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
        else:
            new_content = entry + content
    else:
        # Create new file
        new_content = f"# Changelog\n\nAll notable changes to this project will be documented in this file.\n\nThe format is based on [Common Changelog](https://commonform.github.io/changelog/).\n\n---\n\n{entry}"
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def add_verified_entry(filepath: str, task_title: str, original_notes: str = None) -> bool:
    """Add a verified entry to CHANGELOG.md"""
    timestamp = get_timestamp()
    
    entry = f"## {timestamp} - Task: {task_title} - VERIFIED\n\n"
    
    if original_notes:
        entry += f"### Completed\n- {original_notes}\n\n"
    
    entry += "### Verified\n- Quality check passed\n\n---\n\n"
    
    # Read existing content
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        separator_pos = content.find('---')
        if separator_pos != -1:
            insert_pos = content.find('\n', separator_pos) + 1
            new_content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
        else:
            new_content = entry + content
    else:
        new_content = f"# Changelog\n\n---\n\n{entry}"
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Changelog Manager Script')
    parser.add_argument('--action', required=True,
                        choices=['add_entry', 'add_verified'],
                        help='Action to perform')
    parser.add_argument('--file', default='CHANGELOG.md', help='Path to changelog file')
    parser.add_argument('--task-title', required=True, help='Title of the task')
    parser.add_argument('--completed', help='Description of what was completed')
    parser.add_argument('--notes', help='Additional notes')
    
    args = parser.parse_args()
    
    if args.action == 'add_entry':
        if add_changelog_entry(args.file, args.task_title, args.completed or "", args.notes):
            print(f"Added changelog entry for: {args.task_title}")
        else:
            print("Failed to add entry")
    
    elif args.action == 'add_verified':
        if add_verified_entry(args.file, args.task_title, args.notes):
            print(f"Added verified entry for: {args.task_title}")
        else:
            print("Failed to add verified entry")

if __name__ == '__main__':
    main()
