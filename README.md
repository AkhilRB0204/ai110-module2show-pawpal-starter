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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧠 Implementation Summary

The backend lives in `pawpal_system.py` and is made of four classes:

- **`Task`** (dataclass): one care activity with a title, duration, priority, frequency (daily or weekly), optional preferred time, and completion status. It can rank its own priority, report whether it is due on a given day, and mark itself complete.
- **`Pet`** (dataclass): a pet's name, species and breed, plus its list of tasks. Adding a task stamps it with the pet's name so the schedule can show whose task it is.
- **`Owner`** (dataclass): the owner's name, daily time budget, and pets. `get_all_tasks()` returns every pet's tasks in one list.
- **`Scheduler`**: the planner. `generate_plan()` reads all tasks through `Owner.get_all_tasks()`, keeps the ones due today, sorts them by priority (then shortest first), drops tasks that no longer fit in the owner's available minutes, places tasks with a preferred time at that time, and fills the rest into open slots from the start of the day. `explain_plan()` summarizes the time used, why tasks were ordered that way, which tasks were skipped, and any overlapping time slots.

`main.py` is a terminal demo that builds an owner with two pets and prints today's schedule.

## 🖥️ Sample Output

Output from `python main.py`:

```
Today's Schedule for Jordan's pets
==============================================================
07:00-07:10  Breakfast          Mochi  [high priority]
07:10-07:20  Clean litter box   Luna   [medium priority]
07:30-08:00  Morning walk       Mochi  [high priority, preferred time]
08:00-08:05  Thyroid pill       Luna   [high priority, preferred time]
08:05-08:20  Brush coat         Luna   [medium priority]
08:20-08:40  Fetch in the yard  Mochi  [medium priority]
==============================================================
Scheduled 6 task(s) using 90 of 120 available minutes.
Tasks were chosen by priority (high first, then shorter tasks), placed at their preferred time if they had one, and otherwise fit into open slots starting at 07:00.
Skipped Bath (Mochi): needs 45 min, only 30 min left.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
$ python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.7.0
collected 4 items

tests/test_pawpal.py ....                                                [100%]

============================== 4 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
