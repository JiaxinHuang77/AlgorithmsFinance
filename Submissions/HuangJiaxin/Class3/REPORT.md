# Class 3 lab report: PriceAmericanPut on market data

Jiaxin Huang, 27 November 2026. Code: `put.py`, `data.py`; raw results: `results/`.

## 1. Specification and model

* **Input**: S0 > 0, strike K ≥ 0, N ≥ 0 periods, up and down factors u, d, gross
  risk-free return R per period, with 0 < d < R < u (no arbitrage; checked, error otherwise).
* **Output**: the American put value at date 0 per unit of the asset, and the
  early-exercise boundary b_0..b_N. Inputs are not changed.
* **Model**: Cox, Ross and Rubinstein (1979) binomial tree; no dividends, fees or other
  frictions; exercise at any of the dates 0..N. q = (R − d)/(u − d).
* **Recurrence**: V_N,j = max(K − S_N,j, 0); for t < N,
  V_t,j = max(K − S_t,j, 0, (q V_t+1,j+1 + (1 − q) V_t+1,j) / R).
* **Calibration on data** (README, "Data and calibration"): one period = one hour (row);
  s = sample standard deviation of hourly log returns; u = e^s, d = 1/u;
  R = e^(0.04 T/N); S0 = K = P_0 (at the money).
* **Exercise rule**: exercise if K − S > 0 and K − S ≥ continuation value. The same rule
  is used in all three versions and in the reference.

## 2. Correctness

* **Why backward induction is right**: the value at a node depends only on the two
  nodes one date later, so computing dates N, N−1, ..., 0 in that order uses only
  values that are already final (dynamic programming over the subproblems (t, j)).
* **Why two arrays are enough** (slide 26): at date t, node j reads V[j] and V[j+1]
  (date t+1). Going through j in increasing order, V[j] is overwritten only after its
  last use, and V[j+1] is still the date t+1 value when it is read.
* **Evidence** (166 tests, `evidence/step4_tests_after_implementation.txt`):
  * the slide example gives exactly 1175/147 = 7.9932 (European 6.2925);
  * **my hand trace** of a three-period tree (`TRACE.md`: value 23.2, boundary none,
    50, 25, 50; European 15.2) is a test for all three versions;
  * an **independent exact reference** (fractions and recursion over every node, no
    shared code) agrees with all three versions on 40 random small trees, value and
    boundary, American and European;
  * edge cases: N = 0, K = 0, deep in the money (exercise at once), boundary at expiry;
  * the numpy version equals the plain version at N = 300 and N = 2,000 (every boundary
    value compared); five-year scale has no underflow or overflow (S0 d^N ≈ 1e−235);
  * calibration: sample standard deviation (N − 1), u d = 1, 0 < q < 1, row counting.
  * Tests were written first and failed on stubs (`evidence/step3_...`, 159 failed).

## 3. Algorithms and their cost (theory)

Let N be the number of periods; the tree has (N + 1)(N + 2)/2 ≈ N²/2 nodes.

| Version | Time | Extra memory (workspace) | Notes |
|---|---|---|---|
| `price_plain` (slides 23, 25) | Θ(N²) node updates, each a few Python operations | Θ(N): two lists S, V of N + 1 floats, plus the boundary (N + 1) | Python executes every node update itself |
| `price_numpy` | Θ(N²) element operations, but only N Python-level steps (one per date) | Θ(N): a few arrays of length ≤ N + 1 alive at once | per date: fixed overhead + vectorized work |
| `price_full_tree` (extra 2) | Θ(N²) | **Θ(N²)**: every S and V of the tree stored | only to show why the two-array idea matters |

Input reading is Θ(rows) and is timed separately. The boundary is part of the required
output (N + 1 numbers), not workspace. A cost model for the numpy version is
time ≈ a·N + b·N²/2: a fixed cost a per date plus b per node.

## 4. Results (tasks 2 to 5)

Measured on my MacBook Air (Apple Silicon, 8 cores, macOS 26.4.1), Python 3.14.7,
numpy 2.5.5, code `2f6683c` (`results/environment.json`, `results/run_log.txt`).

### Bitcoin (tasks 2 to 4; `results/bitcoin.csv`, figures `results/btc_*_boundary.png`)

| Window | N | S0 = K | Hourly s | American put | European put | Early-exercise premium | First exercise | Payoff |
|---|---|---|---|---|---|---|---|---|
| Last year | 8,760 | 109,608.01 | 0.461 % | 16,714.94 (15.2 % of S0) | 16,274.31 | 440.62 (2.6 %) | 2 Jun 2026 14:00 UTC at 68,019.30 | 41,588.71 |
| Five years | 43,822 | 61,560.49 | 0.540 % | 20,719.79 (33.7 % of S0) | 18,704.27 | 2,015.52 (9.7 %) | 18 Jun 2022 06:00 UTC at 19,439.26 | 42,121.23 |

* The boundary first appears at t = 137 (6 Nov 2025, about 58,300) in the one-year
  window and rises towards K at expiry (figure). Bitcoin first fell to the boundary on
  2 June 2026; the holder would have exercised then.
* In the five-year window the holder would have exercised in the 2022 crash, although
  Bitcoin ended **above** the strike (77,582 > 61,560): early exercise locks in the
  payoff, and a later recovery does not take it back.

### All 40 assets (task 5; `results/assets_1y.csv`, `results/assets_5y.csv`)

| Window | Exercised early | Put value, % of S0 (min / median / max) | Premium, % of American value (min / median / max) |
|---|---|---|---|
| One year | 36 of 40 (never: NEAR, TRX, UNI, ZEC) | 7.9 / 29.3 / 49.1 | 1.2 / 1.6 / 5.0 |
| Five years | 36 of 40 (never: BNB, PAXG, TRX, XRP) | 12.7 / 61.7 / 70.0 | 8.1 / 8.1 / 19.3 |

Every exercise happened before expiry. In the one-year window the 36 exercised assets
are exactly the 36 that ended below the strike; in the five-year window two assets
(including Bitcoin) were exercised although they ended above it.

The **largest premiums belong to the least volatile assets**: gold (PAXG, 19.3 % over
five years) and TRX. For a volatile asset most of the put's value is the chance of a
large fall, which a European put has too; for a calm asset the put is worth less, so
the interest earned by receiving K early is a larger share of it.

## 5. Performance review

### 5.1 Runtime (task 6; `results/runs.csv`)

| Run | N | Assets | plain Python (s) | numpy (s, median of 3) | plain / numpy |
|---|---|---|---|---|---|
| Bitcoin, one year | 8,760 | 1 | 5.85 | 0.182 | 32 |
| Bitcoin, five years | 43,822 | 1 | 130.8 | 3.09 | 42 |
| All assets, one year | 8,760 | 40 | | 9.1 (American and European) | |
| All assets, five years | 43,822 | 40 | | 158.4 (American and European) | |

Reading the 40 files took 1.9 to 2.0 s and is not included. Plain Python and the
40-asset runs were timed once (too slow to repeat); single-asset numpy runs had a warm-up
and three repeats, all saved.

* **Growth from one to five years** (N × 5.00, so Θ(N²) predicts × 25.0):
  plain Python × 22.4, numpy × 17.0, 40 assets × 17.4.
* **Plain Python is close to N²**: about 152 ns per node at one year and 136 ns at five
  years: each node is a handful of Python operations.
* **numpy is below 25 because of a fixed cost per date.** Fitting time = a·N + b·N²/2 to
  the two Bitcoin runs gives a ≈ 8.4 µs per date (the Python loop and about ten numpy
  calls per date) and b ≈ 2.8 ns per node. The fixed part is 40 % of the one-year time
  but only 12 % of the five-year time, so the ratio lies between 5 (all fixed cost) and
  25 (all per-node cost). At larger N it would approach 25.
* The 40 assets take about 40 × 2 single pricings (the European one is cheaper: no
  exercise test), so the total scales with the number of assets.

### 5.2 Memory (tracemalloc, separate runs)

| Run | Peak traced | Per period |
|---|---|---|
| Bitcoin one year, numpy | 0.58 MB | 66 bytes |
| Bitcoin one year, plain | 0.84 MB | 96 bytes |
| Bitcoin five years, numpy | 2.54 MB | 58 bytes |
| All 40 assets, five years, numpy | 3.31 MB | |

The two-array versions grow linearly in N. The measured peak is several times the
two main arrays (2 × 43,823 × 8 bytes ≈ 0.7 MB) because numpy creates temporary arrays
of the same length each date (continuation values, payoffs, the exercise mask, the new
V) and the boundary has N + 1 entries. The 40 assets are priced one after another, so
the peak does not grow with the number of assets. Traced memory excludes the input
prices already loaded, the interpreter and native stacks; it is not total process memory.

**Full tree vs two arrays (extra 2; `results/memory_full_tree.csv`)**, synthetic tree
with Bitcoin's volatility:

| N | Nodes | Full tree | Factor vs previous N | Two arrays (numpy) |
|---|---|---|---|---|
| 250 | 31,626 | 2.1 MB | | 0.018 MB |
| 500 | 125,751 | 8.3 MB | × 3.94 | 0.035 MB |
| 1,000 | 501,501 | 32.8 MB | × 3.97 | 0.068 MB |
| 2,000 | 2,003,001 | 130.4 MB | × 3.98 | 0.134 MB |
| 4,000 | 8,006,001 | 520.9 MB | × 3.99 | 0.266 MB |

Doubling N multiplies the full tree's memory by 4 (and its time too: 0.55 s to 2.14 s), as Θ(N²) predicts; the full tree
costs about 65 bytes per node (a Python float and two list slots for S and V).
**Projection, not measured**: one year (38.4 million nodes) would need about 2.5 GB and
five years (960 million nodes) about 62 GB; even as two float64 arrays the five-year
tree would need about 15 GB. These runs were not attempted. The two-array version
prices the same five-year tree in 2.5 MB: this is where "memory binds" in this lab.

### 5.3 Profiling (`profile_put.py`, `results/profile_*.txt`)

cProfile of one Bitcoin one-year pricing (run on the Linux environment on the same
laptop; used for shares only):
* `price_plain`: practically all time is inside the function's own loop (38 million
  node updates); there are no other calls to optimize. The bottleneck is the Python
  interpreter executing each node, which is what numpy removes.
* `price_numpy`: 8,761 dates; about 84 % of the time in the function's own array
  operations and about 15 % in the per-date `any` and `max` calls that find the
  boundary. Each date also pays a fixed Python overhead (about 8 µs, section 5.1), which
  is why numpy gains less at small N.

## 6. Predictions compared with the results

My predictions (`PREDICTIONS.md`, committed before the measurements):

| # | Prediction | Result | Verdict |
|---|---|---|---|
| 1 | Five years take about 25 times as long | plain × 22.4, numpy × 17.0 | Right for plain Python; numpy lower because of a fixed cost per date (5.1) |
| 2 | numpy is tens of times faster | 32 to 42 times | Correct |
| 3 | Two arrays fit easily in 3 GB | 2.5 MB (Bitcoin), 3.3 MB (40 assets) | Correct; the peak is a few times my 0.7 MB estimate because of numpy temporaries |
| 4 | Full tree: × 4 per doubling of N | × 3.94 to × 3.99 | Correct |
| 5 | Premium about one third of the value or larger | 2.6 % (one year), 9.7 % (five years) for Bitcoin; largest for gold | **Wrong**: the premium comes from earning interest on K earlier; at 4 % a year (about 0.0005 % per hour) it is small, and it is a larger share for calm assets, not volatile ones |
| 6 | The Bitcoin holder exercises early | Yes, 2 June 2026, payoff 41,589 | Correct |

## 7. Extras

1. **Early-exercise premium**: European put on the same tree for every run (sections 4, 6).
2. **Full tree vs two arrays**: section 5.2.
3. **Bitcoin figures**: `results/btc_1y_boundary.png` and `results/btc_5y_boundary.png`:
   price path, boundary, strike and first exercise (drawn from the saved CSV files by
   `plot_btc.py`).

## 8. Limitations

* **Hindsight**: s comes from the same window the put lives in; a holder at time 0
  would not know it. The exercise check (task 3) uses the boundary of that tree.
* The binomial model has constant volatility and interest; crypto prices have jumps,
  changing volatility and missing hours. One hour is missing in every file (2023-03-24
  13:00 UTC); the tree treats rows as periods.
* Prices are in USDT, a stablecoin, treated as US dollars; no fees or market impact.
* One machine; plain Python and 40-asset runs timed once. Absolute times depend on the
  machine; the growth ratios are the comparable part.
* tracemalloc measures Python and numpy allocations only, not total process memory.

## 9. Use of AI

*To be written by Jiaxin.*
