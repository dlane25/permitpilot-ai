# PermitPilot Agent Workflow

## Goal

Prepare a construction project for permit submission.

## Workflow

Project Goal
  |
  v
PermitPilot Operations Agent
  |
  +-- Intake
  +-- Jurisdiction
  +-- Requirements
  +-- Documents
  +-- Compliance
  +-- Risk
  +-- Forms
  |
  v
Validation
  |
  +-- Safe action -> continue autonomously
  |
  +-- Material decision -> request human approval
                              |
                              v
                           resume
                              |
                              v
                     Permit Package Ready

## Required Agent Event Fields

Every major agent action should record:

- agent identity
- action
- explanation
- confidence when applicable
- evidence references
- projected impact
- timestamp
- approval state
- result
