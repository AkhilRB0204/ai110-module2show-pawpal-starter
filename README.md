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

All tasks, as added:
  17:00  Fetch in the yard  Mochi  daily   todo
  07:30  Morning walk       Mochi  daily   todo
  07:00  Breakfast          Mochi  daily   todo
  --:--  Bath               Mochi  weekly  todo
  12:00  Brush coat         Luna   daily   todo
  09:00  Clean litter box   Luna   daily   todo
  07:30  Thyroid pill       Luna   daily   todo

Sorted by time:
  07:00  Breakfast          Mochi  daily   todo
  07:30  Morning walk       Mochi  daily   todo
  07:30  Thyroid pill       Luna   daily   todo
  09:00  Clean litter box   Luna   daily   todo
  12:00  Brush coat         Luna   daily   todo
  17:00  Fetch in the yard  Mochi  daily   todo
  --:--  Bath               Mochi  weekly  todo

Only Luna's tasks:
  12:00  Brush coat         Luna   daily   todo
  09:00  Clean litter box   Luna   daily   todo
  07:30  Thyroid pill       Luna   daily   todo

Completed Breakfast; next one is due 2026-10-26.

Completed tasks:
  07:00  Breakfast          Mochi  daily   done

Still to do:
  17:00  Fetch in the yard  Mochi  daily   todo
  07:30  Morning walk       Mochi  daily   todo
  --:--  Bath               Mochi  weekly  todo
  07:00  Breakfast          Mochi  daily   todo due 2026-10-26
  12:00  Brush coat         Luna   daily   todo
  09:00  Clean litter box   Luna   daily   todo
  07:30  Thyroid pill       Luna   daily   todo

Today's Schedule for Jordan's pets (2026-10-25)
==============================================================
07:30-07:35  Thyroid pill       Luna   [high priority, preferred time]
07:30-08:00  Morning walk       Mochi  [high priority, preferred time]
09:00-09:10  Clean litter box   Luna   [medium priority, preferred time]
12:00-12:15  Brush coat         Luna   [medium priority, preferred time]
17:00-17:20  Fetch in the yard  Mochi  [medium priority, preferred time]
==============================================================
Scheduled 5 task(s) using 80 of 120 available minutes.
Tasks were chosen by priority (high first, then shorter tasks), placed at their preferred time if they had one, and otherwise fit into open slots starting at 07:00.
Skipped Bath (Mochi): needs 45 min, only 40 min left.
Warning: Thyroid pill at 07:30 overlaps Morning walk at 07:30 (Luna and Mochi).
```

## 🧪 Testing PawPal+

Run the tests from the project folder:

```bash
python -m pytest
```

The 22 tests in `tests/test_pawpal.py` cover:

- **Basics:** `mark_complete()` changes a task's status, and `add_task()` increases a pet's task count.
- **Sorting:** `sort_by_time()` returns tasks in chronological order (including times like `9:15` with no leading zero), puts tasks with no time last, and keeps same-time tasks in the order they were added.
- **Filtering:** `filter_tasks()` by pet, by completion status, and by both together.
- **Recurring tasks:** completing a daily task creates a copy due the next day with the same details, a weekly task comes back in 7 days, a `once` task doesn't repeat, and completing the same task twice doesn't create a duplicate.
- **Conflict detection:** warnings for two tasks at the exact same time (same pet or different pets) and for partial overlaps, and no warning for back-to-back tasks.
- **Scheduling:** plans include every pet's tasks, skip tasks that don't fit the time budget (including a budget of 0), leave out completed and future tasks but keep overdue ones, and fit untimed tasks into gaps without overlapping timed ones.
- **Edge cases:** an owner with no pets, a pet with no tasks, and editing a task field that doesn't exist.

Output of a successful run:

```
$ python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/akhilbolla/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 22 items

tests/test_pawpal.py ......................                              [100%]

============================== 22 passed in 0.01s ==============================
```

**Confidence level: ★★★★☆ (4/5)**

Every core behavior has a passing test, and writing the edge-case tests caught a real bug: marking the same task complete twice used to create two copies for the next day, and it's fixed now. I'm not giving it 5 stars because some cases still aren't handled or tested: tasks that run past midnight, invalid times like `25:99`, and `remove_task()` removing every task with the same title, including future copies of a recurring task.

## 📐 Smarter Scheduling

| Feature | Method(s) | How it works |
|---------|-----------|-------|
| Sort by time | `Scheduler.sort_by_time()` | Uses `sorted()` with a lambda key that converts each task's `"HH:MM"` preferred time to minutes after midnight, so `"9:15"` and `"09:15"` sort the same. Tasks with no preferred time go last. |
| Sort by priority | `Scheduler.sort_by_priority()` | Sorts high priority first, then shortest duration first. `generate_plan()` uses this order to decide what gets time first. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Reads every task through `Owner.get_all_tasks()` and keeps the ones matching a pet name, a completion status, or both. Leaving an argument as `None` means "don't filter on this". |
| Time budget | `Scheduler.fit_to_time()` | Walks the priority-sorted tasks and keeps each one that still fits in the owner's available minutes. Tasks that don't fit go into `scheduler.skipped` with the reason. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()`, `Task.is_due_today()` | Completing a `daily` or `weekly` task marks it done and adds a fresh copy to the same pet, due `today + timedelta(days=1)` or `today + timedelta(weeks=1)`. A `once` task doesn't repeat. `is_due_today()` keeps future copies out of today's plan. |
| Conflict detection | `Scheduler.detect_conflicts()` | Checks every pair of planned tasks (`itertools.combinations`) for overlapping time ranges, not just identical start times, for the same pet or different pets. It returns warning strings instead of raising an error, and `explain_plan()` and the app both show them. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
