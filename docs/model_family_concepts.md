# Choosing a regression model family

*General reference: applies to any stage in this project whose outcome
needs a model-family decision, not just Stage 1. This covers the framework
for choosing among regression families in general (GLMs); OLS, Poisson, and
Negative Binomial are used throughout as a running worked example (drawn
from Stage 1's count outcome), but the same framework and checklist extend
to other families too, e.g. logistic or beta regression for a binary or
bounded outcome. Use this to support the "shortlist candidate statistical
models" step; see the relevant stage's own report (e.g. `reports/stage1_interrupted_time_series.md`
for Stage 1; its model-family comparison is pending and will land in a
"Model family selection" section there once run) for how it was actually
applied to that stage's data.*

## 1. Every GLM shares the same underlying structure

Every regression model in the GLM (Generalized Linear Model) family, e.g.
OLS, Poisson, Negative Binomial, logistic, beta, is built from the same
three ingredients:

1. **Linear predictor**: the plain weighted sum of predictors:
   `η[t] = β0 + β1 * t + β2 * Post[t] + β3 * (t * Post[t])`
2. **Link function**: connects the linear predictor `η[t]` to the actual
   predicted mean `μ[t]`, enforcing whatever constraints the outcome has.
3. **Distribution family**: the assumed shape of random scatter around `μ[t]`.

Any two candidates within this family differ *only* in ingredients 2 and 3.
The linear predictor itself (and therefore whatever variables you've
built from your data, e.g. `t`, `Post[t]`) stays the same
regardless of which family you end up choosing. As a worked example, here's
how three common choices compare:

| | OLS | Poisson | Negative Binomial |
|---|---|---|---|
| Linear predictor | `η[t] = β0 + β1 * t + β2 * Post[t] + β3 * (t * Post[t])` | same | same |
| Link function | Identity: `μ[t] = η[t]` | Log: `μ[t] = exp(η[t])` | Log: `μ[t] = exp(η[t])` |
| Distribution | Gaussian around `μ[t]` | Poisson around `μ[t]` | Negative Binomial around `μ[t]` |
| Mean–variance relationship | Variance constant, unrelated to `μ[t]` | `Var = μ[t]` | `Var = μ[t] + α*μ[t]²` |
| Can predict negative values? | Yes (a flaw for counts) | No | No |

The same three-row comparison could be built for any other pair or triple,
e.g. logistic regression uses a *logit* link and a Bernoulli distribution,
for a binary outcome instead of a count.

## 2. Why the link function matters

The **identity link** (OLS) lets predictions be any real number, positive
or negative, which is a problem for a count that can never go below zero.
The **log link** (Poisson, NB) forces `μ[t] = exp(η[t])`, which is always
positive regardless of how negative `η[t]` gets, and turns coefficients
into *multiplicative* effects (e.g. "×50 jump," "13.6% per month") rather
than additive ones, a natural fit for a process that plausibly compounds. Other
links serve the same purpose for other constraints: the *logit* link (used
in logistic regression) keeps predictions inside (0,1) for a binary or
probability outcome.

## 3. Example: choosing between two counts models (Poisson vs. Negative Binomial)

Both use the log link and both are built for counts. The difference is the
**mean–variance relationship**:

- **Poisson** assumes `Variance = Mean` exactly, allowing no flexibility.
- **Negative Binomial** adds a dispersion parameter `α`, allowing
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

This checklist narrows the *shortlist*: it tells you which families are
plausible candidates. It is not, by itself, sufficient to declare a winner:
that requires actually fitting the candidates and comparing them, below.

## 5. Empirical comparison checklist

Once you have a shortlist of plausible families (typically 2–3, from the
decision checklist above), fit all of them on the same outcome and data
before choosing. Don't declare a winner from theory alone, and don't
carry a conclusion over from a different session or a different fit of the
data. For each candidate, record:

1. **Coefficients and their interpretation.** Note whether the model's
   effects are additive (OLS: "+2,878 dispensings") or multiplicative
   (Poisson/NB via the log link: "×49.6"). These aren't directly comparable
   numbers, which is exactly why steps 2–4 below matter.
2. **AIC** (Akaike Information Criterion). Unlike raw coefficients, AIC
   *is* directly comparable across different distribution families fit on
   the same outcome variable, since it's built from each model's own
   log-likelihood plus a penalty for its number of parameters. Lower AIC
   is better; a difference of more than ~2 is usually considered
   meaningful, not noise.
3. **A diagnostic specific to each candidate's own assumption, but watch
   for cases where two candidates share the same assumption rather than
   each having an independent one.** As a worked example, for the three
   candidates used elsewhere in this document:
   - **OLS** assumes independent residuals, a genuinely distinct
     assumption from the other two, checked with Durbin-Watson (≈2 is
     good; values near 0 or 4 indicate strong autocorrelation).
   - **Poisson and Negative Binomial sit on either side of one shared
     assumption**, not two separate ones: whether variance exceeds the
     mean. Checking it via Poisson's Pearson chi-squared statistic divided
     by residual degrees of freedom (well above 1 signals overdispersion)
     and checking it via NB's `α` confidence interval (excluding zero
     signals the same thing) are two routes to the same answer. Treat
     agreement between them as confirmation, not as two independent
     pieces of evidence.
   For a different shortlist (e.g. logistic or beta regression), the
   principle is the same even though the specific test isn't: identify
   which assumptions are genuinely distinct versus which candidates are
   just testing the same thing from different angles, and don't double-count
   the latter.
4. **One check that applies regardless of which candidates you're
   comparing: residual autocorrelation over time.** Picking a count model
   (Poisson/NB) over OLS fixes "can't predict negative counts" and
   "variance should scale with the mean". It does **not** automatically
   fix correlated errors over time. Run this check on every candidate in
   your shortlist, not just the ones where it seems most relevant.

**Only after this table is filled in for every candidate** should a model
be selected. The selection should cite the specific numbers that decided
it (e.g. "NB's AIC was X points lower than Poisson's, and its `α`
confidence interval excluded zero") rather than asserting a winner, the
same way Stage 1's own model-choice doc should cite its own comparison
table once it exists.

## 6. Glossary

| Term | Meaning | Other common names |
|---|---|---|
| Outcome | The variable being predicted | Dependent variable, response, target |
| Coefficient / parameter | A fixed value estimated by the model | N/A |
| Variable | Has a different value at every row/time point | N/A |
| Linear predictor (`η`) | The unconstrained weighted sum of predictors | Systematic component |
| Link function | Connects the linear predictor to the predicted mean | N/A |
| Error term (`ε`) | True, unobservable gap from the real process | Disturbance term |
| Residual | Observed gap from the *fitted* model | Estimated error (`ε̂`) |
| Overdispersion | Variance exceeding what the simpler distribution in a pair allows (e.g. Poisson) | N/A |
