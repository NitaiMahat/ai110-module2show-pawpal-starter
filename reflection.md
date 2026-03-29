# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Initial design includes four main classes:

- `Owner`: stores owner identity, contact, preferences, and availability; methods to update preferences/availability and provide summaries.
- `Pet`: stores individual pet profile, species, age, health notes, and care requirements; methods to update health notes and indicate task needs.
- `Task`: stores pet care tasks with identifiers, duration, priority, preferred time, and status; methods to complete, reschedule, and revise task details.
- `Scheduler`: orchestrates task assignment for a day, checks constraints, evaluates ordering, and returns today's task list.

Core user actions:
  - Add and manage pets and owner details (basic owner + pet info entry).
  - Add and edit care tasks, including duration and priority (walks, feeding, meds, grooming, enrichment).
  - Generate and view a daily schedule that respects available time and priorities, with explanatory reasoning.

**b. Design changes**

Yes, the design changed significantly during implementation. The key differences between the initial UML and the final `pawpal_system.py` are:

| Area | Initial UML | Final implementation |
|---|---|---|
| Class names | `DailyPlan`, `PetCareTask` | `Scheduler`, `Task` (more natural Python names) |
| Ownership | `Owner` had no `pets` list; relationship was implicit | `Owner.pets: List[Pet]` and `Pet.tasks: List[Task]` make composition explicit in code |
| Task attributes | `priority: String`, `preferred_time: String` | `priority: int`, `preferred_time: time` — using proper types allows arithmetic sorting |
| Task recurrence | Not modelled | `frequency: str` + `due_date: date` + `next_occurrence()` added to support daily/weekly tasks |
| Scheduler methods | `generate_plan`, `score_task_order`, `conflict_check`, `get_todays_tasks` | Added `sort_by_time()`, `filter_tasks()`, `mark_task_complete()`, `get_conflict_warnings()` |
| Conflict reporting | `conflict_check() → bool` | `get_conflict_warnings() → List[str]` returns human-readable per-conflict messages |

The biggest single change was making `Owner → Pet → Task` a true composition chain (each class holds a list of the next), rather than the original design where `DailyPlan` centrally "managed" and "assigned" everything. This made the data flow simpler and allowed `Owner.get_all_tasks()` to work naturally.

The final diagram is saved as `uml_final.png`. Items marked ★ in the diagram were added after the initial design.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Priority (most important)** — every task has a numeric priority (1–10). `generate_plan()` sorts tasks by `-priority` first so urgent care (medications, vet visits) always appears at the top of the plan regardless of time of day.
2. **Preferred time** — used as a tiebreaker when two tasks share the same priority, and as the primary sort key in `sort_by_time()`. Tasks with no preferred time are treated as `23:59` so they fall to the end rather than being excluded.
3. **Status** — only `pending` tasks enter the plan; `done` tasks are filtered out at plan-generation time so completing a task immediately clears it from the schedule.

Priority was chosen as the primary constraint because a pet owner's first concern is whether critical care (medicine, feeding) gets done at all — the exact time is secondary. Time ordering is offered as an optional view rather than the default so the plan stays focused on importance first.

**b. Tradeoffs**

The conflict detector compares tasks by exact `preferred_time` equality — two tasks at `09:00` trigger a warning, but a 45-minute task starting at `09:00` and a 10-minute task starting at `09:30` do not, even though they overlap in real time.

This is a deliberate simplification. Computing true overlap requires a start time *and* an end time (start + duration) for every task, then checking each pair of intervals — an O(n²) comparison. For a typical day with fewer than 20 tasks the performance difference is negligible, but the exact-match approach is far easier to read, test, and explain to a non-technical user. The tradeoff is acceptable here because preferred times are usually set to round hours and the scheduler's primary job is to surface obvious double-bookings, not to act as a calendar solver.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used at every phase, but for different kinds of work:

- **Design brainstorming** — during Phase 1, I used Copilot Chat to evaluate whether the initial four-class design covered all the user scenarios (add pet, schedule tasks, mark done). It surfaced the missing `pets` list on `Owner` and `tasks` list on `Pet` before any code was written, which saved a refactor later.
- **Algorithm suggestions** — for sorting and filtering I asked Copilot to explain how Python's `sorted()` and lambda keys work, then adapted the explanation into `sort_by_time()`. The AI gave the concept; I decided the method signature and where it lived on `Scheduler`.
- **Docstrings** — after each implementation phase I used the "Generate documentation" action to draft 1-line docstrings, then edited them for accuracy and tone.
- **Debugging** — when the nested `st.button("Mark done")` inside `st.button("Generate schedule")` wasn't working, I described the Streamlit re-run model to Copilot and asked why the state wasn't persisting. The explanation of `st.session_state` persistence led directly to storing the `Scheduler` object in session state.

The most effective prompts were specific and gave context: *"In Streamlit, if I store X inside an `if st.button():` block, what happens to X when the user clicks a different button?"* gave a precise, usable answer. Vague prompts like *"make the schedule better"* produced generic code that didn't fit the existing design.

**b. Judgment and verification**

When implementing `filter_tasks()`, Copilot suggested collapsing the two-pass filter into a single list comprehension with both conditions inlined:

```python
return [t for t in self.assigned_tasks
        if (pet_name is None or t.pet_name == pet_name)
        and (status is None or t.status == status)]
```

I kept the two-pass version instead:

```python
result = self.assigned_tasks
if pet_name is not None:
    result = [t for t in result if t.pet_name == pet_name]
if status is not None:
    result = [t for t in result if t.status == status]
return result
```

The single-comprehension version is more "Pythonic" but the two-pass version makes it immediately obvious that each filter is independent and optional — a reader does not have to parse the boolean logic to understand the behavior. Since this method would be called from the UI and possibly extended with more filters later, readability mattered more than brevity. I verified both versions produced identical output by running them against the same task list in `main.py`.

**c. VS Code Copilot — specific experience**

*Most effective features:*

- **Inline Chat on specific methods** was the most useful feature. Highlighting `conflict_check()` and asking "how can I return a warning message per conflict instead of a bool?" gave a focused answer that fit directly into the existing method shape, rather than rewriting the whole class.
- **`#file:` context in chat** allowed me to ask questions like "based on `#file:pawpal_system.py`, what changes would make the UML more accurate?" and get answers that referenced the actual code rather than generic examples.
- **Generate documentation action** saved time on docstrings without changing any logic — it only touched the comment layer.

*Using separate chat sessions per phase:*

Keeping a dedicated chat session for Phase 3 (algorithms) and a separate one for Phase 4 (UI wiring) meant each session stayed on topic. When I started a new session for the Streamlit work, Copilot wasn't carrying assumptions from the algorithm discussion, which prevented it from suggesting algorithm changes when I only wanted UI help. Each session had a narrow scope and a clear exit — that structure mirrors how good software is built: one concern at a time.

*Being the lead architect:*

The clearest lesson was that AI is fast at generating plausible code but has no stake in your design. It will happily suggest a solution that works in isolation but breaks an assumption you made three classes ago. Every AI suggestion needed to be evaluated against two questions: (1) does this fit the existing data model, and (2) who owns this responsibility? When Copilot suggested adding conflict-detection logic directly inside `Task.mark_done()`, I moved it to `Scheduler.mark_task_complete()` instead, because `Task` should not know about the full schedule — that is `Scheduler`'s job. The AI generated the code; the architectural boundary was a human decision.

---

## 4. Testing and Verification

**a. What you tested**

Two automated pytest tests were written in `tests/test_pawpal.py`:

1. **`test_mark_done_changes_status`** — creates a `Task` with `status="pending"`, calls `mark_done()`, and asserts the status is now `"done"`. This test is important because the entire schedule display logic, the filter-by-status feature, and the recurring task spawn logic all depend on `status` being reliably updated by this one method.

2. **`test_add_task_increases_pet_task_count`** — creates a `Pet` with no tasks, calls `add_task()`, and asserts `len(pet.tasks) == 1`. This test verifies the composition relationship: `Pet` must hold its tasks for `Owner.get_all_tasks()` and `Scheduler.generate_plan()` to work at all.

Both tests were run after every phase to confirm that new features (recurring tasks, sorting, filtering) did not break the two foundational behaviors.

Manual verification was done through `main.py`, which exercises sorting, filtering, and the full recurring-task flow end-to-end with printed output that can be inspected visually.

**b. Confidence**

Confidence is moderate-to-high for the core path: adding a pet, adding tasks, generating a plan, and marking tasks done all work correctly as demonstrated by the running app and the terminal demo.

Edge cases I would test next with more time:

- **Two pets with the same name** — `filter_tasks(pet_name=...)` and `mark_task_complete()` both match by name string; duplicate pet names would cause incorrect behavior.
- **Marking the same task done twice** — calling `mark_task_complete()` on an already-`done` task would still increment the recur counter and potentially spawn a duplicate.
- **Empty `preferred_time` with `sort_by_time()`** — currently tasks without a time sort to the end (`23:59`), but the behavior should be explicitly tested rather than assumed.
- **Very large priority values** — `score_task_order()` divides by task count; a list with one task of priority 1000 would produce a misleading "average" score.

---

## 5. Reflection

**a. What went well**

The composition chain (`Owner → Pet → Task`) ended up being the strongest part of the design. Once `Owner.get_all_tasks()` existed, every other feature — the scheduler, the filters, the Streamlit table, the recurring task spawn — could be built on top of it without touching the underlying data structure. Making the relationships explicit in code (rather than leaving them implicit in a diagram) paid off consistently throughout the project.

**b. What you would improve**

The `Scheduler` class accumulates too much responsibility by the end of the project. It handles plan generation, sorting, filtering, conflict detection, and recurring task management. In a next iteration I would extract `RecurrenceManager` (handling `next_occurrence` and `mark_task_complete`) and `ConflictDetector` (handling `get_conflict_warnings`) into separate classes. This would make each class easier to test in isolation and make it clearer which object to reach for when adding a new feature.

I would also replace the plain `status: str` field on `Task` with a proper Python `Enum` (`TaskStatus.PENDING`, `TaskStatus.DONE`). String comparisons like `task.status != "done"` scattered across the codebase are fragile — a typo produces a silent bug rather than an error.

**c. Key takeaway**

The most important thing I learned is that AI collaboration requires you to maintain a mental model of your own system that the AI does not have. The AI sees the code it was just shown; you see the whole architecture, the design decisions made three phases ago, and the direction the project is heading. That asymmetry means the human's job is not to write code — it is to decide what belongs where, what each class is responsible for, and when a technically correct suggestion is architecturally wrong. The AI is a fast, tireless implementer. The lead architect is still you.
