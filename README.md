# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Four algorithms were added to make the scheduler more practical:

- **Sorting by time** — `Scheduler.sort_by_time()` returns tasks in chronological order using `sorted()` with a `lambda` key on `preferred_time`. Tasks with no preferred time are placed at the end (treated as `23:59`). The original priority-sorted list is left untouched.

- **Filtering** — `Scheduler.filter_tasks(pet_name, status)` returns a subset of assigned tasks. Either argument can be omitted to skip that filter, or both can be combined (e.g. pending tasks for a specific pet only).

- **Recurring tasks** — `Task` now carries a `frequency` field (`"once"` / `"daily"` / `"weekly"`) and a `due_date`. Calling `Scheduler.mark_task_complete()` marks the task done and automatically spawns the next occurrence using Python's `timedelta` (+1 day for daily, +7 days for weekly), adding it directly to the pet's task list so it appears in the next generated plan.

- **Conflict detection** — `Scheduler.get_conflict_warnings()` groups tasks by `preferred_time` and returns a human-readable warning string for every time slot that holds more than one task. It never raises an exception — callers check `if warnings` and display or log as needed.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
