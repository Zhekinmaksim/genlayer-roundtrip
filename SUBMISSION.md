# Portal submission - RoundTrip

## Category
Builder > Intelligent Contracts

## Title
RoundTrip

## Contribution date
October 6, 2026 (publication and live verification).

## Description / Notes (908 characters)
```text
RoundTrip is a GenLayer Intelligent Contract that checks whether selected aspects of meaning survive a transformation and its inverse. Each node performs three separate LLM calls: forward transformation, inverse using only the transformed text, and comparison with the original. Validators independently repeat this pipeline through gl.eq_principle.prompt_comparative and compare the source hash and survival vector. The accepted vector directly determines FAITHFUL or LOSSY and the lost-aspect mask. Inputs are creator-only, immutable, bounded and hashed on-chain; malformed judgments fail closed. Deployed on hosted Studio with normal validator consensus. Two finalized live tests verify preservation of both aspects and loss of both after deliberate removal of quantity and deadline. All 10 local regression groups and SDK validation pass. Exact source, inputs, results and transaction links are provided.
```

## Primary evidence links
GitHub:
https://github.com/Zhekinmaksim/genlayer-roundtrip

Hosted Studio contract:
https://explorer-studio.genlayer.com/address/0xBef31E7e6B2586B089fdE61fa23C826b28485C9c

## Additional evidence
- [Exact deployed source](https://github.com/Zhekinmaksim/genlayer-roundtrip/blob/ff6f6bdfe4dae09bf4fc061ff81d07081b40956c/contract.py)
- [Deployment](https://explorer-studio.genlayer.com/tx/0x54cf5eea9a0aa241f3daec2040a787a9fd3be45129ab8ffa4d1675462d63e64d)
- [roundtrip-faithful-001](https://explorer-studio.genlayer.com/tx/0x69422f342b4c2d119e81640b54c25eb5a0b4087c5965ede14d8153512ad5e52d)
- [roundtrip-lossy-001](https://explorer-studio.genlayer.com/tx/0xf0564d6f6e69cf71000f3958176b1a364288db26a32be9eff98cf384346d849c)
- [Inputs, stored results and validator votes](https://github.com/Zhekinmaksim/genlayer-roundtrip/blob/main/evidence.json)

Both evaluation transactions and the deployment are FINALIZED with leader
execution SUCCESS. Stored results were read back and matched the expectations.
Consensus was MAJORITY_AGREE, not necessarily unanimous.

## Local verification
10/10 local regression groups passed on 2026-10-06. GenVM linter 0.11.0 and SDK
semantic validation passed without warnings. Local model/consensus tests use
mocks; the two live scenarios above were executed in hosted Studio.

## Submission status
Ready for manual submission at https://portal.genlayer.foundation/my-submissions.
No portal submission has been sent. These are Studio, not mainnet, deployments.
Tests and deployment evidence do not guarantee steward acceptance.
