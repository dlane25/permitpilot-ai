# PermitPilot Architecture

## Frontend

Next.js + TypeScript + Tailwind CSS

Responsibilities:

- project command center
- permit readiness
- autonomous activity timeline
- human decision queue
- evidence review
- measurable impact dashboard

## Agent Runtime

Python + Strands Agents SDK

Responsibilities:

- orchestration
- tool selection
- reasoning
- permit workflow execution
- human escalation
- structured outputs

## AWS

Amazon Bedrock
Amazon Bedrock AgentCore
Amazon S3
Amazon DynamoDB
AWS Lambda where appropriate
Amazon EventBridge where appropriate

## Architectural Principle

The frontend submits goals and displays state.

The authoritative agent workflow executes server-side.

Secrets, AWS credentials, models, agent tools, and consequential execution logic remain server-side.
