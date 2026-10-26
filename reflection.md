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
