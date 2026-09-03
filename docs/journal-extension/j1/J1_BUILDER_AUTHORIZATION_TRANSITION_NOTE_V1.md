# J1 — Builder Authorization Transition Note V1

Status: `BUILDER AUTHORIZATION PRESENT — BUILD NOT DISPATCHED`

This note marks the transition from the V3 pre-authorization review state to a repository state containing the canonical builder authorization.

The pre-authorization review packets and their tests remain historical evidence of the state that existed when they were written. Assertions whose only purpose was to prove `J1_BUILDER_AUTHORIZATION_V1.json` absent must be updated before this transition PR can merge; they must not be bypassed or hidden. All scientific authorization remains absent.

Current intended state after this PR is reviewed and merged:

```text
builder authorization      PRESENT
controlled build dispatch  NONE
BUILD_A / BUILD_B          NONE
environment artifact       ABSENT
environment authority      ABSENT
J1 authorization           ABSENT
J1 scientific execution    NOT PERMITTED
```
