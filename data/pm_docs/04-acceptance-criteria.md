# Writing Acceptance Criteria

## What They Are
Acceptance criteria are the specific, testable conditions that must be true for a
requirement or user story to be considered complete. They define the boundary of
"done" and become the basis for test cases and QA.

## The Given/When/Then Format
A widely used format is Gherkin's Given/When/Then: "Given [some context], When
[some action occurs], Then [some outcome]." For example: "Given a signed-in user
with items in their cart, When they click Checkout, Then they are taken to the
payment page with the cart total displayed." This format is precise, unambiguous,
and maps directly to automated tests.

## Rule-Oriented Criteria
Not every criterion needs Given/When/Then. Simple rule lists work too: "The
password must be at least 12 characters," "Uploads over 25 MB are rejected with a
clear error." Use whichever form makes the expected behavior clearest.

## Cover the Unhappy Paths
Strong acceptance criteria describe not just the happy path but also errors, empty
states, permissions, and edge cases. What happens on network failure? On invalid
input? For an unauthorized user? Missing these is the most common cause of bugs
found late.

## Good Acceptance Criteria Are
Testable (you can objectively verify pass or fail), unambiguous (two engineers
would build the same thing), independent of implementation (they describe behavior,
not code), and complete enough to cover the important scenarios without trying to
enumerate every conceivable case.

## How Many
Aim for at least two to five acceptance criteria per story. Too few usually means
edge cases are missing; too many often means the story should be split.
