import streamlit as st
from datetime import datetime, time

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state initialisation ─────────────────────────────────────────────
# Everything lives in st.session_state so data survives every Streamlit rerun.
if "owner" not in st.session_state:
    st.session_state.owner = None
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None   # persists between reruns so mark-done works
if "recur_notice" not in st.session_state:
    st.session_state.recur_notice = None  # message shown after a recurring task spawns

# ── 1. Owner ─────────────────────────────────────────────────────────────────
st.subheader("1. Owner")
col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Your name", value="Jordan")
with col_b:
    owner_contact = st.text_input("Contact (email / phone)", value="jordan@example.com")

if st.button("Set owner"):
    st.session_state.owner = Owner(name=owner_name, contact_info=owner_contact)
    st.session_state.scheduler = None   # reset schedule when owner changes
    st.success(f"Owner set to **{owner_name}**.")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ── 2. Pets ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader("2. Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        breed = st.text_input("Breed (optional)")
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    owner.add_pet(Pet(name=pet_name, species=species, breed=breed or None, age=int(age)))
    st.success(f"Added **{pet_name}** the {species}.")

if owner.pets:
    for pet in owner.pets:
        st.markdown(f"- {pet.describe()}")
else:
    st.info("No pets yet — add one above.")

# ── 3. Tasks ──────────────────────────────────────────────────────────────────
st.divider()
st.subheader("3. Add a Care Task")

if not owner.pets:
    st.info("Add a pet first.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_type = st.text_input("Task type", value="Morning walk")
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.slider("Priority (1 low → 10 high)", 1, 10, 5)
            frequency = st.selectbox("Recurrence", ["once", "daily", "weekly"])

        use_time = st.checkbox("Set a preferred time?")
        preferred_time = None
        if use_time:
            preferred_time = st.time_input("Preferred time", value=time(9, 0))

        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        st.session_state.task_counter += 1
        new_task = Task(
            task_id=f"t{st.session_state.task_counter}",
            pet_name=target_pet_name,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            preferred_time=preferred_time,
        )
        for pet in owner.pets:
            if pet.name == target_pet_name:
                pet.add_task(new_task)
                break
        st.session_state.scheduler = None  # stale schedule — force a regenerate
        st.success(f"Added **{task_type}** for {target_pet_name} ({frequency}).")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks:**")
        st.table([
            {
                "Pet": t.pet_name,
                "Task": t.task_type,
                "Min": t.duration_minutes,
                "Priority": t.priority,
                "Recurrence": t.frequency,
                "Time": t.preferred_time.strftime("%H:%M") if t.preferred_time else "—",
                "Status": t.status,
            }
            for t in all_tasks
        ])

# ── 4. Schedule ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("4. Daily Schedule")

if st.button("Generate / refresh schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task first.")
    else:
        sched = Scheduler(date=datetime.now())
        sched.generate_plan(owner)
        st.session_state.scheduler = sched
        st.session_state.recur_notice = None

# Show a recurring-task spawn notice that persists until the next generate
if st.session_state.recur_notice:
    st.info(st.session_state.recur_notice)

sched: Scheduler = st.session_state.scheduler  # may be None

if sched is None:
    st.caption("Click **Generate / refresh schedule** to build today's plan.")
else:
    # ── Conflict warnings (per conflict, not just a generic flag) ────────────
    warnings = sched.get_conflict_warnings()
    if warnings:
        for w in warnings:
            # Strip the "WARNING: " prefix — st.warning already adds visual weight
            st.warning(w.replace("WARNING: ", ""))
    else:
        st.success(f"No conflicts — {sched.plan_description}")

    st.metric("Average priority score", f"{sched.score_task_order():.1f} / 10")

    # ── View controls ────────────────────────────────────────────────────────
    col_sort, col_filter_pet, col_filter_status = st.columns(3)
    with col_sort:
        sort_mode = st.radio("Sort by", ["Priority", "Time"], horizontal=True)
    with col_filter_pet:
        pet_options = ["All"] + [p.name for p in owner.pets]
        filter_pet = st.selectbox("Filter by pet", pet_options)
    with col_filter_status:
        filter_status = st.selectbox("Filter by status", ["All", "pending", "done"])

    # Apply sort
    tasks_to_show = sched.sort_by_time() if sort_mode == "Time" else sched.assigned_tasks

    # Apply filters
    pet_arg = None if filter_pet == "All" else filter_pet
    status_arg = None if filter_status == "All" else filter_status
    tasks_to_show = sched.filter_tasks(pet_name=pet_arg, status=status_arg) if (pet_arg or status_arg) else tasks_to_show

    # ── Schedule table ───────────────────────────────────────────────────────
    if not tasks_to_show:
        st.info("No tasks match the current filters.")
    else:
        rows = []
        for i, t in enumerate(tasks_to_show, 1):
            rows.append({
                "#": i,
                "Pet": t.pet_name,
                "Task": t.task_type,
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority,
                "Time": t.preferred_time.strftime("%H:%M") if t.preferred_time else "Anytime",
                "Recurrence": t.frequency,
                "Status": t.status,
            })
        st.table(rows)

    # ── Mark a task complete ─────────────────────────────────────────────────
    st.write("**Mark a task as done:**")
    pending = [t for t in sched.assigned_tasks if t.status == "pending"]
    if not pending:
        st.success("All tasks are done for today!")
    else:
        task_labels = {f"{t.task_id} — {t.task_type} ({t.pet_name})": t.task_id for t in pending}
        chosen_label = st.selectbox("Select task to complete", list(task_labels.keys()))
        if st.button("Mark done"):
            chosen_id = task_labels[chosen_label]
            new_task = sched.mark_task_complete(chosen_id, owner)
            # Refresh the plan so the table reflects the new status
            sched.generate_plan(owner)
            if new_task:
                due = f" due {new_task.due_date}" if new_task.due_date else ""
                st.session_state.recur_notice = (
                    f"Recurring task spawned: **{new_task.task_type}** "
                    f"for {new_task.pet_name}{due} ({new_task.frequency})"
                )
            st.rerun()
