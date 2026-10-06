# RoundTrip

Checks selected aspects of meaning after a forward transformation and an isolated inverse transformation.

## Published deployment

Published and verified on 2026-10-06 in GenLayer hosted Studio.
- [Contract](https://explorer-studio.genlayer.com/address/0xBef31E7e6B2586B089fdE61fa23C826b28485C9c)
- [Exact deployed source](https://github.com/Zhekinmaksim/genlayer-roundtrip/blob/ff6f6bdfe4dae09bf4fc061ff81d07081b40956c/contract.py)
- [Ready-to-copy submission](SUBMISSION.md)
- [Live evidence](evidence.json)

Deployment and both live evaluation transactions are FINALIZED with execution
SUCCESS. Both stored outcomes matched expectations. Ten local regression groups
and SDK semantic validation pass; see verification.json for the source hash.

## Material nondeterminism and independent validation

Each node performs three separate LLM calls: forward transform, inverse using only the forward output, and aspect comparison against the original. The inverse prompt does not include the source or aspect list. Validators repeat the entire pipeline independently. Consensus compares the source hash and survival vector, not the generated prose. The accepted vector controls FAITHFUL versus LOSSY and the lost-aspect mask.

Uses `gl.nondet.exec_prompt` within `gl.eq_principle.prompt_comparative`.
The comparative wrapper repeats the task and applies an LLM equivalence check;
it is not a byte-for-byte equality check. State is written only after the
equivalence call returns. See the
[official equivalence documentation](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle).

## Safety changes

- Creator-only, one-time submission. Evaluation is permissionless.
- Input hashes are computed on-chain, not accepted from the caller.
- Input and policy commitments are rechecked before judgment.
- Bounded identifiers, terms and inputs; duplicate rubric entries rejected.
- Strict output shape/types and range validation, before and after consensus.
- Every settled outcome, including UNDETERMINED, is terminal.
- Result hash binds input commitments, outcome, decision fields and reason.
- SDK storage containers are not user-constructed. Views use ordinary lists
  or a JSON string. Runtime dependency is pinned in contract.py.

Breaking API change from the archive: the submission method no longer accepts
a caller-provided hash. Use the returned commitment. get_result returns a JSON
string; parse it once in clients. See schema.json for the exact ABI.

## API

- `open_case(id, transform, inverse, aspects_text)` -> terms hash
- `submit_source(id, source)` -> computed SHA-256
- `evaluate(id)` -> settlement
- `get_outcome(id)` -> 0 pending, 1 faithful, 2 lossy, 3 undetermined
- `lost_aspects(id)` -> list of aspect text
- `get_result(id)` -> JSON string with outcome, reason, masks and commitments

## Verification and deployment

From this directory:

```sh
python3 sim/check.py
uvx --python 3.13 --from genvm-linter genvm-lint check contract.py --json
genlayer network set studionet
genlayer deploy --contract contract.py
```

All constructors have no arguments. The commands above deploy a NEW instance.
The verified deployment is linked above; no redeployment is needed to submit it.
Restore your previous network after testing. Use normal validator consensus,
not leader-only mode.

Use the exact method arguments in smoke.json with a fresh case ID each time:
open_case, the listed submit method, evaluate, then get_result.
These two expected outputs were confirmed live; actual readback results and
transaction hashes are in evidence.json.
Wait for FINALIZED and inspect leader execution SUCCESS as well as stored
state; transaction acceptance alone can also describe a reverted execution.
Deployment/evaluation transaction hashes and source SHA-256 have been recorded.

Test an unauthorized submission, duplicate submission, second evaluation and
prompt-injection input in Studio as additional negative cases. Source and
rubric mutation are simulated locally; there is no public mutation API.

## Limitations

This tests a model-generated round trip, not a specific externally supplied translation. Generated text is not stored. The inverse can still infer or hallucinate omitted facts; reversibility is not proof of semantic equivalence. FAITHFUL covers only the supplied aspects. Three calls per node increase latency and model cost.

UNDETERMINED describes catchable judgment/format/integrity failures. A network
consensus failure can instead leave a transaction unaccepted without storing
UNDETERMINED. Models can agree on an incorrect answer. Data delimiters do not
guarantee prompt-injection resistance. No external security audit or claim of
novelty across all existing GenLayer contracts is made.

## Local test scope

The harness prohibits TreeMap/DynArray construction and simulates independent
leader/validator calls. It tests authorization, immutable inputs, commitments,
strict payloads, terminal settlement and outcome logic. It uses an exact mock
comparator, not the real LLM comparator. SDK semantic validation verifies the
storage types and ABI but does not execute the contract inside GenVM.
