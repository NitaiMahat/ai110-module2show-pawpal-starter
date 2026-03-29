# PawPal+ — Pet Care Scheduling Assistant

A Streamlit app that helps a pet owner build and manage a smart daily care plan for one or more pets.

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_demo.png" target="_blank">
  <img src="/course_images/ai110/pawpal_demo.png" alt="PawPal+ running in the browser showing the task table, daily schedule, sort/filter controls, and conflict warnings" width="800">
</a>

*PawPal+ running at `localhost:8501` — owner and pet set up, a Morning walk task added, schedule generated with sort/filter controls visible.*

---

## Features

### Owner & Pet Management
- **Owner profile** — enter your name and contact info; the profile persists across the entire session.
- **Multi-pet support** — add as many pets as you need, each with a name, species, breed, and age.

### Task Management
- **Flexible task entry** — record any care task (walk, feed, meds, grooming, vet visit, etc.) with a duration, a priority score (1–10), and an optional preferred time.
- **Recurring tasks** — mark a task as `daily` or `weekly`; when you complete it the next occurrence is automatically scheduled using Python's `timedelta` (+1 day or +7 days) and added to the pet's queue.
- **One-time tasks** — tasks set to `once` are removed from the plan when completed with no follow-up.

### Smart Scheduling Algorithms
- **Priority-first planning** — `Scheduler.generate_plan()` sorts pending tasks by priority (high → low), using preferred time as a tiebreaker. High-urgency tasks always appear at the top of the plan.
- **Sort by time** — `Scheduler.sort_by_time()` re-orders the plan chronologically using a `lambda` key on `preferred_time`, so you can view the day in clock order. Tasks without a preferred time appear last.
- **Filter by pet or status** — `Scheduler.filter_tasks(pet_name, status)` returns a focused subset of the plan. Filters can be used independently or combined (e.g. "show only Buddy's pending tasks").
- **Conflict detection** — `Scheduler.get_conflict_warnings()` groups tasks by `preferred_time` and returns a human-readable warning message for every time slot that has more than one task assigned. Each conflict names the exact pets and tasks involved so the owner knows what to reschedule.

### Streamlit UI
- **Live schedule table** — the plan updates immediately after every change; sort order and filters are applied with inline controls (no page reload needed).
- **Per-conflict warning banners** — each scheduling conflict surfaces as its own `st.warning()` block, naming the time slot and the clashing tasks.
- **Mark done in-app** — select any pending task from a dropdown and mark it complete; recurring tasks spawn their next occurrence and a confirmation banner appears automatically.
- **Session persistence** — all owner, pet, task, and schedule data is held in `st.session_state`, so nothing is lost when you interact with the UI.

---

## Project Structure

```
pawpal_system.py   — core logic: Task, Pet, Owner, Scheduler classes
app.py             — Streamlit UI wired to the logic layer
main.py            — terminal demo showing sorting, filtering, and recurring tasks
tests/
  test_pawpal.py   — pytest tests for mark_done() and add_task()
uml_final.png      — final UML class diagram (updated from initial design)
generate_uml.py    — script used to render uml_final.png
reflection.md      — design decisions, tradeoffs, and AI collaboration notes
```

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the terminal demo

```bash
python main.py
```

### Run tests

```bash
python -m pytest
```

---

## Smarter Scheduling — Design Notes

Four algorithms power the scheduling layer:

| Feature | Method | How it works |
|---|---|---|
| Priority plan | `Scheduler.generate_plan()` | Sorts by `-priority`, then `preferred_time` as tiebreaker |
| Time ordering | `Scheduler.sort_by_time()` | `sorted()` with a `lambda` key; no-time tasks placed at 23:59 |
| Filtering | `Scheduler.filter_tasks()` | Two-pass list comprehension; each filter is optional |
| Conflict detection | `Scheduler.get_conflict_warnings()` | `defaultdict` buckets tasks by time; warns per busy slot |
| Recurring tasks | `Task.next_occurrence()` + `Scheduler.mark_task_complete()` | `timedelta` advances `due_date`; new Task added to pet's list |

**Key tradeoff:** conflict detection compares exact `preferred_time` values rather than true time intervals (start + duration). This keeps the algorithm simple and readable; see `reflection.md` section 2b for the full reasoning.
