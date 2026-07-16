# Common PRD Mistakes and How to Avoid Them

## Solutionizing Too Early
The most common mistake is describing a solution before the problem is understood.
When a PRD opens with a feature ("add a dashboard") rather than a problem, it locks
the team into one answer and skips the question of whether it is the right one.
Always lead with the problem and the evidence that it matters.

## Vague or Untestable Requirements
Requirements like "the system should be user-friendly" or "it should be fast" cannot
be built or tested. Every requirement needs acceptance criteria or a measurable
threshold. If QA cannot write a test for it, it is not a requirement yet.

## Missing Non-Goals
Without an explicit list of non-goals, scope quietly expands. Naming what you are
deliberately not doing is one of the cheapest ways to protect a timeline and set
stakeholder expectations.

## No Success Metrics
A PRD with no metrics cannot be evaluated after launch. Teams end up arguing about
whether a feature "worked." Define the baseline, the target, and the time window
before building.

## Ignoring Edge Cases and Errors
Happy-path-only PRDs produce happy-path-only products. Empty states, error handling,
permissions, offline behavior, and large-data cases should be specified, because
they are where real users get stuck.

## Writing for No One
A PRD that lists "all users" as the audience usually serves none of them well.
Specific segments produce specific, useful requirements. Narrow the audience.

## The Document Nobody Reads
An overlong, unstructured PRD is functionally the same as no PRD. Keep it skimmable:
a crisp summary, clear IDs, short sections, tables over prose where possible, and
open questions surfaced rather than buried.

## Treating It as Fixed
A PRD written once and never updated goes stale and gets ignored. Version it, date
it, resolve open questions over time, and let it evolve as the team learns.

## Skipping Feasibility Input
A PRD written without engineering input can specify things that are impractical or
miss cheaper alternatives. Involve engineering early so requirements are grounded in
what is buildable.
