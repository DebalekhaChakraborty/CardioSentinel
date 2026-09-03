# J1 — Builder Authorization Transition Checklist V1

This checklist is non-authoritative. It exists so the authorization transition is reviewed as a state change rather than as a file drop.

- Canonical authorization JSON present at the enforced path.
- Authorization ID is `J1-ENV-BUILDER-AUTH-001`.
- Human authorizer identity is `DebalekhaChakraborty`.
- V3 machine values are copied exactly.
- Provenance destination is derived from the authorization ID.
- No workflow dispatch performed.
- No BUILD_A / BUILD_B output exists.
- No environment artifact or environment authority exists.
- No J1 scientific authorization exists.
- Historical pre-authorization tests that assert absence must be transitioned explicitly before merge; they must not be skipped.
