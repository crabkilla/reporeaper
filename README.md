# R2: Repo Reaper

![Project Logo](repo-reaper-logo.png)


### System Design for Agentic Red Team Application Assessments

This is a system design document for Repo Reaper, a mostly agentic system for assessing web apps as a red teamer. The tool is a collection of Claude Agents, MCP Servers, custom scripts, and prompts for a human operator. This tool is designed to systematically deconstruct and analyze codebases from the perspective of a highly sophisticated, nation-state adversary.

### How to Use

1. Clone the repo
2. Run it with `python3 repo-reaper.py`
3. It will prompt you:
   
   ``` 
   1) Initial Repo Assessment 
   2) Second Pass
   3) Re-test.
   ```

Initial repo assessment will give the operator the attack surface. Operator will be given prompts of what it thinks are worth it and whats not. 

Second Pass will use the feedback from the initial repo assessment to inform the current test. 

Re-test will essentially look at the findings from the second pass and check against them. 


### Design Validation

The tool runs in a three phase human operator-gated CLI. This works for a few reasons:

- Human triage: An LLM doesn't have enough context to know the criticality of one exposed API key vs another. The judgement call should remain with the operator

- Defensible audit trail: R2 will log and track "what was tested, when, and against what commit". This can be turned into a report and defended later.

- Cost Control: Deploying multiple parallel subagents across a large monorepo can get expensive. Gating behind an explicit operator kick off rather than auto-triggering on every push keeps spend predictable and intentional.
