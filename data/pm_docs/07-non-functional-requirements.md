# Non-Functional Requirements (NFRs)

## What They Are
Non-functional requirements describe how well a system must perform its functions,
rather than what functions it performs. They are quality attributes: performance,
scalability, reliability, security, privacy, accessibility, usability,
maintainability, and compliance. They are easy to forget and expensive to retrofit.

## Make Them Measurable
An NFR is only useful if it is testable. "The app should be fast" is not an NFR;
"95% of search requests return in under 300 ms at 1,000 concurrent users" is.
Attach a concrete metric and threshold to every NFR so QA can verify it.

## Common Categories
Performance covers latency, throughput, and resource use. Scalability covers
behavior under growth in users or data. Reliability and availability cover uptime
targets (for example, 99.9%) and recovery objectives. Security covers
authentication, authorization, encryption, and threat mitigation. Privacy covers
data handling, consent, and retention. Accessibility covers standards such as WCAG
2.1 AA. Usability covers learnability and error rates. Maintainability covers code
quality, observability, and how easily the system can be changed.

## Accessibility Is Not Optional
Accessibility is both an ethical obligation and, in many jurisdictions, a legal one.
Targeting WCAG 2.1 AA — keyboard navigation, sufficient color contrast, screen-reader
support, and clear focus states — should be a default NFR for any user-facing
product.

## Security and Privacy by Design
Bake security and privacy in from the start rather than bolting them on. Specify
requirements for data encryption in transit and at rest, least-privilege access,
audit logging, and compliance regimes (GDPR, HIPAA, SOC 2) that apply to your users.

## Trade-Offs
NFRs often conflict with each other and with cost and speed. Stronger security can
add friction; higher availability costs more. A PRD should state which quality
attributes take priority when they collide, so engineering can make consistent
trade-offs.
