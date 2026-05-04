---
description: Interview the learner to produce a usable background.md when they have not provided one (or it is too short).
---

# interview — gather a learner's background

Run this only if `background.md` is missing or contains fewer than ~80 words
of substance.

Ask the learner the questions below **one at a time**, wait for each answer,
then write the result to `background.md` at the project root.

## Questions

1. **Field & day-to-day work.** What field are you in, and what does a
   typical week of your work look like? (One paragraph is plenty.)
2. **Career stage.** Undergraduate, masters, PhD student, postdoc, faculty,
   industry researcher, hobbyist?
3. **Maths background.** Comfortable with calculus and linear algebra? Have
   you fit curves to data before? Have you used any statistics?
4. **Programming.** Have you written Python before? Used Jupyter? Used any
   scientific libraries (NumPy, pandas, R, MATLAB, …)?
5. **Analogies that would land.** What kinds of objects, processes, or
   measurements from your daily work would make ML ideas click for you?
   (Examples from past learners: enzyme kinetics, light curves, panel-data
   regressions, dose-response curves.)
6. **What you want out of this notebook.** A one-line goal — e.g. "be able
   to read an ML paper", "fit my own data next week", "prepare for a course".

## Output format

After collecting all answers:

1. Derive a short `snake_case` persona slug from the learner's field
   (e.g. "Marine Biology" → `marine_biologist`, "Climate Science" →
   `climate_scientist`).
2. Create the folder `examples/<slug>/` if it does not exist.
3. Write the background as `examples/<slug>/background.md`:

```markdown
# Learner background

**Field:** ...
**Stage:** ...
**Maths:** ...
**Programming:** ...
**Analogies that would land:** ...
**Goal for this notebook:** ...

## Free-form notes
<anything the learner volunteered that didn't fit above>

> *Background collected via adapt-notebook interview.*
```

4. Confirm the file path to the learner, then proceed with Steps 3–5 of
   `SKILL.md` (adapt both base notebooks for this persona).
