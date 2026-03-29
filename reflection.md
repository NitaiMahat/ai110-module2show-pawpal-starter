# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Initial design includes four main classes:

- `Owner`: stores owner identity, contact, preferences, and availability; methods to update preferences/availability and provide summaries.
- `Pet`: stores individual pet profile, species, age, health notes, and care requirements; methods to update health notes and indicate task needs.
- `Task`: stores pet care tasks with identifiers, duration, priority, preferred time, and status; methods to complete, reschedule, and revise task details.
- `Scheduler`: orchestrates task assignment for a day, checks constraints, evaluates ordering, and returns today’s task list.

Core user actions:
  - Add and manage pets and owner details (basic owner + pet info entry).
  - Add and edit care tasks, including duration and priority (walks, feeding, meds, grooming, enrichment).
  - Generate and view a daily schedule that respects available time and priorities, with explanatory reasoning.

**b. Design changes**

- I started with the four classes above and initially kept responsibilities minimal for clarity.
- After reviewing, I may add explicit relationships (e.g., `Owner` has a list of `Pet`, `Pet` has list of `Task`) during full implementation to keep data flow explicit.
- This is a planned refinement once scheduling behavior is implemented and tested.

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector compares tasks by exact `preferred_time` equality — two tasks at `09:00` trigger a warning, but a 45-minute task starting at `09:00` and a 10-minute task starting at `09:30` do not, even though they overlap in real time.

This is a deliberate simplification. Computing true overlap requires a start time *and* an end time (start + duration) for every task, then checking each pair of intervals — an O(n²) comparison. For a typical day with fewer than 20 tasks the performance difference is negligible, but the exact-match approach is far easier to read, test, and explain to a non-technical user. The tradeoff is acceptable here because preferred times are usually set to round hours and the scheduler's primary job is to surface obvious double-bookings, not to act as a calendar solver.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
