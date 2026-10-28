# Reproducible substitute test

The October 27 benchmark fixes six original synthetic assistance inputs and compares three explicit capability envelopes:

1. **General model:** existing configured Hermes model, one response, no tools or supplied source facts.
2. **General Agent:** the same model with bounded search over a frozen official-source shelf, file reading and arithmetic tools. No BillFit functions or answer keys are exposed. This is a controlled retrieval/file/tool Agent, not a claim about every unrestricted web Agent.
3. **Dedicated Skill:** the actual separately checked-out BillFit assistance function and its versioned data. No model is needed for this deterministic slice. Record its commit; do not copy a private implementation into this repository.

The task asks for current, preliminary CARE/FERA status, both ceilings and an explicit non-official-decision boundary. Expected answers are removed from model inputs. The same normalized response contract is used for every arm. The source shelf is a human-checked transcription of official facts and interpretation, available only through generic tools in arm 2. Its interpretation contains domain knowledge: any advantage over arm 1 is retrieval/context availability, not evidence that the model cannot reason. A wider live-web Agent can have different results.

## Run

Python 3.11+ is sufficient for the harness and tests. Existing Hermes is optional and is never installed or reconfigured by the adapter.

```sh
python -m unittest discover -s tests
python scripts/substitute_benchmark.py --arm skill --billfit-root /path/to/billfit --output /absolute/new-skill.json
python scripts/substitute_benchmark.py --arm model --adapter-json /absolute/hermes-command.json --output /absolute/new-model.json
python scripts/substitute_benchmark.py --arm agent --adapter-json /absolute/hermes-command.json --output /absolute/new-agent.json
python scripts/substitute_benchmark.py --summarize /absolute/new-model.json /absolute/new-agent.json /absolute/new-skill.json
```

Add `--output /absolute/new-analysis.json` to save a summary with hashes of all raw run files. Summaries re-evaluate immutable answers with a named evaluator rather than trusting stored scores. See [the observed October 27 results](2026-10-27/RESULTS.md) for environment, limitations and the disclosed abstention-classification refinement.

The adapter JSON is an argv array, not a shell command. For example, use your existing Hermes interpreter with `-I` and an absolute path to `scripts/hermes_benchmark_adapter.py`. On Windows with an existing WSL installation, an argv array can invoke `wsl.exe -d Ubuntu --cd /tmp -- <hermes-python> -I <adapter-path>`. Keep local command files and credential configuration outside this repository. No credentials are sent through stdin or reports.

Each model call is a real request to the already configured provider; run only within existing authorization and budget. The maximum is one call per model task and four model turns/four bounded tool calls per Agent task. There are six tasks per arm. Failed attempts are retained; no automatic rerun selects a nicer result. Run outputs must be new files. Unknown costs, user actions and maintenance hours remain null. Do not infer a free model call from a subscription.

## Metrics and limits

- **Critical fact correctness:** exact expected fields, with wrong/missing fields shown separately.
- **Task completion:** correct bounded output plus evidence that the current source was actually read when required. A plausible URL guessed by a tool-free model is not a verified lookup.
- **User operations:** null until a user study instruments them; adapter calls are machine operations, not user actions.
- **Time and cost:** measured harness wall time and provider calls; account-attributable cost and tokens remain null if unavailable.
- **Maintenance:** record source-refresh time, adapter repairs and test/review effort prospectively; do not invent a number from code size.

No arm enrolls a household or verifies a real account. The benchmark does not establish demand, realized savings, clinical eligibility or comprehensive bill comparison. The evaluator is deterministic but its expected facts still need independent review. Repeat with new cases and independent coding before selecting a product strategy.
