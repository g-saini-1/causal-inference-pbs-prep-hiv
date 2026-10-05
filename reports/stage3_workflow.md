# Stage 3 workflow: staggered-adoption analysis

Tracks Stage 3 against the nine-step template in
`docs/causal_method_workflow_template.md`. Filled in as the work happens,
following the same convention as Stage 1's worked example in that document.

| Step | What happens | Outcome |
|---|---|---|
| **1. Frame the question** | Plain-language, falsifiable question | "Does NSW's earlier access via EPIC-NSW show the same decline earlier than the rest of the country, consistent with PrEP access itself driving it rather than some other national factor?" |
| **2. Choose the identification strategy** | The argument for why a comparison supports a causal claim | Staggered-adoption difference-in-differences, applied at the state level: NSW ran EPIC-NSW from 2016, ahead of the national PBS listing, so NSW was effectively treated earlier than other states |
| **3. Understand the data structure** | Inspect grain, types, missingness | Partially known. The treatment-timing evidence is already established: NSW's EPIC-NSW ramp starts March 2016, well ahead of the April 2018 national listing, see `reports/pbs_prep_dispensing_data_exploration.md`. The outcome data itself (HIV notifications by state, quarter, and transmission category, the same source Stage 2 uses) hasn't been inspected yet |
| **4. Translate the identification strategy into variables** | Identify the outcome and the variables that encode the comparison (e.g. treatment timing, trend terms) | *Pending* |
| **5. Shortlist candidate statistical models** | Match outcome type to plausible regression families, using the Decision checklist in `docs/model_family_concepts.md` | *Pending* |
| **6. Choose among candidates with evidence** | Fit all shortlisted candidates and compare (see `docs/model_family_concepts.md`'s empirical comparison checklist) | *Pending* |
| **7. Fit the model** | Run it | *Pending* |
| **8. Diagnose and validate** | Check assumptions held up | *Pending* |
| **9. Interpret and document** | Translate to plain English, record reasoning | *Pending* |

See `docs/scope_and_rationale.md` (Stage 3) for the full identification
argument and its named threat to identification.
