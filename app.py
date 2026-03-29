import streamlit as st
from datetime import datetime

# Step 1: Import logic layer
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Step 2: Application "memory" via st.session_state ──────────────────────
# Streamlit re-runs the whole script on every interaction.
# We check whether the Owner already exists in the session "vault" before
# creating a new one, so data persists across button clicks.
if "owner" not in st.session_state:
    st.session_state.owner = None   # will be set when the user confirms their name

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0  # used to generate unique task IDs

# ── Owner setup ─────────────────────────────────────────────────────────────
st.subheader("1. Owner")
owner_name = st.text_input("Your name", value="Jordan")
owner_contact = st.text_input("Contact info (email / phone)", value="jordan@example.com")

if st.button("Set owner"):
    st.session_state.owner = Owner(name=owner_name, contact_info=owner_contact)
    st.success(f"Owner set to **{owner_name}**.")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ── Step 3a: Add a pet ───────────────────────────────────────────────────────
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
    # Wired to Owner.add_pet() → Pet constructor
    new_pet = Pet(
        name=pet_name,
        species=species,
        breed=breed or None,
        age=int(age),
    )
    owner.add_pet(new_pet)
    st.success(f"Added **{pet_name}** the {species}!")

if owner.pets:
    st.write("**Your pets:**")
    for pet in owner.pets:
        st.markdown(f"- {pet.describe()}")
else:
    st.info("No pets yet. Add one above.")

# ── Step 3b: Add a task to a pet ────────────────────────────────────────────
st.divider()
st.subheader("3. Add a Care Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox(
            "Which pet?", options=[p.name for p in owner.pets]
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            task_type = st.text_input("Task type", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.slider("Priority (1 = low, 5 = high)", 1, 5, 3)
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        # Generate a unique ID and wire to Pet.add_task() → Task constructor
        st.session_state.task_counter += 1
        task_id = f"t{st.session_state.task_counter}"
        new_task = Task(
            task_id=task_id,
            pet_name=target_pet_name,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
        )
        # Find the matching Pet object and call add_task()
        for pet in owner.pets:
            if pet.name == target_pet_name:
                pet.add_task(new_task)
                break
        st.success(f"Task **{task_type}** added for {target_pet_name}.")

    # Show all current tasks across every pet
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks:**")
        st.table(
            [
                {
                    "ID": t.task_id,
                    "Pet": t.pet_name,
                    "Task": t.task_type,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Status": t.status,
                }
                for t in all_tasks
            ]
        )
    else:
        st.info("No tasks yet.")

# ── Step 3c: Generate schedule ───────────────────────────────────────────────
st.divider()
st.subheader("4. Generate Today's Schedule")

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Wired to Scheduler.generate_plan()
        scheduler = Scheduler(date=datetime.now())
        plan = scheduler.generate_plan(owner)
        has_conflict = scheduler.conflict_check()
        avg_score = scheduler.score_task_order()

        st.success(scheduler.plan_description)
        st.metric("Average priority score", f"{avg_score:.1f}")
        if has_conflict:
            st.warning("⚠️ Two or more tasks share the same preferred time — consider rescheduling.")

        st.write("**Planned task order:**")
        for i, task in enumerate(plan, 1):
            st.markdown(
                f"{i}. **{task.task_type}** for {task.pet_name} "
                f"— {task.duration_minutes} min, priority {task.priority}"
            )

        # Mark tasks done
        st.write("---")
        st.write("**Mark a task as done:**")
        task_options = {f"{t.task_id}: {t.task_type} ({t.pet_name})": t for t in plan}
        chosen = st.selectbox("Select task", list(task_options.keys()))
        if st.button("Mark done"):
            task_options[chosen].mark_done()
            st.success(f"Marked '{task_options[chosen].task_type}' as done.")
