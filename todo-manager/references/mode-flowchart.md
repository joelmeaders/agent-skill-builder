# Todo Manager Mode Flowchart

## Mode Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY POINT                                  │
│         (User requests task management)                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │  Is .todo.md present?  │
                 └──────────┬─────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
             YES                          NO
              │                           │
              ▼                           ▼
    ┌──────────────────┐    ┌──────────────────────────────────┐
    │ User requesting │    │  Is this INIT_MODE request?      │
    │ work on tasks?  │    └──────────────┬───────────────────┘
    └────────┬─────────┘                   │
             │                    ┌─────────┴─────────┐
      ┌──────┴──────┐          │                  │
      │             │         YES                  NO
      YES          NO          │                  │
      │             │          ▼                  ▼
      ▼             │   ┌───────────┐  ┌──────────────────┐
┌───────────┐       │   │   INIT    │  │ Create error.md  │
│   WORK    │       │   │   MODE    │  │ + ERROR_MODE     │
│   MODE    │       │   └───────────┘  └──────────────────┘
└───────────┘       │
                    │
                    ▼
         ┌─────────────────────────┐
         │   Check Git Status      │
         └───────────┬─────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
        CLEAN               DIRTY
          │                     │
          ▼                     ▼
   ┌─────────────┐    ┌──────────────────┐
   │ Find next   │    │   CORRECTION    │
   │ "not        │    │     MODE        │
   │  started"  │    └────────┬─────────┘
   │ task        │             │
   └──────┬──────┘             │
          │                    ▼
   ┌──────┴──────┐    ┌──────────────────────┐
   │             │    │ Determine last task  │
  FOUND      NOT │    │ status & continue    │
   │        FOUND│    └──────────────────────┘
   ▼             │
┌────────┐       │
│  WORK  │       │
│  TASK  │       │
└───┬────┘       │
    │            │
    ▼            │
┌────────────────────┐
│  VERIFY_MODE      │
│  (all complete)   │
└────────┬──────────┘
         │
         ▼
   ┌────────────┐
   │ Verify     │
   │ first      │
   │ "complete" │
   │ task       │
   └─────┬──────┘
         │
    ┌────┴────┐
    │          │
  PASS     FAIL
    │          │
    ▼          ▼
┌─────────┐ ┌────────────────┐
│ Delete  │ │ Set back to    │
│ task +  │ │ "in progress"  │
│ commit  │ │ + notes        │
└─────────┘ └────────────────┘
```

## Detailed Mode Transitions

### INIT_MODE (Initialization)
```
Trigger: User wants to start task management

1. Check if .todo.md exists
   ├─ Exists → Ask: "Reset or continue?"
   │  ├─ Reset → Clear tasks, keep file
   │  └─ Continue → Skip to step 5
   │
   └─ Not exists → Create .todo.md
       └─ Create CHANGELOG.md if not exists

2. Ask user for tasks
   └─ Populate .todo.md with tasks (status: "not started")

3. Ask user for frequency
   └─ Options: 5min, 15min, 30min, hourly, daily, weekly

4. Create scheduled task
   └─ Use scheduler:create_scheduled_task

5. Confirm with user
   └─ "Task management ready!"
```

### WORK_MODE (Task Execution)
```
Trigger: Scheduled task fires OR User says "work on tasks"

1. Check .todo.md exists
   ├─ YES → Continue
   └─ NO → ERROR_MODE

2. Check git status
   ├─ Clean → Continue to step 3
   └─ Dirty → CORRECTION_MODE

3. Find first task with status "not started"
   ├─ Found → Continue to step 4
   └─ Not found → VERIFY_MODE

4. Set task to "in progress"
   └─ Add timestamp to notes

5. Work task AUTONOMOUSLY
   └─ DO NOT wait for user input

6. Task completion check
   ├─ Success → Set status "complete"
   │             Add completion notes
   │             Update CHANGELOG.md
   │             Commit changes
   │
   └─ Failure → Set status "failed"
                 Add failure notes
                 Create investigation task (insert before failed)
                 Commit changes
```

### VERIFY_MODE (Quality Review)
```
Trigger: All tasks "complete" OR first task is "complete"

1. Get first task with status "complete"

2. Review task
   ├─ Description
   ├─ Completion notes
   └─ Check requirements met

3. Verification result
   ├─ Pass → Delete task from .todo.md
   │          Update CHANGELOG.md (VERIFIED)
   │          Commit changes
   │          → Return to WORK_MODE
   │
   └─ Fail → Set status back to "in progress"
              Add notes about what needs fixing
              → Continue in WORK_MODE
```

### CORRECTION_MODE (Git State Recovery)
```
Trigger: Git status shows uncommitted changes

1. Get git diff
   └─ See what changed

2. Read .todo.md
   └─ Find last task status

3. Check commit history
   └─ Look for recent task commits

4. Determine action
   ├─ Task was complete (status = "complete")
   │  └─ Commit changes + Continue WORK_MODE
   │
   ├─ Task was in progress
   │  └─ Continue working in WORK_MODE
   │
   └─ Unclear
      └─ Commit with "WIP" + Continue WORK_MODE
```

### ERROR_MODE (Error Handling)
```
Trigger: .todo.md not found (non-INIT_MODE)

1. Create error.md
   └─ Error: "Project does not contain .todo.md"
   └─ Timestamp
   └─ Context
   └─ Resolution

2. Check if error.md exists with same info
   ├─ Same error exists
   │  ├─ Find recurring work task
   │  └─ Cancel task + Notify user
   │
   └─ New error
      └─ Ask user: "Start task management?"
```

## File Locations

| File | Location | Purpose |
|------|----------|--------|
| `.todo.md` | Project root | Task list with status |
| `CHANGELOG.md` | Project root | History of completed work |
| `error.md` | Project root | Error notifications |

## Cron Schedule Options

| Frequency | Cron Expression |
|-----------|----------------|
| Every 5 minutes | `*/5 * * * *` |
| Every 15 minutes | `*/15 * * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Hourly | `0 * * * *` |
| Daily | `0 0 * * *` |
| Weekly | `0 0 * * 0` |

## Task Status Values

- `not started` - Task queued, not yet worked
- `in progress` - Currently being worked
- `complete` - Finished, needs verification
- `failed` - Could not complete, needs investigation

## Key Principles

1. **Autonomous Execution** - Never wait for user input in WORK_MODE
2. **Atomic Commits** - One task per commit
3. **Quality First** - Verify before deleting completed tasks
4. **Git Hygiene** - Always check status before working
5. **Error Recovery** - Investigate failures, don't just mark failed
