# Writing Effective User Stories

## The Standard Format
A user story captures a requirement from the user's perspective using the template:
"As a [type of user], I want [some goal] so that [some benefit]." The "so that"
clause is the most important part because it states the value and lets the team
find alternative solutions that still deliver it.

## INVEST Criteria
Good user stories are INVEST: Independent (can be built and shipped on their own),
Negotiable (a conversation, not a rigid contract), Valuable (delivers value to a
user or customer), Estimable (the team can size it), Small (fits comfortably in a
sprint), and Testable (has clear acceptance criteria). If a story fails one of
these, it usually needs to be split or clarified.

## Splitting Large Stories
When a story is too big (an "epic"), split it along meaningful boundaries: by
workflow step, by user role, by data variation, by happy path versus edge cases,
or by create/read/update/delete operations. Avoid splitting by technical layer
(for example, "build the backend" then "build the frontend"), because neither half
delivers user value on its own.

## Epics and Themes
An epic is a large body of work that groups related stories under a common goal.
Themes group epics under a strategic objective. This hierarchy — theme, epic,
story — keeps a backlog organized and traceable back to strategy.

## Common Pitfalls
Avoid writing solutions disguised as stories ("As a user I want a dropdown"),
because that pre-commits to a design. State the goal, not the widget. Avoid vague
benefits ("so that it is better"). And avoid stories with no testable outcome —
if you cannot write acceptance criteria, the story is not ready.

## Stories Are a Placeholder for a Conversation
User stories are intentionally brief. They are a reminder to have a conversation,
not a full specification. The details live in acceptance criteria and in
discussion between PM, design, and engineering.
