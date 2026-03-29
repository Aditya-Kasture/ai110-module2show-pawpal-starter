import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — Owner persists across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_time = st.number_input(
        "Available time today (minutes)", min_value=30, max_value=480, value=120
    )

if st.button("Set owner"):
    st.session_state.owner = Owner(owner_name, int(available_time))
    st.success(f"Owner set: {owner_name} ({available_time} min available)")

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=3.0, step=0.5)

if st.button("Add pet"):
    if st.session_state.owner is None:
        st.session_state.owner = Owner(owner_name, int(available_time))
    pet = Pet(pet_name, species, float(age))
    st.session_state.owner.add_pet(pet)
    st.success(f"Added {pet.summary()}")

if st.session_state.owner and st.session_state.owner.pets:
    st.caption("Pets: " + " · ".join(p.summary() for p in st.session_state.owner.pets))

# ---------------------------------------------------------------------------
# Add a task
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    task_time = st.text_input("Time (HH:MM)", value="07:00")
with col5:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

pet_for_task = None
if st.session_state.owner and st.session_state.owner.pets:
    pet_for_task = st.selectbox(
        "Assign to pet",
        options=[p.name for p in st.session_state.owner.pets],
    )

if st.button("Add task"):
    if st.session_state.owner is None:
        st.session_state.owner = Owner(owner_name, int(available_time))
    task = Task(task_title, int(duration), priority, time=task_time, frequency=frequency)
    if pet_for_task:
        pet_obj = next(
            (p for p in st.session_state.owner.pets if p.name == pet_for_task), None
        )
        if pet_obj:
            pet_obj.add_task(task)
        else:
            st.session_state.owner.add_task(task)
    else:
        st.session_state.owner.add_task(task)
    st.success(f"Added: {task_title} at {task_time}")

# Show current tasks
if st.session_state.owner:
    all_tasks = st.session_state.owner.all_tasks()
    if all_tasks:
        st.write("**Current tasks:**")
        st.table(
            [
                {
                    "Pet": t.pet_name or "—",
                    "Task": t.title,
                    "Time": t.time,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                }
                for t in all_tasks
            ]
        )

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or not st.session_state.owner.all_tasks():
        st.warning("Set an owner, add at least one pet and task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.build_plan()

        conflicts = scheduler.detect_conflicts()
        for warning in conflicts:
            st.warning(f"⚠ {warning}")

        if plan:
            st.success(
                f"Scheduled {len(plan)} tasks — "
                f"{scheduler.total_scheduled_minutes()} min "
                f"of {st.session_state.owner.available_minutes_per_day} min available"
            )
            st.table(
                [
                    {
                        "Time": t.time,
                        "Task": t.title,
                        "Pet": t.pet_name or "—",
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                    }
                    for t in sorted(plan, key=lambda t: t.time)
                ]
            )
            with st.expander("Full explanation"):
                st.text(scheduler.explain_plan())
        else:
            st.error("No tasks fit within the available time.")

# Reset button
if st.session_state.owner and st.button("Reset"):
    st.session_state.owner = None
    st.rerun()
