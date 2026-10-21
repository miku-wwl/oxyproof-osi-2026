# Research request contract v2

## Phase 2.6 additions (2026-10-21)

The current grammar reports `grammar_version=2.6`. It additionally recognizes `degrees Celsius` / `degrees Kelvin`, the two presentation requests in the Phase 2.6 screening example, and the interval question below. This is a bounded compositional extension, not permission to discard unfamiliar clauses.

```
Find promising published bulk oxygen-ion conductors around 600 degrees Celsius, show their conductivity estimates, and tell me what evidence supports the comparison.
How does the ranking of the three comparable Huang materials change from 700 K to 1000 K? Explain the change using their published activation energies.
```

`Around` means the explicitly named **nominal point temperature**, not a tolerance/interval or uncertainty range; the response warns about that interpretation. `Promising` requests conditional descending conductivity within provisional source groups, with no performance threshold or guarantee. `Published` selects the existing curated-data scope, not a new literature search.

The exact named demonstration **three comparable Huang materials** resolves to source rows **1, 2, 3**, the previously defined flagship. It does not select any arbitrary three of the many Huang records. Model interval plans must explicitly propose those IDs; the independent validator checks them against the request, loaded DOI and exact comparison group. Ordinary “Huang materials” remains unresolved. Structured row IDs conflicting with this named selection abstain. Interval model schemas add nullable `row_ids`; old no-selection requests remain compatible.

Unknown suffixes, humidity, lifetime, cycling, conditions and conflicting temperatures remain rejected. Numeric punctuation in unverified requirements, such as `10,000 operating hours`, is preserved. A model's own refusal prose is also untrusted: on an independently covered request it becomes a typed `MODEL_PLAN_CONFLICT` with provider prose withheld. Actual user constraints remain visible in independent request coverage.

Every request still follows the contracts below. See `REAL_AGENT_ACCEPTANCE.md` for current execution evidence and the limits of unconfigured live integration.

Offline mode is a conservative English coverage grammar, not a language model. REAL_LLM uses the same independent coverage boundary: a model cannot declare an unfamiliar requirement satisfied. Unknown clauses produce `UNVERIFIED_CONSTRAINTS` with exact unresolved offsets/text in `request_coverage`. This deliberately sacrifices open-ended phrasing for completeness of supported requests.

Supported screening examples:

```
Find bulk conductors at 600 °C
Find bulk oxygen-ion conductors at 600 C with source provenance
Find perovskites bulk conductors at 700 K formula La0.95
Screen bulk conductors
Screen bulk conductivity at 1100 K
```

The last example requires a structured temperature. Recognized fields are one explicit C/K temperature, bulk/total, one exact loaded class label and `formula X` (a verbatim substring, not a composition or element constraint). Benign source provenance/citations/evidence/audit-report phrases are supported. Connectors and domain/action phrases are an allowlist; every remaining non-punctuation span is rejected. This is coverage checking rather than a blacklist of hazards.

The legacy empty request still screens at 600 C. When a structured temperature is supplied without a goal, the API does not invent a conflicting 600 C text constraint. Explicit text and structured fields must agree. Two temperatures in screening return `MULTIPLE_TEMPERATURE_CONSTRAINTS`; use the interval tool instead.

Interval examples:

```
Compare bulk conductors between 600 K and 1100 K with source provenance
Analyze total conductors from 400 C to 700 C
```

Both natural-language bounds require units. Structured interval fields are canonical and can be used with an empty goal. Every selected-temperature value uses `temperature_unit`. The interval tool selects exact row IDs or an exact catalog comparison-group identity; it does not interpret free-form composition restrictions.

`Inspect scientific evidence row 1` is the bounded evidence-inspection grammar on `/api/research`. Model selection must agree with independently determined tool intent. There are exactly three allowlisted tools, no executable code, shell command, URL or path argument. No source record is sent to the provider. Provider prose and invented citations are never used in product explanations.

Humidity/wet air, oxygen partial pressure, phase stability, lifetime, cycling, synthesis, cost, toxicity, fabrication, element exclusions and performance thresholds are unsupported requirements, as are unfamiliar meaningful clauses. Structured formula substring filtering does not establish these properties.

Guided UI goals carry `goal_origin=GENERATED` and stay synchronized with temperature/unit/type controls. Editing the goal changes it to MANUAL; control edits preserve manual text and contradictions are reported. “Use synchronized goal” explicitly replaces manual text at the user's click. `goal_origin` never bypasses backend checks.

Bounds: 2000 goal characters; one provider call, 25 s transport timeout / 5 s connect timeout, 64 KiB maximum provider envelope, 2000 output tokens, no retries. Provider failure is `UNAVAILABLE`; it does not trigger a silent offline run. Deterministic explanations and next-action templates use only validated outputs and clearly proposed measurements.
