# R2: Repo Reaper

![Project Logo](repo-reaper-logo.png)


# Agentic Red Team Orchestrator

This is a system design document for Repo Reaper, a mostly agentic system for assessing codebases as a red teamer. The tool is a collection of Claude Agents, MCP Servers, custom scripts, and prompts for a human operator. This tool is designed to systematically deconstruct and analyze codebases from the perspective of a highly sophisticated, nation-state adversary.

The outputs of this tool are meant to be useful for red team operators, defenders, and codebase owners.
For red teamers - the tool will provide you with attack chain options
For defenders - detection opportunities across any part of the attack chain
For code owners - automated PR generation for fixes

## How to Use

1. Clone the repo
2. Run it with `python3 repo-reaper.py`
3. It will prompt you:
   
   ``` 
   1) Initial Repo Assessment # This will give the operator the attack surface with prompts to triage findings
   2) Second Pass # This will use the feedback from the initial repo assessment to inform the current test
   3) Re-test # Run the exact same scenarios to validate fixes
   ```

![Three phase Workflow](three-phase-workflow.png)

## Design Validation

The tool runs in a three phase human operator-gated CLI. This works for a few reasons:

- **Human triage:** An LLM doesn't have enough context to know the criticality of one exposed API key vs another. The judgement call should remain with the operator

- **Defensible audit trail:** R2 will log and track "what was tested, when, and against what commit". This can be turned into a report and defended later.

- **Cost Control:** Deploying multiple parallel subagents across a large monorepo can get expensive. Gating behind an explicit operator kick off rather than auto-triggering on every push keeps spend predictable and intentional.

## How it Works

![Dispatch Workflow](dispatch-workflow.png)

## Components


### Agents + Skills
These agents and skills will be developed to leverage LLM capability + reach for existing tools as needed

| Agent         | Skills        |
|--------------|-------------|
| secrets-recon | secrets-detection/SKILL.MD |
| webapp-reviewer | owasp-web/SKILL.md |     
| api-reviewer | owasp-api/SKILL.md |  
| supply-chain-cicd-reviewer | owasp-cicd/SKILL.md | 
| iac-reviewer | iac-misconfig-review/SKILL.md | 
| cloud-posture-reviewer | aws-iam-review/SKILL.md, aws-sg-review/SKILL.md, aws-codeartifact-review/SKILL.md | 
| container-image-reviewer | owasp-docker/SKILL.md | 
| k8s-reviewer | owasp-kubernetes/SKILL.md | 
| codebase-to-diagram | codebase-to-diagram/SKILL.md | 
| findings-normalizer | finding-severity-rubric/SKILL.md, finding-schema/SKILL.md | 
| attack-chain-generator | attack-chain-generator/SKILL.md | 


### Tools
These existing open source tools will be called by the agents as needed

| Purpose         | Tool        | Details |
|--------------|-------------|--------------|
| SCA | semgrep | https://github.com/semgrep/semgrep |
| SAST | semgrep | https://github.com/semgrep/semgrep  |
| DAST | COMING SOON - burpsuite pro | https://portswigger.net/bappstore/9952290f04ed4f628e624d0aa9dccebc  |
| Secrets Scanning | trufflehog | https://github.com/trufflesecurity/trufflehog |
| Container Mapping | trivy | https://github.com/aquasecurity/trivy | 
| Kubernetes Mapping | kubescape | https://github.com/kubescape/kubescape | 
| Registry Mapping | trivy | https://github.com/aquasecurity/trivy | 
| CI/CD | poutine | https://github.com/boostsecurityio/poutine | 


### MCP

## Assumptions

- Assuming a target tech stack comprising of Github, Terraform, AWS, Kubernetes and Docker
- This tool will be granted read-only access to github, AWS, artifact repositories, and ticket management
- Codebases will primarily be monorepos
- Token consumption is a non-issue :) 

## Workflow

1. Operator initiates python cli and selects Initial Assessment
2. The initial assessment will kick off the following agents in order:
   - **codebase-to-diagram:** this will read directory structure, package.json, requirements.txt, go.md, dockerfiles, CI configs, etc. to understand the overall application. 
   Output:
   - System Context Diagram - depiction of how a user would use the app
   - Deployment Diagram - depiction of the build pipeline
   - Runtime Architecture - depiction of the cloud infrastructure
   - Data Flow Diagram - depiction of data flows through the application
   - Trust Boundaries Table - api routes, webhook receivers, file upload endpoints, ci pipeline triggers, admin panels
3. secrets-recon: initial scan across the repo for any hardcoded secrets
4. The rest of the agents will run in parallel and each write their output to findings/


## How this can be improved

- Runtime attack surface mapping: give the operator options to use Burp and SmokedMeat via MCP
- A chat feature where the LLM can be leveraged in the context of each assessment
- Enable the retest option to run non-interactively
- Add Reporting
- Out of band initial access methods
- Security for this tool itself to ensure only the intended operators can leverage it
- Feedback loop into defensive tooling

## Whats left to be done

- Skill and agent generation
- The plumbing for tying the pieces together with MCP, API Keys etc.
- Script development


