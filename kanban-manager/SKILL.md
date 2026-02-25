---
name: kanban-manager
description: >
  A task management skill using kanban boards for visual project tracking.
  Use when: user wants kanban-style task management, visual project boards,
  task cards, columns for workflow stages, or moving tasks through stages.
---

# Kanban Manager Skill

## Overview

This skill provides a complete task management system using kanban boards for visual project tracking.
It enables autonomous task execution, scheduled work sessions, git integration, and quality verification.
The skill operates in 5 distinct modes to handle all aspects of project task management using kanban boards.

## When to Use

Activate this skill when the user mentions:

- "start a kanban board" or "task board"
- "kanban" or "task management" with visual boards
- "work on tasks" or "execute tasks"
- "automated task execution" or "autonomous work"
- "scheduled tasks" or "recurring work"
- Any request to create or manage project tasks using kanban boards

---

## Kanban Board Structure

### Column Mapping (5-Column System)

| Status      | Column      | Description                               |
| ----------- | ----------- | ----------------------------------------- |
| not started | To Do       | New tasks waiting to be worked on         |
| in progress | In Progress | Tasks currently being worked on           |
| complete    | Done        | Tasks completed, awaiting verification    |
| verified    | Verified    | Tasks verified and complete (final state) |
| failed      | Backlog     | Failed tasks for retry/investigation      |

### Metadata File: .kanban-meta.md

Metadata is stored in `.kanban-meta.md` in the project root:

```markdown
---
title: Kanban Manager
project: [Project Name]
board_id: [UUID from kanban board]
created: [ISO timestamp]
last_updated: [ISO timestamp]
scheduled_task_id: [UUID from scheduler:create_scheduled_task]
scheduled_task_mode: work | verify | complete
work_complete: true | false
---
```

### CHANGELOG.md Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Common Changelog](https://commonform.github.io/changelog/).

## [Date] - Task: [Task Title]

### Completed

- [Description of work completed]

### Notes

- [Additional notes about the work]

---

## [Previous entries...]
```

### error.md Format

```markdown
# Kanban Manager Error

- **Error:** [Error description]
- **Timestamp:** [ISO timestamp]
- **Context:** [What the agent was trying to do]
- **Resolution:** [What action was taken]
```

---

## Mode Definitions

### MODE 1: INIT_MODE (Initialization)

**Purpose:** Set up new kanban-based task management for a project.

**Entry Condition:** First time user wants to start kanban task management OR explicitly requested.

**CRITICAL: Tasks are NEVER deleted** - Only status changes throughout the lifecycle.

**Actions:**

1. Check if `.kanban-meta.md` already exists in project root
2. **If exists, present current state to user and ask:**
   > "A kanban task list already exists for this project. What would you like to do?
   >
   > **Options:**
   >
   > - **Replace:** Clear all existing cards and start fresh with new goals
   > - **Modify:** Keep existing cards and add/update as needed
   >
   > Current board state:
   > [List all cards with their status/column]
3. **If user chooses Replace:**
   - Delete all cards from kanban board (keep board and columns)
   - Ask user for new task list
   - Proceed to create new cards
4. **If user chooses Modify:**
   - Show current cards to user
   - Ask which cards to keep, update, or remove
   - Ask what new goals/tasks to add
   - Update kanban board accordingly
5. If not exists, create kanban board with 5 columns: Backlog, To Do, In Progress, Done, Verified
6. Create `.kanban-meta.md` with project header
7. Create `CHANGELOG.md` if it doesn't exist
8. Ask user for task list (what needs to be done)
9. Create cards in "To Do" column with sequential IDs (task-001, task-002, etc.)
   - Store metadata in card: status, created, updated, notes, subtasks
10. Ask user for work frequency (how often to work on tasks)
11. Schedule recurring task using `scheduler:create_scheduled_task`
    - **CRITICAL:** Save the returned UUID as `scheduled_task_id` in metadata
    - Set `scheduled_task_mode: work` and `work_complete: false` in metadata
    - Write the updated metadata to `.kanban-meta.md`
12. Confirm setup complete with user

### MODE 2: WORK_MODE (Task Execution)

**Purpose:** Execute the next task in the queue autonomously.

**Entry Condition:**

- Scheduled task fires with `scheduled_task_mode: work` in metadata, OR
- User says "work on tasks" / "execute tasks"

**CRITICAL: When to Enter VERIFY_MODE:**
After completing a task, ALWAYS check if ALL tasks are now complete. If all tasks have status "complete" or "verified", you MUST:

1. Update the `.kanban-meta.md` to change `scheduled_task_mode: verify`
2. Then enter VERIFY_MODE immediately to verify the completed work

**CRITICAL: Tasks are NEVER deleted** - Only status changes throughout the lifecycle.

**Actions:**

1. Check if `.kanban-meta.md` exists
   - If not → enter ERROR_MODE
2. Check git status with `git status`
   - If dirty → enter CORRECTION_MODE
3. Read scheduled_task_mode and work_complete from metadata
   - If work_complete is "true" → All work already done, notify user
   - If scheduled_task_mode is "verify" → enter VERIFY_MODE
   - If scheduled_task_mode is "complete" → All work done, notify user
4. Find first card with status "not started" (in "To Do" column)
   - If none → Check if any cards have status "complete" (in "Done" column)
     - If yes → ALL WORK IS DONE, update metadata to `scheduled_task_mode: verify`, enter VERIFY_MODE
     - If no cards are "complete" either → Notify user all tasks are done
5. Move card to "In Progress" column, update metadata status to "in progress"
6. **Work the task autonomously using sub-agents/subordinates** - break down the task into subtasks and delegate to subordinate agents using call_subordinate, solve issues without waiting for input
   - **Subtask limit:** Work on a maximum of 3 subtasks per session
   - If task has more than 3 subtasks, complete up to 3 and mark remaining for next session
   - Help user break down large tasks into smaller, manageable chunks during INIT_MODE
7. **If task is too large to complete in one session:**
   - Break down the task into smaller subtasks
   - Add new cards to kanban board with unique sequential IDs
   - Keep current card in "In Progress" with notes on what's done
   - Commit progress so far
8. On completion:
   - Move card to "Done" column
   - Update card status to "complete"
   - Add completion notes to card metadata
   - Update CHANGELOG.md with descriptive notes
   - Commit all work with single commit
   - **CRITICAL:** After marking complete, check if ALL tasks are now complete or verified
   - If ALL tasks are complete/verified:
     - Update `.kanban-meta.md`: `scheduled_task_mode: verify`
     - Enter VERIFY_MODE immediately to verify completed work
9. On failure:
   - Move card to "Backlog" column
   - Update card status to "failed"
   - Add detailed failure notes explaining why
   - Create new investigation card placed in "To Do" column (directly before failed task)
   - Include context from failure
   - Commit all work with single commit

### MODE 3: VERIFY_MODE (Quality Review)

**Purpose:** Review completed tasks to verify quality. When all tasks are verified, disable the scheduled task so it no longer runs. **Tasks are NEVER deleted** - only status changes.

**Entry Condition:**

- Scheduled task fires with `scheduled_task_mode: verify` in metadata, OR
- WORK_MODE completes last "not started" task and all tasks are now "complete" or "verified"

**CRITICAL: When to Enter VERIFY_MODE from WORK_MODE:**
The most important trigger is when WORK_MODE completes a task and discovers there are no more "not started" tasks. This means all work is done and verification is needed.

**CRITICAL: Tasks are NEVER deleted** - Only status changes throughout the lifecycle.

**Actions:**

1. Check if there are any cards with status "complete" (in "Done" column)
   - If none → ALL TASKS ALREADY VERIFIED, skip to step 6
2. Get the first card marked "complete" (not yet "verified")
3. Review the card description and completion notes
4. Verify requirements were met and work is quality
   - Check if all subtasks were addressed
   - Verify code/tests work if applicable
   - Confirm documentation is complete
5. If verification passes:
   - Move card to "Verified" column
   - Change status to **"verified"**
   - Add verification notes to card metadata
   - Update CHANGELOG.md with verification notes
   - Commit all changes
   - **Loop back to step 1** to check for more "complete" cards
6. If verification fails:
   - Move card back to "In Progress" column
   - Add notes about what needs to be fixed
   - Update metadata: `scheduled_task_mode: work` (switch back to work mode)
   - Return to WORK_MODE
7. **After all tasks verified (no "complete" cards remain, only "verified"):**
   - Read the `scheduled_task_id` from `.kanban-meta.md`
   - **DISABLE the scheduled task** using `scheduler:update_task`:
     - Tool: scheduler:update_task
     - Arguments: task_id: [scheduled_task_id], state: "disabled"
   - Update `.kanban-meta.md` to indicate work is complete:
     ```yaml
     scheduled_task_mode: complete
     work_complete: true
     ```
   - Notify user that all tasks are complete and scheduled task has been disabled

### MODE 4: CORRECTION_MODE (Git State Recovery)

**Purpose:** Handle dirty git state and get back on track.

**Entry Condition:** Git status shows uncommitted changes when entering WORK_MODE

**Actions:**

1. Analyze the uncommitted changes
2. Read `.kanban-meta.md` to find the last task that was being worked on
3. Determine if the task was completed:
   - Check if card status was set to "complete" before git state became dirty
   - Check commit history for recent task completion commits
4. If task was NOT completed:
   - Keep card status as "in progress" if needed
   - Continue working on the task in WORK_MODE
5. If task was completed (status already "complete"):
   - Commit the changes with descriptive message
   - Return to normal WORK_MODE to find next task
6. If unclear:
   - Add notes to current card about the situation
   - Commit with message: "WIP: [task name] - state recovery"
   - Return to WORK_MODE

### MODE 5: ERROR_MODE (Error Handling)

**Purpose:** Handle errors when metadata file is missing.

**Entry Condition:** `.kanban-meta.md` does not exist and not in INIT_MODE

**Actions:**

1. Create `error.md` with:
   - Error: "Project does not contain .kanban-meta.md"
   - Timestamp
   - Context: What the agent was trying to do
   - Resolution: "Created error.md - INIT_MODE required"
2. Check if `error.md` already exists with same information
   - If same error exists:
     - Use `scheduler:find_task_by_name` to find recurring work task
     - Disable the recurring task using scheduler:update_task with state: "disabled"
     - Notify user that task management was cancelled
   - If new error:
     - Ask user if they want to start kanban task management (enter INIT_MODE)

---

## Step-by-Step Instructions

### Starting Kanban Task Management (INIT_MODE)

1. **Check existing files:**

   ```bash
   ls -la | grep -E "\.kanban-meta\.md|CHANGELOG\.md|error\.md"
   ```

2. **If .kanban-meta.md exists, present current state and ask user:**

   > "A kanban task list already exists for this project. Here's the current state:
   >
   > **Current Tasks:**
   >
   > - Task 1: [Title] - [Status/Column]
   > - Task 2: [Title] - [Status/Column]
   > - ...
   >
   > What would you like to do?
   >
   > - **Replace:** Clear all tasks and start fresh with new goals
   > - **Modify:** Update the existing board (keep, remove, or change tasks)"

3. **If user chooses Replace:**
   - Ask: "Are you sure you want to replace the current kanban board? This will clear all existing cards."
   - If confirmed, delete all cards from kanban board
   - Ask for new task list

4. **If user chooses Modify:**
   - Show current cards to user:
     - For each card: "Keep this task? Update it? Remove it?"
   - Ask: "What new tasks would you like to add?"
   - Update kanban board with changes

5. **If no files, create kanban board with columns:**
   - Use `kanban.list_projects` to get project list
   - Use `kanban.create_board` to create board for this project
   - Use `kanban.create_column` to create 5 columns in order:
     - Backlog (position 0)
     - To Do (position 1)
     - In Progress (position 2)
     - Done (position 3)
     - Verified (position 4)

6. **Create `.kanban-meta.md` with ALL required fields:**

   ```markdown
   ---
   title: Kanban Manager
   project: [Project Name]
   board_id: "[UUID from kanban board]"
   created: [ISO timestamp]
   last_updated: [ISO timestamp]
   scheduled_task_id: "" # Will be filled after creating scheduled task
   scheduled_task_mode: work
   work_complete: false
   ---
   ```

7. **Create `CHANGELOG.md`:**

   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Common Changelog](https://commonform.github.io/changelog/).

   ---
   ```

8. **Ask user for tasks:**

   > "What tasks need to be completed for this project? Please describe each task clearly."

9. **Create cards** in "To Do" column:
   - Use `kanban.create_card` for each task
   - Title format: "task-001: [Task Title]"
   - Description: Full task description
   - Store metadata in card's metadata field or description

10. **Ask for frequency with recommended options:**

    > "How often should I work on these tasks? Here are some recommended options:
    >
    > **Recommended Intervals:**
    >
    > - **15 minutes** - Quick check-ins, small tasks
    > - **20 minutes** - Small to medium tasks
    > - **30 minutes** - Medium tasks (recommended default)
    > - **45 minutes** - Medium to large tasks
    > - **60 minutes** - Large, complex tasks
    >
    > **Note:** If your tasks are large or complex, I recommend a **larger frequency** (30-60 minutes) to prevent agent overlap and ensure each session can complete meaningful work before the next session starts.
    >
    > How often would you like me to work on these tasks?"

11. **Create scheduled task:**
    - Use `scheduler:create_scheduled_task` with:
      - Name: "[Project] Kanban Work Session"
      - Prompt: Instructions to load kanban-manager skill and execute appropriate mode based on scheduled_task_mode
      - Schedule based on user frequency
      - dedicated_context: true (so it runs in its own context)
    - **CRITICAL:** Get the returned UUID from scheduler:create_scheduled_task
    - Update `.kanban-meta.md` with the UUID:
      ```yaml
      scheduled_task_id: "[UUID from scheduler response]"
      scheduled_task_mode: work
      work_complete: false
      ```

### Working Tasks (WORK_MODE)

**CRITICAL: When to Enter VERIFY_MODE**
After EVERY task completion, you MUST check if all tasks are now complete or verified. This is the key trigger for VERIFY_MODE.

**CRITICAL: Tasks are NEVER deleted** - Only status changes.

1.  **Check for .kanban-meta.md:**

    ```bash
    test -f .kanban-meta.md && echo "exists" || echo "missing"
    ```

    If missing → ERROR_MODE

2.  **Check git status:**

    ```bash
    git status --porcelain
    ```

    If output not empty → CORRECTION_MODE

3.  **Read metadata from .kanban-meta.md:**
    - Parse `.kanban-meta.md` to get `scheduled_task_mode` and `work_complete` values
    - If work_complete is "true" → All work done, notify user and exit
    - If scheduled_task_mode is "verify" → enter VERIFY_MODE
    - If scheduled_task_mode is "complete" → All work done, notify user and exit

4.  **Get board and find next task:**
    - Use `kanban.get_board` to get board with cards
    - Parse cards in "To Do" column looking for first card with status "not started"

5.  **If no "not started" cards remain:**
    - Check if any cards have status "complete" (in "Done" column)
    - If yes → ALL WORK IS DONE!
      - Update `.kanban-meta.md`: `scheduled_task_mode: verify`
      - Enter VERIFY_MODE immediately to verify completed work
    - If no "complete" cards either → All tasks already verified, enter VERIFY_MODE to complete cleanup

6.  **Update card to "in progress":**
    - Use `kanban.move_card` to move card from "To Do" to "In Progress"
    - Use `kanban.update_card` to update metadata: status="in progress", updated=[timestamp]

7.  **Execute task autonomously using sub-agents/subordinates** - DO NOT wait for user input
    - Break down task into subtasks
    - Delegate subtasks to subordinate agents using call_subordinate tool
    - **Work on maximum 3 subtasks per session** - if more exist, complete up to 3 and note the rest for next session
    - Execute each subtask via sub-agents
    - Handle errors and issues independently
    - Use all available tools to solve problems

8.  **If task is too large:**
    - Break down into smaller tasks
    - Add new cards to kanban board with unique sequential IDs
    - Keep current card partially complete with progress notes
    - Commit progress

9.  **On completion:**
    - Use `kanban.move_card` to move card from "In Progress" to "Done"
    - Use `kanban.update_card` to update metadata:
      ```json
      {
        "status": "complete",
        "updated": "[ISO timestamp]",
        "notes": "[What was accomplished]"
      }
      ```

    Update CHANGELOG.md:

    ```markdown
    ## [Date] - Task: [Task Title]

    ### Completed

    - [Description of work]

    ### Notes

    - [Any additional notes]
    ```

    Commit:

    ```bash
    git add -A
    git commit -m "Complete: [Task Title] - [Brief description]"
    ```

    **CRITICAL: Check if ALL tasks are now complete:**
    - Get board and parse all card statuses
    - If ALL cards have status "complete" or "verified" (none are "not started" or "in progress" or "failed"):
      - Update metadata: `scheduled_task_mode: verify`
      - Enter VERIFY_MODE immediately to verify the completed work

10. **On failure:** - Use `kanban.move_card` to move card from "In Progress" to "Backlog" - Use `kanban.update_card` to update metadata:
    `json
  {
    "status": "failed",
    "updated": "[ISO timestamp]",
    "notes": "[Detailed explanation of why it failed, error messages, attempts made]"
  }
  `

        Create investigation card in "To Do" column (directly before failed task):
        - Use `kanban.create_card` with title like "task-X: Investigate: [Failed Task Title]"
        - Description: "Investigate and resolve the failure: [failure context]"

        Commit:
        ```bash
        git add -A

    git commit -m "Failed: [Task Title] - Reason: [brief reason]. Created investigation task."

    ```

    ```

### Verifying Completed Tasks (VERIFY_MODE)

**When to enter VERIFY_MODE:**

- Scheduled task fires with `scheduled_task_mode: verify` in metadata, OR
- WORK_MODE completes last "not started" task and all remaining cards are "complete"

**NOTE:** VERIFY_MODE may be entered multiple times - it verifies ONE task per run, then the next scheduled run will verify the next task. This is by design to prevent one agent from doing too much work.

**CRITICAL: Tasks are NEVER deleted** - Only status changes.

1. **Check for remaining "complete" cards:**
   - Use `kanban.get_board` to get board
   - Look for cards in "Done" column with status "complete"
   - If none found → All tasks already verified, skip to step 6

2. **Get first "complete" card** from board (first card with status "complete", not yet "verified")

3. **Verify the work:**
   - Re-read card description
   - Check if requirements were met
   - Test code if applicable
   - Review documentation

4. **If verified:**
   - Use `kanban.move_card` to move card from "Done" to "Verified"
   - Use `kanban.update_card` to update metadata:
     ```json
     {
       "status": "verified",
       "verified": "[ISO timestamp]",
       "verification_notes": "Quality check passed - [notes]"
     }
     ```
   - Update CHANGELOG.md:

     ```markdown
     ## [Date] - Task: [Task Title] - VERIFIED

     ### Completed

     - [Original completion notes]

     ### Verified

     - Quality check passed - [verification notes]
     ```

   - Commit:
     `bash
     git add -A
git commit -m "Verified: [Task Title] - Quality verified"
     `
   - **The scheduled task will run again to verify the next "complete" card**

5. **If failed verification:**
   - Move card back to "In Progress" column
   - Add notes about what needs fixing
   - Update metadata: `scheduled_task_mode: work` (switch back to work mode)
   - Continue in WORK_MODE

6. **After all tasks verified (no "complete" cards remain):**
   - **DISABLE the scheduled task** using `scheduler:update_task`:
     - Tool: scheduler:update_task
     - Arguments:
       - task_id: [scheduled_task_id from metadata]
       - state: "disabled"
   - Update `.kanban-meta.md` to indicate completion:
     ```yaml
     scheduled_task_mode: complete
     work_complete: true
     ```
   - Notify user that all tasks are complete and scheduled task has been disabled

### Handling Dirty Git State (CORRECTION_MODE)

1. **Get git diff** to see what changed:

   ```bash
   git diff --stat
   git diff
   ```

2. **Read .kanban-meta.md** to see last task status

3. **Check commit history:**

   ```bash
   git log --oneline -10
   ```

4. **Determine action:**
   - If card was marked "complete" before dirty state → commit and continue
   - If card was in progress → continue working
   - If unclear → commit with "WIP" message and continue

### Error Handling (ERROR_MODE)

1. **Check if error.md exists:**

   ```bash
   test -f error.md && cat error.md
   ```

2. **If same error exists:**

   ```bash
   scheduler:find_task_by_name
   # Find the recurring work task
   scheduler:update_task (if found)
   ```

3. **If new error:**
   Create error.md with details
   Ask user: "This project doesn't have kanban task management set up. Would you like to start a new kanban board?"

---

## Frequency Options

**Recommended work frequencies for scheduled tasks:**

| Interval   | Best For                           | Notes                              |
| ---------- | ---------------------------------- | ---------------------------------- |
| 15 minutes | Quick check-ins, very small tasks  | May cause overlap with large tasks |
| 20 minutes | Small tasks                        | Minimum for most sessions          |
| 30 minutes | Medium tasks (recommended default) | Good balance                       |
| 45 minutes | Medium to large tasks              | Recommended for complex work       |
| 60 minutes | Large, complex tasks               | Prevents agent overlap             |

**Guidance for Large Tasks:**

If your task list contains large or complex tasks, **choose a larger frequency (30-60 minutes)**. This ensures:

- Each session has enough time to make meaningful progress
- Previous session completes before next starts (no agent overlap)
- Sub-agents have sufficient time to complete subtasks
- Better git commit hygiene (one task per session)

| User Input       | Cron Schedule  |
| ---------------- | -------------- |
| Every 15 minutes | `*/15 * * * *` |
| Every 20 minutes | `*/20 * * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Every 45 minutes | `*/45 * * * *` |
| Every 60 minutes | `0 * * * *`    |
| Hourly           | `0 * * * *`    |
| Daily            | `0 0 * * *`    |
| Weekly           | `0 0 * * 0`    |

Or accept custom cron expression from user.

---

## Available Kanban Tools

**IMPORTANT:** Use these exact tool names and parameters:

| Tool                   | Purpose                          | Key Parameters                          |
| ---------------------- | -------------------------------- | --------------------------------------- |
| `kanban.list_boards`   | List all kanban boards           | -                                       |
| `kanban.list_projects` | List all projects                | -                                       |
| `kanban.get_board`     | Get board with columns and cards | board_id                                |
| `kanban.create_board`  | Create new board                 | project_id, name                        |
| `kanban.create_column` | Create column in board           | board_id, name, position                |
| `kanban.create_card`   | Create card in column            | column_id, title, description, metadata |
| `kanban.update_card`   | Update card details              | card_id, title, description, metadata   |
| `kanban.move_card`     | Move card between columns        | card_id, column_id, position            |
| `kanban.delete_card`   | Delete card from board           | card_id                                 |

## Available Scheduler Tools

**IMPORTANT:** Use these exact tool names and parameters:

| Tool                              | Purpose                          | Key Parameters                                           |
| --------------------------------- | -------------------------------- | -------------------------------------------------------- |
| `scheduler:create_scheduled_task` | Create recurring task            | name, system_prompt, prompt, schedule, dedicated_context |
| `scheduler:update_task`           | Update or disable scheduled task | task_id, state (use "disabled" to disable)               |
| `scheduler:find_task_by_name`     | Find task by name                | name                                                     |
| `scheduler:run_task`              | Run task manually                | uuid, context                                            |

---

## Example Use Cases

### Example 1: Starting a New Kanban Project

- **User:** "I want to start a kanban board for my project"
- **Agent:** Enters INIT_MODE, checks for existing files
- **Agent:** Creates kanban board with 5 columns
- **Result:** Kanban board created, cards in "To Do", `.kanban-meta.md` with scheduled_task_id, scheduled task configured

### Example 2: Continuing Existing Project with New Goals

- **User:** "I want to add more tasks to the kanban"
- **Agent:** Enters INIT_MODE, finds existing `.kanban-meta.md`
- **Agent:** Presents current cards, asks: "Replace or Modify?"
- **User:** "Modify"
- **Agent:** Walks through current cards, adds new ones
- **Result:** Updated kanban board with new and existing cards

### Example 3: Scheduled Work Session - All Work Complete

- **Trigger:** Scheduled task fires, agent enters WORK_MODE
- **Agent:** Checks scheduled_task_mode from metadata
- **Agent:** Finds no "not started" cards but has "complete" cards
- **Agent:** Updates metadata to `scheduled_task_mode: verify`, enters VERIFY_MODE
- **Result:** Completed card is verified, moved to "Verified" column

### Example 4: Verify Mode - Next Run Verifies Next Task

- **Trigger:** Scheduled task fires with `scheduled_task_mode: verify`
- **Agent:** Enters VERIFY_MODE, finds first "complete" card
- **Agent:** Verifies it, moves to "Verified", commits
- **Agent:** Checks for more "complete" cards - if more exist, the next scheduled run will verify the next one
- **Result:** One card verified per run, eventually all verified

### Example 5: All Work Complete - Disable Scheduled Task

- **Trigger:** VERIFY_MODE finds no remaining "complete" cards
- **Agent:** Reads scheduled_task_id, calls scheduler:update_task with state: "disabled"
- **Agent:** Updates metadata to `scheduled_task_mode: complete`, `work_complete: true`
- **Result:** Project complete, scheduled task disabled, cards preserved with verified status

### Example 6: User Requests Work

- **User:** "Work on the tasks"
- **Agent:** Enters WORK_MODE (checks git first), executes task
- **Result:** Card completed or failed with investigation card created

### Example 7: Dirty Git State

- **Trigger:** WORK_MODE finds dirty git
- **Agent:** Enters CORRECTION_MODE, analyzes state
- **Result:** Either commits and continues OR continues interrupted work

### Example 8: No Metadata File

- **Trigger:** Agent in non-INIT mode finds no .kanban-meta.md
- **Agent:** Enters ERROR_MODE, creates error.md
- **Result:** User prompted to start kanban task management or recurring task disabled

---

## Edge Cases

1. **No tasks in kanban board**
   - Ask user to add tasks before scheduling

2. **All tasks failed**
   - Keep failed cards in "Backlog" with investigation cards in "To Do"
   - Agent will work on investigation cards first

3. **Recurring task already exists**
   - Ask user if they want to update frequency or keep existing

4. **Git conflict during commit**
   - Resolve conflict, complete commit, note in changelog

5. **Very long task descriptions**
   - Keep descriptions concise but complete
   - Add detail in subtasks if needed

6. **Task depends on another task**
   - Add dependency notes in description
   - Agent should complete prerequisite tasks first

7. **Large task frequency recommendation**
   - Always recommend 30-60 minute intervals for large/complex tasks
   - Explain that smaller intervals may cause agent overlap

8. **Verify mode not triggering**
   - CRITICAL: After completing ANY task in WORK_MODE, always check if all tasks are now complete
   - If all tasks are "complete" or "verified", immediately update `scheduled_task_mode: verify` and enter VERIFY_MODE
   - This is the key mechanism that ensures verification happens

9. **Scheduled task runs in wrong mode**
   - The metadata `scheduled_task_mode` field controls which mode runs
   - WORK_MODE updates this to "verify" when all tasks complete
   - VERIFY_MODE updates this to "work" if verification fails and work is needed

10. **Task verification takes multiple runs**
    - VERIFY_MODE verifies ONE task per scheduled run
    - This is intentional to prevent agent overload
    - The next scheduled run will verify the next "complete" card

---

## Fundamental Principles

### CRITICAL: Tasks are NEVER deleted

- Cards remain in kanban board forever
- Only status/column changes: not started → in progress → complete → verified (or failed → Backlog)
- This preserves the complete history of work done

### CRITICAL: Scheduled Task Handling

- The recurring scheduled task should be DISABLED when all work is complete
- Use `scheduler:update_task` with `state: "disabled"` to disable the task
- The kanban board and cards are NEVER deleted

---

## Scheduled Task Prompt Template

When creating the recurring task, use this prompt:

```
You are running a scheduled work session for the kanban-manager skill.

Project: [PROJECT NAME]
Metadata File: .kanban-meta.md

IMPORTANT: Check the scheduled_task_mode and work_complete in .kanban-meta.md metadata FIRST:
- If work_complete is "true": All work is done, notify user and exit
- If scheduled_task_mode is "complete": All work is done, notify user and exit
- If scheduled_task_mode is "verify": Execute VERIFY_MODE
- If scheduled_task_mode is "work" OR NOT SET: Execute WORK_MODE

Instructions:
1. Load the kanban-manager skill
2. Read .kanban-meta.md and parse the metadata for scheduled_task_mode and work_complete
3. Use kanban.get_board to see current board state
4. Execute the appropriate mode based on the mode values
5. Do not wait for user input - work autonomously
6. Handle any errors that arise
7. Report completion status when done

Remember: Use kanban tools to manage cards and all available tools to complete tasks. Do not ask for user input unless absolutely necessary.
```

---

## Tools & Resources

### Required Tools

- `kanban.*`: All kanban MCP tools for board/column/card management
- `code_execution_tool`: For git operations, file read/write
- `scheduler:create_scheduled_task`: For creating scheduled tasks (returns UUID)
- `scheduler:update_task`: For disabling scheduled task (use state: "disabled")
- `scheduler:find_task_by_name`: For finding existing tasks
- `document_query`: For reading metadata files
- `memory_*`: For storing project context if needed

### File Locations

- Metadata file: `.kanban-meta.md` (project root) - NEVER deleted
- Changelog: `CHANGELOG.md` (project root)
- Error file: `error.md` (project root)

---

## Notes

- Always use ISO 8601 timestamps: `YYYY-MM-DDTHH:MM:SSZ`
- The skill assumes it's running in the project directory
- Commits should be atomic - one task per commit
- Use descriptive commit messages that match changelog entries
- Investigation cards should have clear failure context
- When in doubt, prefer continuing work over asking questions
- Check git status before every work session
- Quality verification is critical - don't just mark complete
- **CRITICAL:** When existing tasks are found, ALWAYS ask user whether to replace or modify - never automatically reset
- **CRITICAL:** Recommend larger frequencies (30-60 min) for large tasks to prevent agent overlap
- **CRITICAL:** After completing ANY task in WORK_MODE, ALWAYS check if ALL tasks are now complete/verified. If so, update `scheduled_task_mode: verify` and enter VERIFY_MODE immediately.
- **CRITICAL:** In VERIFY_MODE, when a task passes verification, update its status to "verified" and move to Verified column (NOT deleted)
- **CRITICAL:** Always save the scheduled_task_id from scheduler:create_scheduled_task to the metadata - this is required to disable the task later
- **CRITICAL:** Tasks are NEVER deleted from kanban board - only status/column changes
- **CRITICAL:** Use scheduler:update_task with state: "disabled" to disable the scheduled task when work is complete
- **CRITICAL:** Use kanban.move_card to move cards between columns based on task status changes

---

_Skill Version: 1.1 | Author: Agent Zero | Based on agentskills.io specification_

---

## Version History

- **1.1** - Cleaned up: Removed all references to todo-manager and markdown-based task files. Pure kanban-based task management.
- **1.0** - Initial release
