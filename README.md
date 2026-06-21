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


1.**codebase-to-diagram**
- look for any directory structures, package.json, requirements.txt, go.md, dockerfiles, kubernetes helm charts, etc. to map out http entrypoints, auth libraries, third party APIs, known vulnerable versions in use, exposed container ports, shared networks/volumes, session token storage
- ouput: excalidraw diagrams (system context, build pipeline diagram, runtime architecture diagram, dataflow diagram) this will help identify things like where secrets enter the pipeline for example

2. **secrets-recon**
  - use trufflehog to scan the repo for any hardcoded secrets like api keys, AWS OIDC tokens, developer tokens
  - output: save any secrets that can be leveraged at a later point in the assessment
  
3. **webapp-reviewer**
- calls semgrep SAST to review the codebase and flag any findings for things like reflected/stored XSS, unauthenticated or missing-auth-check endpoints, insecure file upload handling (extension/MIME bypass, path traversal on upload), IDOR in object-returning routes, SSRF in any user-controlled fetch/URL
- output: tagged findings mapped to OWASP Top 10, with file:line location

4. **api-reviewer**
- skill.md will be created based on owasp api top 10
- look for things such as unencrypted communications, absence of rate limiting, SSRF in any endpoint that fetches user-supplied URL, permissive CORS
- output: tagged findings mapped to OWASP Top 10, with file:line location

5. **supply-chain-cicd-reviewer**
- look for attack paths in the build pipeline. If github actions are in use, can it be abused to leak secrets in the actions log or exfiltrate them to a c2 channel?
- calls poutine against workflow definitions for known CI/CD patterns like poisoned pipeline execution, risky triggers, exposed self-hosted runners
- check for missing branch protection and tag protection rules in github, missing egress control
- runs semgrep SCA across lockfiles for known vulnerable dependencies, dependency confusion
- reviews aws iam trust policies for overly broad subject cliams like repo:org/* instead of specific scopes
- output: any weaknesses in the build pipeline, tagged with whether exploitation needs existing repo write access or is reachable from an external PR/fork

6. **iac-reviewer**
- reviews Terraform/CloudFormation/Helm-values for IAM roles with overly broad principals or trust conditions (wildcard resources, missing Condition blocks on AssumeRole)
- checks for publicly-exposed resources declared in code: S3 buckets missing PublicAccessBlock, security groups with 0.0.0.0/0 ingress on anything internet-facing
- flags missing encryption-at-rest/in-transit and missing logging (CloudTrail, VPC flow logs) that would blind an investigation later
- output: IaC misconfigs by resource and file:line

7. **cloud-posture-reviewer**
- this will review AWS IAM policies, Security Groups, and CodeArtifacts
- IAM: confirms the actual deployed trust condition on CI-assumable roles (not just what Terraform says), checks for confused-deputy patterns (a role trusted by a third party with no external ID)
- Security Groups: live ingress rules — anything 0.0.0.0/0 on a port that shouldn't be public, and whether they match what IaC declared
- CodeArtifact: who can publish and how broadly, package-origin controls (can an internal package name be shadowed by a public one — registry-level dependency confusion)
- output: live findings, each tagged with whether it matches or diverges from what iac-reviewer found in source (drift)

8. **container-image-reviewer**
- runs Trivy against built images and Dockerfiles for known CVEs in base images and installed packages
- reviews Dockerfile hygiene: running as root (no USER), secrets baked into a layer (recoverable from layer history even if "removed" later), unpinned/latest base image tags
- checks multi-stage builds for build-time secrets (build args, .npmrc/.pip.conf tokens) leaking into the final image
- output: image/Dockerfile findings by severity, kept separate from how k8s-reviewer finds the image actually being run

9. **k8s-reviewer**
- runs Kubescape against manifests/Helm charts for RBAC over-permissioning, missing Pod Security Standards, CISA hardening-guide deviations
- runs Trivy (k8s mode) for workload-level vulnerabilities and misconfig
- looks specifically for breakout-enabling settings: privileged containers, hostPath mounts, hostNetwork/hostPID, capabilities not actually dropped, missing seccomp/AppArmor
- checks secrets handling: plaintext Secrets readable cluster-wide, service-account tokens auto-mounted into pods that don't need API access
output: k8s findings tagged by breakout-potential (lateral-movement-enabling vs. general misconfig)

10. **findings-normalizer**
- reshapes every raw finding from every other agent into one consistent schema — same severity scale, same fields, regardless of which tool or skill produced it
- tags what each finding actually grants/requires access to (e.g. "this token grants push to repo X," "this role requires assuming role Y first") — this is what makes
findings from different agents linkable
- dedupes - the same secret sometimes gets flagged by more than one agent (e.g. a key in a CI workflow caught by both secrets-recon and supply-chain-cicd-reviewer)
- output: one consolidated, schema-consistent json — the only input attack-chain-generator reads

11. **attack-chain-generator**
    - it would leverage mitre att&ck for cloud/saas/containers/k8s and compare it against the findings to map out potential attack paths
    - builds the resource/access graph from the normalized findings (deterministic — matches grants_access_to against requires_access_to) and finds candidate paths from internet-facing entry points to high-value targets
    - maps each hop in a candidate path to its MITRE ATT&CK technique (Enterprise + Cloud/Containers matrices) — e.g. a leaked CI token → T1552 Unsecured Credentials, assuming an over-trusted role → T1078.004 Valid Cloud Accounts, escaping a container → T1611 Escape to Host
    - output: ranked attack chains, each with an ATT&CK-tagged kill chain, entry point, target, and business impact


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


