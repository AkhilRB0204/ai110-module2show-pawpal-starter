import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, to_hhmm, to_minutes

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.caption(
    "Plan your pets' care for the day. Add your pets and their tasks, then PawPal+ builds "
    "a schedule that fits your time, puts the most important care first, and warns you "
    "about anything that clashes."
)


def valid_time(text: str) -> bool:
    """Return True if text is a real 24-hour clock time like 07:30."""
    try:
        minutes = to_minutes(text)
    except ValueError:
        return False
    hours, mins = text.split(":")
    return 0 <= int(hours) < 24 and 0 <= int(mins) < 60 and 0 <= minutes < 24 * 60


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
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        with col5:
            preferred = st.text_input("Preferred time (HH:MM, optional)")
        if st.form_submit_button("Add task"):
            preferred = preferred.strip() or None
            if not task_title.strip():
                st.error("Enter a title for the task.")
            elif preferred and not valid_time(preferred):
                st.error("Preferred time must be a 24-hour time like 08:30.")
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
        tools = Scheduler(owner)
        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
        with col2:
            status_filter = st.selectbox("Show status", ["To do", "Done", "All"])
        shown = tools.sort_by_time(
            tools.filter_tasks(
                pet_name=None if pet_filter == "All pets" else pet_filter,
                completed={"To do": False, "Done": True, "All": None}[status_filter],
            )
        )
        st.table(
            [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Preferred time": t.preferred_time or "-",
                    "Minutes": t.duration,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                    "Due": str(t.due_date) if t.due_date else "today",
                    "Done": "yes" if t.completed else "no",
                }
                for t in shown
            ]
        )

        open_tasks = tools.sort_by_time(tools.filter_tasks(completed=False))
        if open_tasks:
            col1, col2 = st.columns([3, 1])
            with col1:
                choice = st.selectbox(
                    "Mark a task complete",
                    range(len(open_tasks)),
                    format_func=lambda i: f"{open_tasks[i].pet_name}: {open_tasks[i].title}",
                )
            with col2:
                st.write("")
                if st.button("Complete"):
                    done = open_tasks[choice]
                    next_task = tools.mark_task_complete(done)
                    if next_task:
                        st.success(
                            f"Completed {done.title}. Next one is due {next_task.due_date}."
                        )
                    else:
                        st.success(f"Completed {done.title}.")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.caption("Add a pet first, then you can give it tasks.")

st.divider()

st.subheader("Today's Schedule")
day_start = st.text_input("Day starts at (HH:MM)", value="08:00")

if st.button("Generate schedule", type="primary"):
    if not valid_time(day_start.strip()):
        st.error("Day start must be a 24-hour time like 08:00.")
        st.stop()

    scheduler = Scheduler(owner, day_start=day_start.strip())
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()
    used = sum(task.duration for _, task, _ in plan)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks scheduled", len(plan))
    col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
    col3.metric("Conflicts", len(conflicts))

    # Conflicts go first, above the table, so the owner sees them before
    # following the plan. Each one names both tasks and suggests a fix.
    if conflicts:
        st.warning(
            "**Some tasks overlap.** PawPal+ kept them at your preferred times "
            "because it can't tell which one is safe to move. Change one task's "
            "preferred time, or do them together if that works for you."
        )
        for conflict in conflicts:
            st.warning(conflict)

    if plan:
        st.success(f"Here's today's plan for {owner.name}'s pets, in time order.")
        st.table(
            [
                {
                    "Time": f"{start}-{to_hhmm(to_minutes(start) + task.duration)}",
                    "Pet": task.pet_name,
                    "Task": task.title,
                    "Priority": task.priority,
                    "Why": reason,
                }
                for start, task, reason in plan
            ]
        )
    else:
        st.info("Nothing to schedule today. Add tasks, or check that they fit in your time.")

    if scheduler.skipped:
        st.info(
            "**Left out today** (not enough time left):\n"
            + "\n".join(
                f"- {task.title} ({task.pet_name}): {reason}"
                for task, reason in scheduler.skipped
            )
        )

    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan())
