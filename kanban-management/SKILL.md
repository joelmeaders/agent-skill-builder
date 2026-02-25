---
name: kanban-management
description: >
  A skill for managing kanban boards, projects, columns, cards, and comments via MCP.
  Use when: user needs to create or manage tasks, organize work items, track project progress,
  manage to-do lists, create kanban boards, move tasks through workflow stages, add comments to tasks,
  or perform batch operations on multiple cards at once.
license: MIT
compatibility: agent0 v0.9+
metadata:
  author: Agent Skill Builder
  version: "3.0"
---

# Kanban Management Skill

This skill provides comprehensive tools for managing kanban boards, projects, columns, cards, and comments through the MCP interface.

## What You Can Do With This Skill

The agent can perform the following categories of actions:

| Capability | Description |
|------------|-------------|
| **Project Management** | List and sync projects that own boards |
| **Board Operations** | Create, read, update, delete kanban boards |
| **Column Management** | Add, modify, reorder, remove columns in boards |
| **Card Operations** | Create, update, move, delete task cards |
| **Batch Operations** | Create, update, move, or delete multiple cards simultaneously |
| **Comments** | Add, modify, retrieve, and delete comments on cards |

---

## When to Use Each Capability

### Project Management

**When to use:**
- At the start of any kanban workflow to identify which project to work with
- When creating a new board, you need the project_id first
- When you need to see all available projects

**How to use:**
```
# List all available projects
list_projects()

# Sync projects from filesystem (discovers projects automatically)
sync_projects(projects_path="/a0/usr/projects")
```

**Instance:** User says "Show me my projects" or "I need to create a board for my project"

---

### Board Operations

**When to use:**
- User wants to see all boards across projects
- User needs to view a specific board with all its columns and cards
- Creating a new board for organizing work
- Renaming or updating board metadata
- Deleting an old or unused board

**How to use:**
```
# List all boards with their project info
list_boards()

# Get a specific board (returns columns and cards)
get_board(board_id="uuid-of-board")

# Create a new board for a project
create_board(project_id="uuid-of-project", name="Sprint Board")

# Update board name or metadata
update_board(board_id="uuid-of-board", name="New Name")

# Delete a board (deletes columns and cards too)
delete_board(board_id="uuid-of-board")
```

**Instances:**
- User says "Create a kanban board for my marketing project"
- User says "Show me the board called Sprint Planning"
- User says "What boards exist in my project?"

---

### Column Management

**When to use:**
- Setting up a new board with workflow stages
- Adding a new stage to an existing workflow (e.g., "In Review")
- Renaming columns to match team terminology
- Reordering columns to reflect priority
- Removing columns that are no longer needed

**How to use:**
```
# Create a new column in a board
create_column(board_id="uuid-of-board", name="In Review", position=2)

# Rename a column
update_column(column_id="uuid-of-column", name="Review")

# Reorder a column (position is 0-indexed)
update_column(column_id="uuid-of-column", position=3)

# Delete a column (moves cards to first column or fails if column has cards - handle appropriately)
delete_column(column_id="uuid-of-column")
```

**Instances:**
- User says "Add a 'Testing' column to our board"
- User says "Rename the third column to 'Awaiting Approval'"
- User wants to set up columns like: To Do, In Progress, In Review, Done

**Common column patterns:**
| Pattern | Columns |
|---------|---------|
| Simple | To Do, In Progress, Done |
| Standard | Backlog, To Do, In Progress, Done |
| Complete | To Do, In Progress, In Review, Done, Verified |
| Bug Tracking | To Do, In Progress, In Review, Verified, Backlog |

---

### Card Operations

**When to use:**
- Creating new tasks or work items
- Updating task details (title, description, metadata)
- Moving tasks between workflow stages (columns)
- Reordering tasks within a column
- Deleting tasks that are no longer needed

**How to use:**
```
# Create a new task card
create_card(column_id="uuid-of-column", title="Fix login bug", description="Users cannot log in with special characters")

# Update card details
update_card(card_id="uuid-of-card", title="Fixed login bug", description="Issue resolved in v2.1")

# Move card to a different column (workflow stage change)
move_card(card_id="uuid-of-card", column_id="new-column-uuid", position=0)

# Reorder card within same column
update_card(card_id="uuid-of-card", position=5)

# Move card by updating its column
update_card(card_id="uuid-of-card", column_id="new-column-uuid")

# Delete a card
delete_card(card_id="uuid-of-card")
```

**Instances:**
- User says "Add a task to review the design"
- User says "Move the bug fix to the Done column"
- User says "Update the description for task #3"
- User says "What tasks are in the To Do column?"

**Card lifecycle:**
1. Create in appropriate column (typically "To Do")
2. Move through columns as work progresses
3. End in final column (typically "Done" or "Verified")

---

### Batch Operations

**When to use:**
- Importing multiple tasks at once (e.g., from a sprint backlog)
- Updating status of multiple tasks simultaneously
- Moving multiple tasks to a new stage (e.g., starting a new sprint)
- Deleting completed or obsolete tasks in bulk
- Reorganizing many cards at once

**How to use:**
```
# Create multiple cards at once
batch_create_cards(cards=[
    {"column_id": "col-uuid-1", "title": "Task 1", "description": "First task"},
    {"column_id": "col-uuid-1", "title": "Task 2", "description": "Second task"},
    {"column_id": "col-uuid-2", "title": "Task 3"}
])

# Update multiple cards at once
batch_update_cards(cards=[
    {"id": "card-uuid-1", "title": "Updated Title 1", "position": 0},
    {"id": "card-uuid-2", "description": "New description"},
    {"id": "card-uuid-3", "column_id": "new-column-uuid"}
])

# Delete multiple cards at once
batch_delete_cards(ids=["card-uuid-1", "card-uuid-2", "card-uuid-3"])

# Move multiple cards to a column at once
batch_move_cards(card_ids=["card-uuid-1", "card-uuid-2", "card-uuid-3"], column_id="target-column-uuid")
```

**Instances:**
- User says "Import these 10 tasks from our planning meeting"
- User says "Move all completed tasks to Done column"
- User says "Archive these old tasks (delete them)"
- User says "Start a new sprint - move these tasks to In Progress"

**Batch vs Individual:**
- Use batch when: 3+ cards need same operation, importing lists, bulk moves
- Use individual when: 1-2 cards, complex different updates, unclear requirements

---

### Comments

**When to use:**
- Adding notes or context to a task
- Recording review feedback on a task
- Adding questions that need answering
- Tracking discussions about work items
- Adding status updates or blockers

**How to use:**
```
# Get all comments on a card
get_comments(card_id="uuid-of-card")

# Add a comment to a card
create_comment(card_id="uuid-of-card", content="This needs review before merging", author="Reviewer")

# Update a comment
update_comment(comment_id="uuid-of-comment", content="Updated comment text")

# Delete a comment
delete_comment(comment_id="uuid-of-comment")
```

**Instances:**
- User says "Add a note to the design task about the color scheme"
- User says "What's the discussion on the bug fix?"
- User says "Mark the review comment as addressed"
- User says "Add feedback: needs more testing"

---

## Complete Tool Reference

### Projects
| Tool | Description |
|------|-------------|
| `list_projects` | List all projects that can own boards |
| `sync_projects` | Sync projects from filesystem to discover available projects |

### Boards
| Tool | Description |
|------|-------------|
| `list_boards` | List all kanban boards with project information |
| `get_board` | Get a board with all its columns and cards |
| `create_board` | Create a new board for a project |
| `update_board` | Update a board's name or metadata |
| `delete_board` | Delete a board and all its contents |

### Columns
| Tool | Description |
|------|-------------|
| `create_column` | Create a new column in a board |
| `update_column` | Update a column's name or position |
| `delete_column` | Delete a column |

### Cards
| Tool | Description |
|------|-------------|
| `create_card` | Create a new card in a column |
| `update_card` | Update a card's title, description, position, or column |
| `move_card` | Move a card to a different column |
| `delete_card` | Delete a card |

### Batch Operations
| Tool | Description |
|------|-------------|
| `batch_create_cards` | Create multiple cards at once |
| `batch_update_cards` | Update multiple cards at once |
| `batch_delete_cards` | Delete multiple cards at once |
| `batch_move_cards` | Move multiple cards to a column at once |

### Comments
| Tool | Description |
|------|-------------|
| `get_comments` | Get comments for a card |
| `create_comment` | Create a comment on a card |
| `update_comment` | Update a comment |
| `delete_comment` | Delete a comment |

---

## Common Workflows

### Creating a New Project Board

1. **Identify the project**: `list_projects()` or `sync_projects()`
2. **Create the board**: `create_board(project_id="uuid", name="Board Name")`
3. **Set up columns**: Use `create_column` for each workflow stage
4. **Add tasks**: Use `create_card` or `batch_create_cards`

### Moving Tasks Through Workflow

1. **View current state**: `get_board(board_id="uuid")`
2. **Move task**: `move_card(card_id="uuid", column_id="next-stage-uuid")`
3. **Or update directly**: `update_card(card_id="uuid", column_id="next-stage-uuid")`

### Bulk Task Import

1. **Get target column**: Find column ID from `get_board`
2. **Prepare card data**: Create list of {column_id, title, description}
3. **Import**: `batch_create_cards(cards=[...])`

### Adding Discussion to Tasks

1. **Find card**: Get card ID from `get_board`
2. **Add comment**: `create_comment(card_id="uuid", content="...", author="Name")`
3. **View discussion**: `get_comments(card_id="uuid")`

---

## Data Structures

### Board Response
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "name": "Board Name",
  "columns": [
    {
      "id": "uuid",
      "name": "To Do",
      "position": 0,
      "cards": [
        {
          "id": "uuid",
          "title": "Task title",
          "description": "Task description",
          "position": 0
        }
      ]
    }
  ]
}
```

---

## Edge Cases

1. **Empty board**: Boards are created with default columns: New, To Do, In Progress, Done
2. **Position handling**: When moving cards, specify position explicitly or they'll append to end
3. **Batch partial failure**: If one card in a batch fails, others still proceed; check returned results
4. **Column deletion**: May fail if column has cards - handle by moving cards first or using batch operations
5. **Card updates**: Can update multiple fields in single call (title, description, column_id, position)

---

## Best Practices

1. **Always get the board first** to understand structure before making changes
2. **Use batch operations** for 3+ cards to reduce API calls
3. **Use descriptive titles** for cards that clearly indicate the work item
4. **Add descriptions** for cards with details, requirements, or context
5. **Use comments** for ongoing discussion rather than constantly editing card description
6. **Plan column structure** before bulk card creation

---

*Skill Version: 3.0 | Focus: MCP-only usage for kanban board management*
