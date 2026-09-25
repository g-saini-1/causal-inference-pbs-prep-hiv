# Causal method workflow template

Use this once per identification strategy in the project's methodology (see
`scope_and_rationale.md`), one copy for Stage 1, one for Stage 2, and so
on. Steps 1–2 are usually already answered for every stage up front, since
they live in `scope_and_rationale.md`. Steps 3–9 are done separately per
stage, since they depend on that stage's specific data and model.

## Template

| Step | What happens | Outcome |
|---|---|---|
| **1. Frame the question** | Plain-language, falsifiable question | *(see the stage's bold heading in `scope_and_rationale.md`)* |
| **2. Choose the identification strategy** | The argument for why a comparison supports a causal claim | *(the stage's identification strategy in `scope_and_rationale.md`)* |
| **3. Understand the data structure** | Inspect grain, types, missingness | |
| **4. Translate the identification strategy into variables** | Turn the chosen strategy into actual columns | |
| **5. Shortlist candidate statistical models** | Match outcome type to plausible regression families | |
| **6. Choose among candidates with evidence** | Test assumptions, don't guess | |
| **7. Fit the model** | Run it | |
| **8. Diagnose and validate** | Check assumptions held up | |
| **9. Interpret and document** | Translate to plain English, record reasoning | |

## Worked example: Stage 1 (interrupted time series)

| Step | What happens | Outcome |
|---|---|---|
| **1. Frame the question** | Plain-language, falsifiable question | "Did dispensing itself change sharply at the moment of the PBS listing?" |
| **2. Choose the identification strategy** | The argument for why a comparison supports a causal claim | Interrupted time series on dispensing |
| **3. Understand the data structure** | Inspect grain, types, missingness | Outcome is a non-negative count |
| **4. Translate the identification strategy into variables** | Turn the chosen strategy into actual columns | `t`, `post_listing[t]`, `months_since_post_listing[t]` |
| **5. Shortlist candidate statistical models** | Match outcome type to plausible regression families | OLS, Poisson, and NB (see `docs/model_family_concepts.md` for the general reasoning) |
| **6. Choose among candidates with evidence** | Fit all shortlisted candidates and compare (see `docs/model_family_concepts.md`'s empirical comparison checklist) | *Pending, not yet run side-by-side; will be written up in a "Model family selection" section of `reports/stage1_interrupted_time_series.md` once run* |
| **7. Fit the model** | Run it | *Pending final model choice* |
| **8. Diagnose and validate** | Check assumptions held up | Durbin-Watson = 0.255 found for the OLS fit (strong autocorrelation), not yet checked for other candidates |
| **9. Interpret and document** | Translate to plain English, record reasoning | *Pending final model choice* |

## How to use this in the project

Two jobs, from the same table:

**As a progress tracker.** An Outcome cell marked *Pending*, or filled in
only partway, means that step isn't finished yet for that stage. Stage 1's
own table above shows both: step 8 has a partial result (OLS only, not yet
the other candidates), and steps 6, 7, and 9 are still marked *Pending*, an
accurate, at-a-glance status, not just a to-do note. When starting Stage 2,
copy the template into a new file (`stage2_workflow.md`, see "Practically"
below) and fill cells in as the work happens rather than after the fact.
This keeps the table honest as a status view rather than reconstructed
later.

**As an index into the detailed docs.** Most Outcome cells are short
because the full reasoning lives elsewhere: general, reusable reasoning in
a stage-agnostic reference (e.g. `docs/model_family_concepts.md`), and the
specific application, fitted results, and interpretation in a per-stage
report (e.g. `reports/stage1_interrupted_time_series.md`). Once a stage
has a detailed doc for a given step, link to it from that cell
instead of re-describing it. The table becomes a map of "what's been
decided and where the reasoning for it lives," which is more useful once
the project has several stages' worth of documents than trying to hold
everything in one place.

Practically, this suggests one file per stage (`stage2_workflow.md`,
`stage3_workflow.md`, ...), each starting from the template above, sitting
alongside that stage's detailed docs and linked from them. Stage 1's worked
example stays inline in this document as the reference illustration of how
to fill the template out; it doesn't get its own `stage1_workflow.md`.
