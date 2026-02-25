#!/usr/bin/env python3
"""
Todo Parser Script for todo-manager skill

Usage:
    python scripts/todo_parser.py --action get_next_task --file .todo.md
    python scripts/todo_parser.py --action update_status --file .todo.md --task-id 1 --status "in progress"
    python scripts/todo_parser.py --action add_task --file .todo.md --title "New Task" --description "Task description"
    python scripts/todo_parser.py --action list_tasks --file .todo.md
    python scripts/todo_parser.py --action get_first_complete --file .todo.md
"""

import argparse
import re
import os
import json
from datetime import datetime
from typing import Optional, Dict, List

def get_timestamp() -> str:
    """Get current ISO timestamp"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_todo_file(filepath: str) -> Dict:
    """Parse .todo.md file and return structured data"""
    if not os.path.exists(filepath):
        return {"exists": False, "tasks": []}
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    result = {
        "exists": True,
        "raw": content,
        "project": None,
        "created": None,
        "last_updated": None,
        "tasks": []
    }
    
    # Parse project header
    project_match = re.search(r'## Project: (.+)', content)
    if project_match:
        result["project"] = project_match.group(1).strip()
    
    created_match = re.search(r'\*\*Created:\*\* (\S+)', content)
    if created_match:
        result["created"] = created_match.group(1)
    
    updated_match = re.search(r'\*\*Last Updated:\*\* (\S+)', content)
    if updated_match:
        result["last_updated"] = updated_match.group(1)
    
    # Parse tasks - split by task headers
    task_blocks = re.split(r'## Task \d+:', content)[1:]
    
    for idx, block in enumerate(task_blocks, 1):
        task = {"id": idx}
        
        # Title (everything before first metadata field)
        title_match = re.match(r'\s*(.+?)(?:\n|- \*\*Status)', block, re.DOTALL)
        if title_match:
            task["title"] = title_match.group(1).strip()
        
        # Status
        status_match = re.search(r'\*\*Status:\*\* (\S+)', block)
        if status_match:
            task["status"] = status_match.group(1).strip()
        
        # Description
        desc_match = re.search(r'\*\*Description:\*\* (.+?)(?:\n- \*\*|$)', block, re.DOTALL)
        if desc_match:
            task["description"] = desc_match.group(1).strip()
        
        # Notes
        notes_match = re.search(r'\*\*Notes:\*\* (.+)', block, re.DOTALL)
        if notes_match:
            task["notes"] = notes_match.group(1).strip()
        
        # Timestamps
        created_task_match = re.search(r'\*\*Created:\*\* (\S+)', block)
        if created_task_match:
            task["created"] = created_task_match.group(1)
        
        updated_task_match = re.search(r'\*\*Updated:\*\* (\S+)', block)
        if updated_task_match:
            task["updated"] = updated_task_match.group(1)
        
        result["tasks"].append(task)
    
    return result

def find_next_not_started_task(filepath: str) -> Optional[Dict]:
    """Find the first task with status 'not started'"""
    data = parse_todo_file(filepath)
    for task in data["tasks"]:
        if task.get("status") == "not started":
            return task
    return None

def find_first_complete_task(filepath: str) -> Optional[Dict]:
    """Find the first task with status 'complete'"""
    data = parse_todo_file(filepath)
    for task in data["tasks"]:
        if task.get("status") == "complete":
            return task
    return None

def update_task_status(filepath: str, task_id: int, status: str, notes: str = None) -> bool:
    """Update task status and optionally add notes"""
    data = parse_todo_file(filepath)
    if task_id < 1 or task_id > len(data["tasks"]):
        return False
    
    timestamp = get_timestamp()
    
    # Update content
    content = data["raw"]
    
    # Find and update the specific task block
    task_blocks = re.split(r'## Task \d+:', content)
    
    for idx in range(1, len(task_blocks)):
        if idx == task_id:
            block = task_blocks[idx]
            
            # Update status
            block = re.sub(
                r'(\*\*Status:\*\*)\s*\S+',
                rf'\1 {status}',
                block
            )
            
            # Update timestamp
            block = re.sub(
                r'(\*\*Updated:\*\*)\s*\S+',
                rf'\1 {timestamp}',
                block
            )
            
            # Add notes if provided
            if notes:
                if "**Notes:**" in block:
                    # Append to existing notes
                    block = re.sub(
                        r'(\*\*Notes:\*\*)(.+)',
                        rf'\1 \2\n- {notes}',
                        block,
                        flags=re.DOTALL
                    )
                else:
                    # Add notes field
                    block = block.rstrip() + f"\n- **Notes:** {notes}\n"
            
            task_blocks[idx] = block
            break
    
    # Update last updated
    new_content = '## Task '.join(task_blocks)
    new_content = re.sub(
        r'(\*\*Last Updated:\*\*)\s*\S+',
        rf'\1 {timestamp}',
        new_content
    )
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def add_task(filepath: str, title: str, description: str, insert_before: int = None) -> bool:
    """Add a new task to the todo file"""
    data = parse_todo_file(filepath)
    timestamp = get_timestamp()
    
    new_task_block = f"""## Task X: {title}
- **Status:** not started
- **Created:** {timestamp}
- **Updated:** {timestamp}
- **Description:** {description}
- **Notes:** 
"""
    
    content = data["raw"]
    
    if insert_before:
        # Insert before the specified task
        task_blocks = re.split(r'## Task \d+:', content)
        task_blocks.insert(insert_before, new_task_block.replace("Task X", f"Task {insert_before}"))
        
        # Renumber all tasks
        for i in range(1, len(task_blocks)):
            task_blocks[i] = re.sub(
                r'## Task \d+:',
                f'## Task {i}:',
                task_blocks[i]
            )
        
        content = '## Task '.join(task_blocks)
    else:
        # Add at end
        task_num = len(data["tasks"]) + 1
        new_task_block = new_task_block.replace("Task X", f"Task {task_num}")
        content = content.rstrip() + "\n\n" + new_task_block
    
    # Update last updated
    content = re.sub(
        r'(\*\*Last Updated:\*\*)\s*\S+',
        rf'\1 {timestamp}',
        content
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return True

def delete_task(filepath: str, task_id: int) -> bool:
    """Delete a task from the todo file"""
    data = parse_todo_file(filepath)
    if task_id < 1 or task_id > len(data["tasks"]):
        return False
    
    content = data["raw"]
    
    # Split by task and remove the specified one
    task_blocks = re.split(r'## Task \d+:', content)
    del task_blocks[task_id]
    
    # Renumber remaining tasks
    for i in range(1, len(task_blocks)):
        task_blocks[i] = re.sub(
            r'## Task \d+:',
            f'## Task {i}:',
            task_blocks[i]
        )
    
    # Rejoin and update timestamp
    new_content = '## Task '.join(task_blocks)
    timestamp = get_timestamp()
    new_content = re.sub(
        r'(\*\*Last Updated:\*\*)\s*\S+',
        rf'\1 {timestamp}',
        new_content
    )
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def create_todo_file(filepath: str, project_name: str) -> bool:
    """Create a new .todo.md file"""
    timestamp = get_timestamp()
    
    content = f"""# Todo List

## Project: {project_name}
- **Created:** {timestamp}
- **Last Updated:** {timestamp}

---
"""
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Todo Parser Script')
    parser.add_argument('--action', required=True, 
                        choices=['get_next_task', 'update_status', 'add_task', 'list_tasks', 
                                'get_first_complete', 'delete_task', 'create'],
                        help='Action to perform')
    parser.add_argument('--file', default='.todo.md', help='Path to todo file')
    parser.add_argument('--task-id', type=int, help='Task ID for update/delete')
    parser.add_argument('--status', help='Status for update')
    parser.add_argument('--title', help='Title for new task')
    parser.add_argument('--description', help='Description for new task')
    parser.add_argument('--notes', help='Notes to add')
    parser.add_argument('--insert-before', type=int, help='Insert task before this ID')
    parser.add_argument('--project', help='Project name for create action')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        if create_todo_file(args.file, args.project or "Untitled Project"):
            print(f"Created {args.file}")
        else:
            print("Failed to create file")
    
    elif args.action == 'get_next_task':
        task = find_next_not_started_task(args.file)
        if task:
            print(json.dumps(task, indent=2))
        else:
            print("No 'not started' tasks found")
    
    elif args.action == 'get_first_complete':
        task = find_first_complete_task(args.file)
        if task:
            print(json.dumps(task, indent=2))
        else:
            print("No 'complete' tasks found")
    
    elif args.action == 'list_tasks':
        data = parse_todo_file(args.file)
        print(json.dumps(data, indent=2))
    
    elif args.action == 'update_status':
        if update_task_status(args.file, args.task_id, args.status, args.notes):
            print(f"Updated task {args.task_id} to '{args.status}'")
        else:
            print(f"Failed to update task {args.task_id}")
    
    elif args.action == 'add_task':
        if add_task(args.file, args.title, args.description, args.insert_before):
            print(f"Added task: {args.title}")
        else:
            print("Failed to add task")
    
    elif args.action == 'delete_task':
        if delete_task(args.file, args.task_id):
            print(f"Deleted task {args.task_id}")
        else:
            print(f"Failed to delete task {args.task_id}")

if __name__ == '__main__':
    main()
