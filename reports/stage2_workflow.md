# Stage 2 workflow: difference-in-differences

Tracks Stage 2 against the nine-step template in
`docs/causal_method_workflow_template.md`. Filled in as the work happens,
following the same convention as Stage 1's worked example in that document.

| Step | What happens | Outcome |
|---|---|---|
| **1. Frame the question** | Plain-language, falsifiable question | "Did the population PrEP targets see a larger drop in HIV notifications than other groups, beyond a trend they share?" |
| **2. Choose the identification strategy** | The argument for why a comparison supports a causal claim | Difference-in-differences on HIV notifications, comparing diagnoses attributed to male-to-male sexual contact against other transmission categories. PrEP overwhelmingly targets gay and bisexual men (`docs/scope_and_rationale.md`, Stage 2, references 1-2), so heterosexual/other notifications form a comparison group not materially treated by PrEP |
| **3. Understand the data structure** | Inspect grain, types, missingness | State x transmission category x quarter, 2013Q1-2022Q4, no missing data, non-negative count outcome (`data/data_dictionary.md`, `hiv_notifications_quarterly.csv`). Synthetic ground truth: the PrEP-driven reduction (ramping to ~42% relative) is applied only to the `MSM` category, starting 2018Q2 for all states except NSW (2016Q2, Stage 3's concern). Explored in `reports/data_exploration_hiv_notifications.md`: MSM falls 44% unconditionally (vs. 19% for the comparison group), but the national MSM series is already declining pre-2018, an NSW pre-trend, not a PBS-listing effect, the same issue Stage 1 found in dispensing |
| **4. Translate the identification strategy into variables** | Identify the outcome and the variables that encode the comparison (e.g. treatment timing, trend terms) | `hiv_notifications` as the outcome; `is_msm` and `post_pbs_listing` (fixed at April 2018) as the comparison variables; `state` and `quarter` fixed effects. **NSW excluded**, same resolution as Stage 1, for the same reason: its EPIC-NSW pre-trend would otherwise bias the April-2018 comparison (see `reports/data_exploration_hiv_notifications.md`) |
| **5. Shortlist candidate statistical models** | Match outcome type to plausible regression families, using the Decision checklist in `docs/model_family_concepts.md` | *Pending* |
| **6. Choose among candidates with evidence** | Fit all shortlisted candidates and compare (see `docs/model_family_concepts.md`'s empirical comparison checklist) | *Pending* |
| **7. Fit the model** | Run it | *Pending* |
| **8. Diagnose and validate** | Check assumptions held up | *Pending* |
| **9. Interpret and document** | Translate to plain English, record reasoning | *Pending* |

See `docs/scope_and_rationale.md` (Stage 2) for the full identification
argument and its named threat to identification.
