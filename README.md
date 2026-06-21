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


1.codebase-to-diagram
- look for any directory structures, package.json, requirements.txt, go.md, dockerfiles, kubernetes helm charts, etc. to map out http entrypoints, auth libraries, third party APIs, known vulnerable versions in use, exposed container ports, shared networks/volumes, session token storage
- ouput: excalidraw diagrams (system context, build pipeline diagram, runtime architecture diagram, dataflow diagram) this will help identify things like where secrets enter the pipeline for example

2. secrets-recon
  - 
  - output: 
  
3. webapp-reviewer

4. api-reviewer

5. supply-chain-cicd-reviewer
- 

6. iac-reviewer

7. cloud-posture-reviewer
- this will review AWS IAM policies, Security Groups, and CodeArtifacts

8. container-image-reviewer

9. k8s-reviewer

10. findings-normalizer

11. attack-chain-generator
    - it would leverage mitre att&ck for cloud/saas/containers/k8s and compare it against the findings to map out potential attack paths


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



## Assumptions

- Assuming a target tech stack comprising of Github, Terraform, AWS, Kubernetes and Docker
- This tool will be granted read-only access to github, AWS, artifact repositories, and ticket management
- Codebases will primarily be monorepos
- Token consumption is a non-issue :) 


## How this can be improved

- Runtime attack surface mapping: give the operator options to use Burp and SmokedMeat via MCP
- A chat feature where the LLM can be leveraged in the context of each assessment
- Leverage hackerone published bug bounty reports in the attack-chain-generator skill
- Enable the retest option to run non-interactively
- Add Reporting
- Out of band initial access methods
- Security for this tool itself to ensure only the intended operators can leverage it
- Feedback loop into defensive tooling

## Whats left to be done

- Skill and agent generation
- The plumbing for tying the pieces together with MCP, API Keys etc.
- Script development


