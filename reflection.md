# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Core user actions, based on the PawPal+ scenario:

1. **Enter owner and pet information.** The user can set up a profile with basic details about themselves (name, how much time they have each day, any preferences) and about their pet (name, species/breed, any special needs). The scheduler uses this context when building a plan.
2. **Add and manage care tasks.** The user can add care tasks for their pet, such as a walk, feeding, medication, grooming, or enrichment. Each task has at least a duration and a priority, and the user can edit or remove a task later as their routine changes.
3. **Generate and view today's plan.** The user can ask PawPal+ to build a daily schedule that fits the tasks into the time available, putting higher-priority tasks first. The app shows the plan clearly, explains why it chose that order, and notes any tasks it had to leave out.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code for pretty much every step of this phase. First I had it read the README scenario and pick out the three main things a user needs to do. Then I used it to brainstorm the classes and what each one should store and do, and to turn that into a Mermaid UML diagram. After that it wrote the class skeletons (with dataclasses for Task, Pet, and Owner), the actual scheduling logic, the main.py demo, and the tests.

The prompts that worked best were the ones that pointed at something I already had, like "use my UML to make the class skeletons" or "look at the diagram and cut anything unnecessary." When I was vague it gave me more than I needed.

**b. Judgment and verification**

I didn't take everything it suggested. Its first brainstorm had five classes, including a separate DailyPlan class, but the assignment is built around four, so I had that folded into the Scheduler instead. I also had it review the first UML and it found stuff that didn't need to be there: a collect_tasks() method that did the same thing as Owner.get_all_tasks(), getter/setter methods for attributes that were already public, and fields like age, special_needs, and category that nothing actually used. I cut all of those. I also made sure the Scheduler gets its tasks through Owner.get_all_tasks() and not from just one pet, since it needs to plan for all of them.

To check that it actually worked, I ran python main.py and went through the schedule myself. The walk and the pill showed up at their preferred times, the other tasks filled in around them without overlapping, and the bath got skipped because it was 45 minutes and there were only 30 left. I also ran python -m pytest and all 4 tests passed.

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
