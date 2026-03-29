from datetime import datetime, time, date
from pawpal_system import Owner, Pet, Task, Scheduler


def print_tasks(label: str, tasks) -> None:
    print(f"\n{label}")
    if not tasks:
        print("  (none)")
        return
    for task in tasks:
        preferred = task.preferred_time.strftime('%H:%M') if task.preferred_time else 'Anytime'
        due = f", due {task.due_date}" if task.due_date else ""
        print(
            f"  [{task.status}] {task.pet_name}: {task.task_type}"
            f" (priority {task.priority}, {task.duration_minutes} min"
            f", at {preferred}, {task.frequency}{due})"
        )


def main():
    owner = Owner(name='Alex', contact_info='alex@example.com')
    owner.set_availability(['08:00-10:00', '17:00-20:00'])

    pet1 = Pet(name='Buddy', species='Dog', breed='Labrador', age=5)
    pet2 = Pet(name='Mittens', species='Cat', age=3)

    # Tasks added intentionally out of chronological order to prove sort_by_time()
    task1 = Task(
        task_id='t1', pet_name='Buddy', task_type='Walk',
        duration_minutes=30, priority=5, preferred_time=time(17, 0),
        frequency='daily', due_date=date.today(),
    )
    task2 = Task(
        task_id='t2', pet_name='Buddy', task_type='Feed',
        duration_minutes=10, priority=10, preferred_time=time(7, 30),
        frequency='daily', due_date=date.today(),
    )
    task3 = Task(
        task_id='t3', pet_name='Mittens', task_type='Medicine',
        duration_minutes=5, priority=8, preferred_time=time(9, 0),
        frequency='weekly', due_date=date.today(),
    )
    task4 = Task(
        task_id='t4', pet_name='Buddy', task_type='Grooming',
        duration_minutes=20, priority=3, preferred_time=time(11, 0),
        frequency='once',
    )

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet1.add_task(task4)
    pet2.add_task(task3)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(date=datetime.now())
    scheduler.generate_plan(owner)

    # ── Step 2a: Sorting ─────────────────────────────────────────────────────
    print_tasks("Sorted by priority (generate_plan default):", scheduler.assigned_tasks)
    print_tasks("Sorted by preferred time (sort_by_time):", scheduler.sort_by_time())

    # ── Step 2b: Filtering ───────────────────────────────────────────────────
    print_tasks("Filter — Buddy's tasks only:", scheduler.filter_tasks(pet_name='Buddy'))
    print_tasks("Filter — pending tasks only:", scheduler.filter_tasks(status='pending'))

    # ── Step 3: Recurring tasks ──────────────────────────────────────────────
    print("\n-- Marking t2 (Buddy: Feed, daily) as complete --")
    new_task = scheduler.mark_task_complete('t2', owner)
    if new_task:
        print(f"  Spawned next occurrence -> {new_task.task_id}: due {new_task.due_date}")

    print("\n-- Marking t3 (Mittens: Medicine, weekly) as complete --")
    new_task = scheduler.mark_task_complete('t3', owner)
    if new_task:
        print(f"  Spawned next occurrence -> {new_task.task_id}: due {new_task.due_date}")

    print("\n-- Marking t4 (Buddy: Grooming, once) as complete --")
    new_task = scheduler.mark_task_complete('t4', owner)
    print(f"  No recurrence spawned: {new_task is None}")

    # Rebuild plan to show recurring tasks now queued
    scheduler.generate_plan(owner)
    print_tasks("\nRebuilt plan (recurring tasks now queued):", scheduler.assigned_tasks)
    print(f"\nPlan score:      {scheduler.score_task_order():.2f}")
    print(f"Conflict flagged: {scheduler.conflict_check()}")


if __name__ == '__main__':
    main()
