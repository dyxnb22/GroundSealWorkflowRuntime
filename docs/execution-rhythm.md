# Execution Rhythm

## Ideal Single Agent Round

One round should usually do one of the following well:
- clarify a contract
- implement one narrow behavior slice
- add one focused evaluation path
- analyze one failure cluster

## What A Round Should Leave Behind

- an updated canonical document, or
- a coherent code change, or
- a durable evaluation artifact, or
- a findings note that changes the next decision

## When To Pause Coding

Pause implementation when:
- the roadmap phase is unclear
- the contract is unstable
- failures are accumulating without diagnosis
- integration assumptions are multiplying faster than evidence

## When To Start Evaluation

Start evaluation as soon as one narrow core path exists. Do not wait for the subsystem to feel feature complete.

## Anti-Drift Rules

- do not reward raw file count over design clarity
- do not keep adding code if conclusions are not improving
- do not bury important tradeoffs inside commit history alone
