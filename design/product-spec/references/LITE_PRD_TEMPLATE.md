# Lite PRD (Demo-Grade) Template

Use this template when generating a demo-grade PRD. It is intentionally short and maps into the full PRD.

## 1) One-Sentence Problem
> Format: [User] struggles to [do X] because [reason], resulting in [impact].

## 2) Demo Goal (What Success Looks Like)
- What must work for the demo to be considered successful
- What outcome the demo should clearly communicate
- Optional: Non-goals (what is intentionally out of scope)

## 3) Target User (Role-Based)
- Role / context
- Skill level
- Key constraint (time, knowledge, access, etc.)

## 4) Core Use Case (Happy Path)
- Start condition
- Step-by-step flow (numbered)
- End condition

## 5) Functional Decisions (What It Must Do)
| ID | Function | Notes |
|----|----------|-------|

## 6) UX Decisions (What the Experience Is Like)
### 6.1 Entry Point
- How the user starts
- What they see first

### 6.2 Inputs
- What the user provides

### 6.3 Outputs
- What the user receives and in what form

### 6.4 Feedback and States
- Loading
- Success
- Failure
- Partial results

### 6.5 Errors (Minimum Viable Handling)
- Invalid input
- System failure
- User does nothing

## 7) Data and Logic (At a Glance)
### 7.1 Inputs
- User
- API
- Static / mocked
- Generated

### 7.2 Processing
- Input -> transform -> output
- Fetch -> analyze -> summarize

### 7.3 Outputs
- UI only
- Temporarily stored
- Logged

## Compatibility Map (Lite -> Full PRD)
- One-Sentence Problem -> 0) PRD Summary + 2) Problem Statement / Opportunity
- Demo Goal -> 1) Executive Summary + 10) Success Metrics / KPIs
- Target User -> 3) Target Users / Personas
- Core Use Case -> 4) User Stories / Use Cases (core narrative)
- Functional Decisions -> 8) Functional Requirements
- UX Decisions -> 4.2 Use case narratives + 9) Non-Functional Requirements (UX aspects)
- Data and Logic -> 7) Data Lifecycle and Retention + 14) Dependencies (data sources)
