# Choosing a regression model family

*General reference for choosing a model family within the GLM class, used
by any stage in this project that needs one (currently Stages 1 and 2;
see the README). OLS, Poisson, and Negative Binomial (NB) are used as the
running example throughout, though the same framework applies to any
family, e.g. logistic or beta regression.*

An identification strategy (e.g. interrupted time series, comparing
outcomes before and after treatment) is the argument for why a comparison
supports a causal claim; the model family covered here is how that
comparison gets fit numerically. This document only concerns the latter.

## 1. Every model in the GLM class shares the same underlying structure

Generalized Linear Models (GLM) are a model class: a broad group of
regression models sharing a common structure. OLS, Poisson, Negative
Binomial, logistic, and beta regression are each a family within that
class (NB and beta are GLM-adjacent extensions rather than
strict textbook GLMs, but share the same structure and are treated the
same way here). Every family in this class is built from the same three
ingredients:

1. **Linear predictor**: the plain weighted sum of predictors:
   `η[t] = β0 + β1 * t + β2 * Post[t] + β3 * (t * Post[t])`
2. **Link function**: connects the linear predictor `η[t]` to the actual
   predicted mean `μ[t]`, enforcing whatever constraints the outcome has.
3. **Distribution family**: the assumed shape of random scatter around `μ[t]`.

Ingredient 1 is the comparison itself, e.g. before-vs-after treatment, and
comes from the identification strategy, not from this document. Any two
candidates within this class differ *only* in ingredients 2 and 3: the
linear predictor itself (and therefore whatever variables were built from
the data, e.g. `t`, `Post[t]`) stays the same regardless of which family
is ultimately chosen. As a worked example, here's how three common choices
compare:

| | OLS | Poisson | NB |
|---|---|---|---|
| Linear predictor | `η[t] = β0 + β1 * t + β2 * Post[t] + β3 * (t * Post[t])` | same | same |
| Link function | Identity: `μ[t] = η[t]` | Log: `μ[t] = exp(η[t])` | Log: `μ[t] = exp(η[t])` |
| Distribution | Gaussian around `μ[t]` | Poisson around `μ[t]` | NB around `μ[t]` |
| Mean–variance relationship | Variance constant, unrelated to `μ[t]` | `Var = μ[t]` | `Var = μ[t] + α*μ[t]²` |
| Can predict negative values? | Yes (a flaw for counts) | No | No |

The same three-row comparison could be built for any other pair or triple,
e.g. logistic regression uses a *logit* link and a Bernoulli distribution,
for a binary outcome instead of a count.

## 2. Why the link function matters

The **identity link** (OLS) lets predictions be any real number, positive
or negative, which is a problem for a count that can never go below zero.
The **log link** (Poisson and NB) forces `μ[t] = exp(η[t])`, which is always
positive regardless of how negative `η[t]` gets, and turns coefficients
into *multiplicative* effects (e.g. "×50 jump," "13.6% per month") rather
than additive ones, a natural fit for a process that plausibly compounds. Other
links serve the same purpose for other constraints: the *logit* link (used
in logistic regression) keeps predictions inside (0,1) for a binary or
probability outcome.

## 3. Example: choosing between two counts models (Poisson vs. NB)

Both use the log link and both are built for counts. The difference is the
**mean–variance relationship**:

- **Poisson** assumes `Variance = Mean` exactly, allowing no flexibility.
- **NB** adds a dispersion parameter `α`, allowing
  `Variance = Mean + α*Mean²`. When `α = 0`, it collapses back to Poisson.

Real count data is very often **overdispersed** (variance exceeds the mean):
bursty periods, batch effects, unmodelled real-world events all add scatter
beyond what pure Poisson randomness allows. Fitting Poisson on overdispersed
data doesn't bias the coefficient estimates much, but it understates their
standard errors, making effects look more statistically significant than
they really are. This is checkable, not a matter of preference: fit NB and
look at whether `α` is estimated as meaningfully greater than zero.

## 4. Decision checklist

This is the generic starting point for any stage's outcome: walk down
until one applies, regardless of whether the eventual comparison ends up
being OLS vs. Poisson vs. NB or something else entirely:

| Question | If yes → | Why |
|---|---|---|
| Continuous, roughly symmetric, can plausibly go negative? | OLS | Its noise assumption fits. |
| A count (0, 1, 2, ...) that can't go negative? | Poisson or NB | Keeps predictions valid. |
| ...and does variance exceed the mean? | NB over Poisson | Poisson understates uncertainty otherwise. |
| Binary outcome? | Logistic | Line can't be restricted to {0,1} otherwise. |
| Bounded proportion (0–1)? | Binomial / Beta | Keeps predictions in range. |

This checklist narrows the *shortlist*: it identifies which families are
plausible candidates. It is not, by itself, sufficient to declare a winner:
that requires actually fitting the candidates and comparing them, below.

## 5. Empirical comparison checklist

Once a shortlist of plausible families exists (typically 2–3, from the
decision checklist above), fit all of them on the same outcome and data
before choosing. For each candidate, record:

1. **Coefficients and their interpretation.** Note whether the model's
   effects are additive (OLS, e.g. "+50 units") or multiplicative
   (Poisson and NB, via the log link, e.g. "×1.5"), these aren't directly comparable
   numbers, which is exactly why steps 2–4 below matter.
2. **AIC** (Akaike Information Criterion, see Glossary). A difference of
   more than ~2 between candidates is usually considered meaningful, not
   noise.
3. **An assumption check specific to each candidate.** Watch
   for cases where two candidates share the same assumption rather than
   each having an independent one.
   - **OLS**: independent residuals (Durbin-Watson, see Glossary).
   - **Poisson and NB**: share one assumption, whether
     variance exceeds the mean (the dispersion test, see Glossary); treat
     agreement between their two versions of this check as confirmation,
     not two independent pieces of evidence.

   For a different shortlist (e.g. logistic or beta regression), the
   principle is the same even though the specific test isn't: identify
   which assumptions are genuinely distinct versus which candidates are
   just testing the same thing from different angles, and don't double-count
   the latter.
4. **Residual autocorrelation over time.** One check that applies
   regardless of which candidate is being compared:
   - **OLS**: reuses the same Durbin-Watson check as its assumption check
     above.
   - **Poisson and NB**: picking a count model over OLS fixes "can't predict
     negative counts" and "variance should scale with the mean," but it
     does **not** automatically fix correlated errors over time, so this
     still needs checking separately.

   Run this check on every candidate in the shortlist, not just the ones
   where it seems most relevant.

Recording the four items above for every candidate produces a table like
this:

| Candidate | Coefficients | AIC | Assumption check | Autocorrelation check |
|---|---|---|---|---|
| OLS | ... | ... | Durbin-Watson = ... | Durbin-Watson = ... |
| Poisson | ... | ... | Pearson chi-squared / df = ... | ... |
| NB | ... | ... | `α` confidence interval = ... | ... |

OLS's "Assumption check" and "Autocorrelation check" columns hold the
same number: Durbin-Watson tests both. That's expected, not a mistake;
Poisson and NB's distinctive assumption is separate from their
autocorrelation check.

**Only after this table is filled in for every candidate** should a model
be selected. The selection should cite the specific numbers that decided
it (e.g. "NB's AIC was X points lower than Poisson's, and its `α`
confidence interval excluded zero").

## 6. Glossary

| Term | Meaning | Other common names |
|---|---|---|
| Model class | A broad group of regression models sharing a common structure (e.g. GLM) | Modeling framework |
| Family | A specific distribution-and-link choice within a model class (e.g. Poisson and NB) | N/A |
| Model | A family fitted to specific data with specific predictors and estimated coefficients | Fitted model |
| Outcome | The variable being predicted | Dependent variable, response, target |
| Coefficient / parameter | A fixed value estimated by the model | N/A |
| Variable | Has a different value at every row/time point | N/A |
| Linear predictor (`η`) | The unconstrained weighted sum of predictors | Systematic component |
| Link function | Connects the linear predictor to the predicted mean | N/A |
| Error term (`ε`) | True, unobservable gap from the real process | Disturbance term |
| Residual | Observed gap from the *fitted* model | Estimated error (`ε̂`) |
| Overdispersion | Variance exceeding what the simpler distribution in a pair allows (e.g. Poisson) | N/A |
| AIC | A single score for a fitted model's fit-vs-complexity tradeoff; lower is better and it's directly comparable across different distribution families fit on the same outcome | Akaike Information Criterion |
| Durbin-Watson | A statistic (roughly 0-4) testing whether a model's residuals are independent over time; near 2 means independent, near 0 or 4 means strongly correlated | N/A |
| Dispersion test | A check of whether real data's variance matches what Poisson assumes (`Variance = Mean`) or exceeds it, via Poisson's Pearson chi-squared/df or NB's `α` confidence interval | Overdispersion test |
