# Todo Manager Skill

## Overview

This skill provides a complete task management system for AI agents. It enables autonomous task execution,
scheduled work sessions, git integration, and quality verification. The skill operates in 5 distinct modes
to handle all aspects of project task management.

## When to Use

Activate this skill when the user mentions:
- "start a todo list" or "task list"
- "task management" or "project tracking"
- "work on tasks" or "execute tasks"
- "automated task execution" or "autonomous work"
- "scheduled tasks" or "recurring work"
- Any request to create or manage project tasks

---

## File Formats

### .todo.md Structure

The task file uses a structured markdown format with task blocks:

```markdown
---
title: Todo List
project: [Project Name]
created: [ISO timestamp]
last_updated: [ISO timestamp]
scheduled_task_id: [UUID from scheduler:create_scheduled_task]
scheduled_task_mode: work | verify | complete
work_complete: true | false
---

## Task 1: [Task Title]
id: [auto-generated unique task ID, e.g., task-001]
- **Status:** not started | in progress | complete | failed | verified
- **Created:** [ISO timestamp]
- **Updated:** [ISO timestamp]
- **Description:** [What needs to be done - be specific and detailed]
- **Notes:** [Work notes, added as tasks progress]
- **Subtasks:** [Optional list of subtasks for this task]

## Task 2: [Task Title]
id: [auto-generated unique task ID, e.g., task-002]
- **Status:** not started | in progress | complete | failed | verified
- **Created:** [ISO timestamp]
- **Updated:** [ISO timestamp]
- **Description:** [What needs to be done]
- **Notes:** [Work notes]
- **Subtasks:** [Optional list of subtasks for this task]
```

### CHANGELOG.md Format (Common Changelog Standard)

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
# Todo Manager Error

- **Error:** [Error description]
- **Timestamp:** [ISO timestamp]
- **Context:** [What the agent was trying to do]
- **Resolution:** [What action was taken]
```

---

## Mode Definitions

### MODE 1: INIT_MODE (Initialization)

**Purpose:** Set up new task management for a project.

**Entry Condition:** First time user wants to start task management OR explicitly requested.

**CRITICAL: Tasks are NEVER deleted** - Only status changes throughout the lifecycle.

**Actions:**
1. Check if `.todo.md` already exists in project root
2. **If exists, present current state to user and ask:**
   > "A task list already exists for this project. What would you like to do?
   >
   > **Options:**
   > - **Replace:** Clear all existing tasks and start fresh with new goals
   > - **Modify:** Keep existing tasks and add/update as needed
   >
   > Current task list:
   > [List all existing tasks with their status]
3. **If user chooses Replace:**
   - Clear all tasks from `.todo.md` (keep header metadata)
   - Ask user for new task list
   - Proceed to populate with new tasks
4. **If user chooses Modify:**
   - Walk through current task list with user
   - Ask which tasks to keep, update, or remove
   - Ask what new goals/tasks to add
   - Update `.todo.md` accordingly
5. If not exists, create `.todo.md` with project header
6. Create `CHANGELOG.md` if it doesn't exist
7. Ask user for task list (what needs to be done)
8. Populate `.todo.md` with tasks
9. Ask user for work frequency (how often to work on tasks)
10. Schedule recurring task using `scheduler:create_scheduled_task`
    - **CRITICAL:** Save the returned UUID as `scheduled_task_id` in frontmatter
    - Set `scheduled_task_mode: work` and `work_complete: false` in frontmatter
    - Write the updated frontmatter to `.todo.md`
11. Confirm setup complete with user

### MODE 2: WORK_MODE (Task Execution)

**Purpose:** Execute the next task in the queue autonomously.

**Entry Condition:** 
- Scheduled task fires with `scheduled_task_mode: work` in frontmatter, OR
- User says "work on tasks" / "execute tasks"

**CRITICAL: When to Enter VERIFY_MODE:**
After completing a task, ALWAYS check if ALL tasks are now complete. If all tasks have status "complete" or "verified", you MUST:
1. Update the `.todo.md` frontmatter to change `scheduled_task_mode: verify`
2. Then enter VERIFY_MODE immediately to verify the completed work

**CRITICAL: Tasks are NEVER deleted** - Only status changes throughout the lifecycle.

**Actions:**
1. Check if `.todo.md` exists
   - If not → enter ERROR_MODE
2. Check git status with `git status`
   - If dirty → enter CORRECTION_MODE
3. Read scheduled_task_mode and work_complete from frontmatter
   - If work_complete is "true" → All work already done, notify user
   - If scheduled_task_mode is "verify" → enter VERIFY_MODE
   - If scheduled_task_mode is "complete" → All work done, notify user
4. Find first task with status "not started"
   - If none → Check if any tasks have status "complete"
     - If yes → ALL WORK IS DONE, update frontmatter to `scheduled_task_mode: verify`, enter VERIFY_MODE
     - If no tasks are "complete" either → Notify user all tasks are done
5. Set task status to "in progress", add timestamp to notes
6. **Work the task autonomously using sub-agents/subordinates** - break down the task into subtasks and delegate to subordinate agents using call_subordinate, solve issues without waiting for input
   - **Subtask limit:** Work on a maximum of 3 subtasks per session
   - If task has more than 3 subtasks, complete up to 3 and mark remaining for next session
   - Help user break down large tasks into smaller, manageable chunks during INIT_MODE
7. **If task is too large to complete in one session:**
   - Break down the task into smaller subtasks
   - Add new tasks to `.todo.md` with unique IDs
   - Mark current task as "in progress" with notes on what's done
   - Commit progress so far
8. On completion:
   - Set status to "complete"
   - Add completion notes to task
   - Update CHANGELOG.md with descriptive notes
   - Commit all work with single commit
   - **CRITICAL:** After marking complete, check if ALL tasks are now complete or verified
   - If ALL tasks are complete/verified:
     - Update `.todo.md` frontmatter: `scheduled_task_mode: verify`
     - Write the updated frontmatter to `.todo.md`
     - Enter VERIFY_MODE immediately to verify completed work
9. On failure:
   - Set status to "failed"
   - Add detailed failure notes explaining why
   - Create new investigation task placed directly before failing task
   - Include context from failure
   - Commit all work with single commit

### MODE 3: VERIFY_MODE (Quality Review)

**Purpose:** Review completed tasks to verify quality. When all tasks are verified, disable the scheduled task so it no longer runs. **Tasks are NEVER deleted** - only status changes.

**Entry Condition:** 
- Scheduled task fires with `scheduled_task_mode: verify` in frontmatter, OR
- WORK_MODE completes last "not started" task and all tasks are now "complete" or "verified"

**CRITICAL: When to Enter VERIFY_MODE from WORK_MODE:**
The most important trigger is when WORK_MODE completes a task and discovers there are no more "not started" tasks. This means all work is done and verification is needed.

**CRITICAL: Tasks are NEVER deleted** - Only status changes throughout the lifecycle.

**Actions:**
1. Check if there are any tasks with status "complete" (not yet verified)
   - If none → ALL TASKS ALREADY VERIFIED, skip to step 6
2. Get the first task marked "complete" (not yet "verified")
3. Review the task description and completion notes
4. Verify requirements were met and work is quality
   - Check if all subtasks were addressed
   - Verify code/tests work if applicable
   - Confirm documentation is complete
5. If verification passes:
   - Change status from "complete" to **"verified"**
   - Add verification notes to task
   - Update CHANGELOG.md with verification notes
   - Commit all changes
   - **Loop back to step 1** to check for more "complete" tasks
6. If verification fails:
   - Set status back to "in progress"
   - Add notes about what needs to be fixed
   - Update frontmatter: `scheduled_task_mode: work` (switch back to work mode)
   - Write updated frontmatter to `.todo.md`
   - Return to WORK_MODE
7. **After all tasks verified (no "complete" tasks remain, only "verified"):**
   - Read the `scheduled_task_id` from `.todo.md` frontmatter
   - **DISABLE the scheduled task** using `scheduler:update_task`:
     - Tool: scheduler:update_task
     - Arguments: task_id: [scheduled_task_id from frontmatter], state: "disabled"
   - Update `.todo.md` frontmatter to indicate work is complete:
     ```yaml
     scheduled_task_mode: complete
     work_complete: true
     ```
   - Write updated frontmatter to `.todo.md`
   - Notify user that all tasks are complete and scheduled task has been disabled

### MODE 4: CORRECTION_MODE (Git State Recovery)

**Purpose:** Handle dirty git state and get back on track.

**Entry Condition:** Git status shows uncommitted changes when entering WORK_MODE

**Actions:**
1. Analyze the uncommitted changes
2. Read `.todo.md` to find the last task that was being worked on
3. Determine if the task was completed:
   - Check if task status was set to "complete" before git state became dirty
   - Check commit history for recent task completion commits
4. If task was NOT completed:
   - Set task status back to "in progress" if needed
   - Continue working on the task in WORK_MODE
5. If task was completed (status already "complete"):
   - Commit the changes with descriptive message
   - Return to normal WORK_MODE to find next task
6. If unclear:
   - Add notes to current task about the situation
   - Commit with message: "WIP: [task name] - state recovery"
   - Return to WORK_MODE

### MODE 5: ERROR_MODE (Error Handling)

**Purpose:** Handle errors when task file is missing.

**Entry Condition:** `.todo.md` does not exist and not in INIT_MODE

**Actions:**
1. Create `error.md` with:
   - Error: "Project does not contain .todo.md"
   - Timestamp
   - Context: What the agent was trying to do
   - Resolution: "Created error.md - INIT_MODE required"
2. Check if `error.md` already exists with same information
   - If same error exists:
     - Use `scheduler:find_task_by_name` to find recurring work task
     - Disable the recurring task using scheduler:update_task with state: "disabled"
     - Notify user that task management was cancelled
   - If new error:
     - Ask user if they want to start task management (enter INIT_MODE)

---

## Step-by-Step Instructions

### Starting Task Management (INIT_MODE)

1. **Check existing files:**
   ```bash
   ls -la | grep -E "\.todo\.md|CHANGELOG\.md|error\.md"
   ```

2. **If .todo.md exists, present current state and ask user:**
   > "A task list already exists for this project. Here's the current state:
   >
   > **Current Tasks:**
   > - Task 1: [Title] - [Status]
   > - Task 2: [Title] - [Status]
   > - ...
   >
   > What would you like to do?
   > - **Replace:** Clear all tasks and start fresh with new goals
   > - **Modify:** Update the existing list (keep, remove, or change tasks)"

3. **If user chooses Replace:**
   - Ask: "Are you sure you want to replace the current task list? This will clear all existing tasks."
   - If confirmed, clear tasks from `.todo.md` (keep header metadata)
   - Ask for new task list

4. **If user chooses Modify:**
   - Walk through current tasks one by one:
     - For each task: "Keep this task? Update it? Remove it?"
   - Ask: "What new tasks would you like to add?"
   - Update `.todo.md` with changes

5. **If no files, create `.todo.md` with ALL required fields:**
   ```markdown
   ---
   title: Todo List
   project: [Project Name]
   created: [ISO timestamp]
   last_updated: [ISO timestamp]
   scheduled_task_id: ""  # Will be filled after creating scheduled task
   scheduled_task_mode: work
   work_complete: false
   ---
   ```

6. **Create `CHANGELOG.md`:**
   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Common Changelog](https://commonform.github.io/changelog/).

   ---
   ```

7. **Ask user for tasks:**
   > "What tasks need to be completed for this project? Please describe each task clearly."

8. **Populate tasks** in `.todo.md` with status "not started"

9. **Ask for frequency with recommended options:**
   > "How often should I work on these tasks? Here are some recommended options:
   >
   > **Recommended Intervals:**
   > - **15 minutes** - Quick check-ins, small tasks
   > - **20 minutes** - Small to medium tasks
   > - **30 minutes** - Medium tasks (recommended default)
   > - **45 minutes** - Medium to large tasks
   > - **60 minutes** - Large, complex tasks
   >
   > **Note:** If your tasks are large or complex, I recommend a **larger frequency** (30-60 minutes) to prevent agent overlap and ensure each session can complete meaningful work before the next session starts.
   >
   > How often would you like me to work on these tasks?"

10. **Create scheduled task:**
    - Use `scheduler:create_scheduled_task` with:
      - Name: "[Project] Todo Work Session"
      - Prompt: Instructions to load todo-manager skill and execute appropriate mode based on scheduled_task_mode
      - Schedule based on user frequency
      - dedicated_context: true (so it runs in its own context)
    - **CRITICAL:** Get the returned UUID from scheduler:create_scheduled_task
    - Update `.todo.md` frontmatter with the UUID:
      ```yaml
      scheduled_task_id: "[UUID from scheduler response]"
      scheduled_task_mode: work
      work_complete: false
      ```
    - Write the complete updated `.todo.md` file with the scheduled_task_id

### Working Tasks (WORK_MODE)

**CRITICAL: When to Enter VERIFY_MODE**
After EVERY task completion, you MUST check if all tasks are now complete or verified. This is the key trigger for VERIFY_MODE.

**CRITICAL: Tasks are NEVER deleted** - Only status changes.

1. **Check for .todo.md:**
   ```bash
   test -f .todo.md && echo "exists" || echo "missing"
   ```
   If missing → ERROR_MODE

2. **Check git status:**
   ```bash
   git status --porcelain
   ```
   If output not empty → CORRECTION_MODE

3. **Read frontmatter from .todo.md:**
   - Parse `.todo.md` to get `scheduled_task_mode` and `work_complete` values
   - If work_complete is "true" → All work done, notify user and exit
   - If scheduled_task_mode is "verify" → enter VERIFY_MODE
   - If scheduled_task_mode is "complete" → All work done, notify user and exit

4. **Find next task:**
   Parse `.todo.md` looking for first task with status "not started"

5. **If no "not started" tasks remain:**
   - Check if any tasks have status "complete" (not yet verified)
   - If yes → ALL WORK IS DONE!
     - Update `.todo.md` frontmatter: `scheduled_task_mode: verify`
     - Write updated frontmatter to `.todo.md`
     - Enter VERIFY_MODE immediately to verify completed work
   - If no "complete" tasks either → All tasks already verified, enter VERIFY_MODE to complete cleanup

6. **Update task to "in progress":**
   ```markdown
   - **Status:** in progress
   - **Updated:** [ISO timestamp]
   - **Notes:** Started work at [timestamp]
   ```

7. **Execute task autonomously using sub-agents/subordinates** - DO NOT wait for user input
   - Break down task into subtasks
   - Delegate subtasks to subordinate agents using call_subordinate tool
   - **Work on maximum 3 subtasks per session** - if more exist, complete up to 3 and note the rest for next session
   - Execute each subtask via sub-agents
   - Handle errors and issues independently
   - Use all available tools to solve problems

8. **If task is too large:**
   - Break down into smaller tasks
   - Add new tasks to `.todo.md` with unique IDs
   - Mark current task as partially complete with progress notes
   - Commit progress

9. **On completion:**
   ```markdown
   - **Status:** complete
   - **Updated:** [ISO timestamp]
   - **Notes:** [What was accomplished]
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
   - Parse `.todo.md` for all task statuses
   - If ALL tasks have status "complete" or "verified" (none are "not started" or "in progress" or "failed"):
     - Update frontmatter: `scheduled_task_mode: verify`
     - Write updated frontmatter to `.todo.md`
     - Enter VERIFY_MODE immediately to verify the completed work

10. **On failure:**
    ```markdown
    - **Status:** failed
    - **Updated:** [ISO timestamp]
    - **Notes:** [Detailed explanation of why it failed, error messages, attempts made]
    ```

    Create investigation task directly BEFORE the failed task:
    ```markdown
    ## Task X: Investigate: [Failed Task Title] Failure
    - **Status:** not started
    - **Created:** [ISO timestamp]
    - **Description:** Investigate and resolve the failure: [failure context]
    - **Notes:** [Context from failed task]
    ```

    Commit:
    ```bash
    git add -A
git commit -m "Failed: [Task Title] - Reason: [brief reason]. Created investigation task."
    ```

### Verifying Completed Tasks (VERIFY_MODE)

**When to enter VERIFY_MODE:**
- Scheduled task fires with `scheduled_task_mode: verify` in frontmatter, OR
- WORK_MODE completes last "not started" task and all remaining tasks are "complete"

**NOTE:** VERIFY_MODE may be entered multiple times - it verifies ONE task per run, then the next scheduled run will verify the next task. This is by design to prevent one agent from doing too much work.

**CRITICAL: Tasks are NEVER deleted** - Only status changes.

1. **Check for remaining "complete" tasks:**
   - Parse `.todo.md` looking for tasks with status "complete"
   - If none found → All tasks already verified, skip to step 6

2. **Get first "complete" task** from `.todo.md` (first task with status "complete", not yet "verified")

3. **Verify the work:**
   - Re-read task description
   - Check if requirements were met
   - Test code if applicable
   - Review documentation

4. **If verified:**
   - Change status from "complete" to **"verified"**
   - Add verification notes:
     ```markdown
     - **Status:** verified
     - **Verified:** [ISO timestamp]
     - **Verification Notes:** Quality check passed - [notes]
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
     ```bash
     git add -A
git commit -m "Verified: [Task Title] - Quality verified"
     ```
   - **The scheduled task will run again to verify the next "complete" task**

5. **If failed verification:**
   - Change status back to "in progress"
   - Add notes about what needs fixing
   - Update frontmatter: `scheduled_task_mode: work` (switch back to work mode)
   - Write updated frontmatter to `.todo.md`
   - Continue in WORK_MODE

6. **After all tasks verified (no "complete" tasks remain):**
   - **DISABLE the scheduled task** using `scheduler:update_task`:
     - Tool: scheduler:update_task
     - Arguments: 
       - task_id: [scheduled_task_id from frontmatter]
       - state: "disabled"
   - Update `.todo.md` frontmatter to indicate completion:
     ```yaml
     scheduled_task_mode: complete
     work_complete: true
     ```
   - Write updated frontmatter to `.todo.md`
   - Notify user that all tasks are complete and scheduled task has been disabled

### Handling Dirty Git State (CORRECTION_MODE)

1. **Get git diff** to see what changed:
   ```bash
git diff --stat
git diff
   ```

2. **Read .todo.md** to see last task status

3. **Check commit history:**
   ```bash
git log --oneline -10
   ```

4. **Determine action:**
   - If task was marked "complete" before dirty state → commit and continue
   - If task was in progress → continue working
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
   Ask user: "This project doesn't have task management set up. Would you like to start a new task list?"

---

## Frequency Options

**Recommended work frequencies for scheduled tasks:**

| Interval | Best For | Notes |
|----------|----------|-------|
| 15 minutes | Quick check-ins, very small tasks | May cause overlap with large tasks |
| 20 minutes | Small tasks | Minimum for most sessions |
| 30 minutes | Medium tasks (recommended default) | Good balance |
| 45 minutes | Medium to large tasks | Recommended for complex work |
| 60 minutes | Large, complex tasks | Prevents agent overlap |

**Guidance for Large Tasks:**

If your task list contains large or complex tasks, **choose a larger frequency (30-60 minutes)**. This ensures:
- Each session has enough time to make meaningful progress
- Previous session completes before next starts (no agent overlap)
- Sub-agents have sufficient time to complete subtasks
- Better git commit hygiene (one task per session)

| User Input | Cron Schedule |
|------------|---------------|
| Every 15 minutes | `*/15 * * * *` |
| Every 20 minutes | `*/20 * * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Every 45 minutes | `*/45 * * * *` |
| Every 60 minutes | `0 * * * *` |
| Hourly | `0 * * * *` |
| Daily | `0 0 * * *` |
| Weekly | `0 0 * * 0` |

Or accept custom cron expression from user.

---

## Available Scheduler Tools

**IMPORTANT:** Use these exact tool names and parameters:

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `scheduler:create_scheduled_task` | Create recurring task | name, system_prompt, prompt, schedule, dedicated_context |
| `scheduler:update_task` | Update or disable scheduled task | task_id, state (use "disabled" to disable) |
| `scheduler:find_task_by_name` | Find task by name | name |
| `scheduler:run_task` | Run task manually | uuid, context |
| `scheduler:delete_task` | Delete scheduled task | uuid (use update_task with state: "disabled" instead when possible) |

---

## Example Use Cases

### Example 1: Starting a New Project
- **User:** "I want to start a todo list for my project"
- **Agent:** Enters INIT_MODE, checks for existing files
- **Result:** `.todo.md`, `CHANGELOG.md` created with scheduled_task_id, scheduled task configured

### Example 2: Continuing Existing Project with New Goals
- **User:** "I want to add more tasks"
- **Agent:** Enters INIT_MODE, finds existing `.todo.md`
- **Agent:** Presents current tasks, asks: "Replace or Modify?"
- **User:** "Modify"
- **Agent:** Walks through current tasks, adds new ones
- **Result:** Updated `.todo.md` with new and existing tasks

### Example 3: Scheduled Work Session - All Work Complete
- **Trigger:** Scheduled task fires, agent enters WORK_MODE
- **Agent:** Checks scheduled_task_mode from frontmatter
- **Agent:** Finds no "not started" tasks but has "complete" tasks
- **Agent:** Updates frontmatter to `scheduled_task_mode: verify`, writes to file, enters VERIFY_MODE
- **Result:** Completed task is verified, status updated to "verified"

### Example 4: Verify Mode - Next Run Verifies Next Task
- **Trigger:** Scheduled task fires with `scheduled_task_mode: verify`
- **Agent:** Enters VERIFY_MODE, finds first "complete" task
- **Agent:** Verifies it, updates status to "verified", commits
- **Agent:** Checks for more "complete" tasks - if more exist, the next scheduled run will verify the next one
- **Result:** One task verified per run, eventually all verified

### Example 5: All Work Complete - Disable Scheduled Task
- **Trigger:** VERIFY_MODE finds no remaining "complete" tasks
- **Agent:** Reads scheduled_task_id, calls scheduler:update_task with state: "disabled"
- **Agent:** Updates frontmatter to `scheduled_task_mode: complete`, `work_complete: true`
- **Result:** Project complete, scheduled task disabled, .todo.md preserved with all tasks (status changed but never deleted)

### Example 6: User Requests Work
- **User:** "Work on the tasks"
- **Agent:** Enters WORK_MODE (checks git first), executes task
- **Result:** Task completed or failed with investigation task created

### Example 7: Dirty Git State
- **Trigger:** WORK_MODE finds dirty git
- **Agent:** Enters CORRECTION_MODE, analyzes state
- **Result:** Either commits and continues OR continues interrupted work

### Example 8: No Todo File
- **Trigger:** Agent in non-INIT mode finds no .todo.md
- **Agent:** Enters ERROR_MODE, creates error.md
- **Result:** User prompted to start task management or recurring task disabled

---

## Edge Cases

1. **No tasks in .todo.md**
   - Ask user to add tasks before scheduling

2. **All tasks failed**
   - Keep failed tasks with investigation tasks
   - Agent will work on investigation tasks first

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
   - The frontmatter `scheduled_task_mode` field controls which mode runs
   - WORK_MODE updates this to "verify" when all tasks complete
   - VERIFY_MODE updates this to "work" if verification fails and work is needed

10. **Task verification takes multiple runs**
    - VERIFY_MODE verifies ONE task per scheduled run
    - This is intentional to prevent agent overload
    - The next scheduled run will verify the next "complete" task

---

## Fundamental Principles

### CRITICAL: Tasks are NEVER deleted
- Tasks remain in `.todo.md` forever
- Only status changes: not started → in progress → complete → verified (or failed)
- This preserves the complete history of work done

### CRITICAL: Scheduled Task Handling
- The recurring scheduled task should be DISABLED when all work is complete
- Use `scheduler:update_task` with `state: "disabled"` to disable the task
- The .todo.md file itself is NEVER deleted

---

## Scheduled Task Prompt Template

When creating the recurring task, use this prompt:

```
You are running a scheduled work session for the todo-manager skill.

Project: [PROJECT NAME]
Task File: .todo.md

IMPORTANT: Check the scheduled_task_mode and work_complete in .todo.md frontmatter FIRST:
- If work_complete is "true": All work is done, notify user and exit
- If scheduled_task_mode is "complete": All work is done, notify user and exit
- If scheduled_task_mode is "verify": Execute VERIFY_MODE
- If scheduled_task_mode is "work" OR NOT SET: Execute WORK_MODE

Instructions:
1. Load the todo-manager skill
2. Read .todo.md and parse the frontmatter for scheduled_task_mode and work_complete
3. Execute the appropriate mode based on the mode values
4. Do not wait for user input - work autonomously
5. Handle any errors that arise
6. Report completion status when done

Remember: Use all available tools to complete tasks. Do not ask for user input unless absolutely necessary.
```

---

## Tools & Resources

### Required Tools
- `code_execution_tool`: For git operations, file read/write
- `scheduler:create_scheduled_task`: For creating scheduled tasks (returns UUID)
- `scheduler:update_task`: For disabling scheduled task (use state: "disabled")
- `scheduler:find_task_by_name`: For finding existing tasks
- `document_query`: For reading task files
- `memory_*`: For storing project context if needed

### File Locations
- Task file: `.todo.md` (project root) - NEVER deleted
- Changelog: `CHANGELOG.md` (project root)
- Error file: `error.md` (project root)

---

## Notes

- Always use ISO 8601 timestamps: `YYYY-MM-DDTHH:MM:SSZ`
- The skill assumes it's running in the project directory
- Commits should be atomic - one task per commit
- Use descriptive commit messages that match changelog entries
- Investigation tasks should have clear failure context
- When in doubt, prefer continuing work over asking questions
- Check git status before every work session
- Quality verification is critical - don't just mark complete
- **CRITICAL:** When existing tasks are found, ALWAYS ask user whether to replace or modify - never automatically reset
- **CRITICAL:** Recommend larger frequencies (30-60 min) for large tasks to prevent agent overlap
- **CRITICAL:** After completing ANY task in WORK_MODE, ALWAYS check if ALL tasks are now complete/verified. If so, update `scheduled_task_mode: verify`, write to file, and enter VERIFY_MODE immediately.
- **CRITICAL:** In VERIFY_MODE, when a task passes verification, update its status to "verified" (NOT deleted)
- **CRITICAL:** Always save the scheduled_task_id from scheduler:create_scheduled_task to the frontmatter - this is required to disable the task later
- **CRITICAL:** Tasks are NEVER deleted from .todo.md - only status changes
- **CRITICAL:** Use scheduler:update_task with state: "disabled" to disable the scheduled task when work is complete

---

*Skill Version: 1.5 | Author: Agent Zero | Based on agentskills.io specification*

---

## Version History

- **1.5** - Fixed: scheduler:update_task DOES exist with state parameter. Use scheduler:update_task with state: "disabled" to disable scheduled task (not delete). Added work_complete check at start of WORK_MODE.
- **1.4** - Clarified: tasks NEVER deleted (only status changes), scheduled task removed using scheduler:delete_task when complete, added work_complete flag to frontmatter
- **1.3** - Fixed critical bugs: scheduler:update_task replaced with scheduler:delete_task, added scheduled_task_id saving in INIT_MODE, fixed VERIFY_MODE to verify one task per run with loop back, added scheduled_task_mode check at start of WORK_MODE
- **1.2** - Added VERIFY_MODE trigger mechanism: WORK_MODE now checks if all tasks complete after each task, updates scheduled_task_mode to "verify", and enters VERIFY_MODE immediately. Verified tasks now marked as "verified" status.
- **1.1** - Added replace/modify workflow for existing todo lists and frequency recommendations (15/20/30/45/60 min) with guidance for large tasks
- **1.0** - Initial release
