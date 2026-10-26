import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, to_hhmm, to_minutes

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit reruns this script on every click, so keep the Owner in session_state.
# It is created only the first time; later runs reuse the same object.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Time available today (minutes)",
            min_value=0,
            max_value=1440,
            value=owner.available_minutes,
        )
    )

st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        breed = st.text_input("Breed (optional)")
    if st.form_submit_button("Add pet"):
        name = new_pet_name.strip()
        if not name:
            st.error("Enter a name for the pet.")
        elif any(p.name == name for p in owner.pets):
            st.error(f"You already have a pet named {name}.")
        else:
            owner.add_pet(Pet(name=name, species=species, breed=breed.strip()))
            st.success(f"Added {name}.")

if owner.pets:
    st.table(
        [
            {"Name": p.name, "Species": p.species, "Breed": p.breed or "-", "Tasks": len(p.tasks)}
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.subheader("Tasks")
if owner.pets:
    with st.form("add_task", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        col4, col5 = st.columns(2)
        with col4:
            frequency = st.selectbox("Frequency", ["daily", "weekly"])
        with col5:
            preferred = st.text_input("Preferred time (HH:MM, optional)")
        if st.form_submit_button("Add task"):
            preferred = preferred.strip() or None
            try:
                if preferred:
                    to_minutes(preferred)
            except ValueError:
                st.error("Preferred time must look like 08:30.")
            else:
                pet = next(p for p in owner.pets if p.name == pet_choice)
                pet.add_task(
                    Task(
                        title=task_title.strip(),
                        duration=int(duration),
                        priority=priority,
                        frequency=frequency,
                        preferred_time=preferred,
                    )
                )
                st.success(f"Added {task_title} for {pet_choice}.")

    tasks = owner.get_all_tasks()
    if tasks:
        st.table(
            [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Minutes": t.duration,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                    "Preferred time": t.preferred_time or "-",
                }
                for t in tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.caption("Add a pet first, then you can give it tasks.")

st.divider()

st.subheader("Build Schedule")
day_start = st.text_input("Day starts at (HH:MM)", value="08:00")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner, day_start=day_start)
    plan = scheduler.generate_plan()
    if plan:
        st.success(f"Today's schedule for {owner.name}'s pets")
        st.table(
            [
                {
                    "Time": f"{start}-{to_hhmm(to_minutes(start) + task.duration)}",
                    "Pet": task.pet_name,
                    "Task": task.title,
                    "Why": reason,
                }
                for start, task, reason in plan
            ]
        )
    else:
        st.warning("Nothing to schedule. Add tasks that fit in the time available.")
    for conflict in scheduler.detect_conflicts():
        st.warning(f"Conflict: {conflict}")
    st.markdown("**Why this plan**")
    st.text(scheduler.explain_plan())
