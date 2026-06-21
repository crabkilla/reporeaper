This is plain orchestrator code and it's the _only_ thing with write access to `assessments/`.  

Responsible for:

- Creating the assessment folder structure (`manifest.json`, the `findings/` subfolders) when a new assessment starts
- Receiving each subagent's final response since subagents don't write files themselves, they just return structured JSON as their last message and persisting that to `findings/raw/<subagent-name>.json`
- Validating that JSON is well-formed before writing it, so a malformed subagent response gets caught immediately rather than discovered later when something downstream chokes on a broken file
- Reading state back in for phases 2 and 3 — when you run "second pass" possibly days later, this module is what knows how to find the right assessment-id and load `triaged.json`
- Updating `manifest.json` as the pipeline progresses (which subagents succeeded/failed, phase status, the pinned plugin version)
