---
title: "Claude Code in Action - Steering Long Sessions"
source_url: "https://app.notion.com/p/3b3380860dab8004a59ee2cbbc657652"
---

# Claude Code in Action - Steering Long Sessions

## Scope the work first with plan mode

Before Claude writes a single line, get it to lay out a plan.

## Steer while Claude works

### Compact

Compact summarizes your conversation, uses that summary as the new context, and deletes the old messages.
```
/compact Focus on the --version flag implementation
```

### Rewind

Rewind takes you to your last checkpoint. From the rewind menu you get a few options:
- **Restore code and conversation** - roll back both together.
- **Restore conversation** - roll back just the chat.
- **Restore code** - roll back just the files.
- **Summarize from here** - summarizes everything after the checkpoint. Great if you had a side conversation and just want to free up some space.
- **Summarize up to here** - summarizes everything before the checkpoint. Great when you had a long setup phase you want to compress, but you want to keep the implementation parts intact.

## Let Claude run more autonomously

### Goal

Goal sets a completion condition.
```
/goal all tests in src/billing pass, and the type checker reports zero errors
```
To cancel it, run `/goal clear`.

### Loop

Loop runs a prompt on an interval between turns, either fixed or self-paced.

### Run parallel work with worktrees

Instead of sessions stepping on each other, each one gets its own independent file tree.

## Putting it together

1. Scope your work first, then steer.
2. Direct your compaction so the summary keeps what matters.
3. Use the rewind menu to course correct when Claude drifts.
4. Set a goal when you can describe "done" better than you can describe the steps.
5. Run parallel work in worktrees.
