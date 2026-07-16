# PRD Structure and Template

## Standard Sections
A comprehensive PRD typically contains the following sections, in order:

## Overview and Objectives
A short executive summary: what this is, why now, and the top objectives. A reader
should understand the gist in under a minute.

## Problem Statement
A precise description of the user problem, ideally one or two sentences that do not
imply a solution. Include evidence: data, research, or customer quotes that show
the problem is real and worth solving.

## Target Users
The specific segments who have the problem. Personas, jobs-to-be-done, and the
context in which they experience the pain. Avoid "everyone" — the more specific,
the better the requirements.

## Goals and Non-Goals
Goals state the outcomes this work should achieve. Non-goals explicitly name what
is out of scope, which prevents scope creep and clarifies boundaries. Non-goals are
one of the highest-leverage sections in a PRD.

## Assumptions and Dependencies
Assumptions are things you believe to be true but have not verified. Dependencies
are external teams, systems, or decisions this work relies on. Naming them early
surfaces risk.

## Functional Requirements
The capabilities the product must provide, each with a clear title, description,
priority, and acceptance criteria. These are testable statements of behavior.

## Non-Functional Requirements
Quality attributes such as performance, security, accessibility, reliability, and
scalability, each with a measurable target.

## User Flows
Step-by-step paths a user takes to accomplish key tasks, including error and edge
cases. Diagrams help.

## Success Metrics
The measurable signals that indicate the product is working, tied to the objectives.
Include a baseline and a target where possible.

## Risks and Mitigations
The main things that could go wrong, their severity, and how you will reduce them.

## Open Questions
Unresolved decisions, with owners and, ideally, a decision date.

## Keep It Skimmable
Use consistent IDs (FR-1, NFR-1), short paragraphs, and tables. A PRD that cannot
be skimmed will not be read.
