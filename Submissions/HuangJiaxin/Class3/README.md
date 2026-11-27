# Class 3 lab: PriceAmericanPut on market data

Jiaxin Huang. American put on a binomial tree (Cox, Ross and Rubinstein 1979), priced
by backward induction (dynamic programming) on hourly prices from `Class3/data/hourly/`.

Work in progress. The work follows the five steps from Class 1, one commit each:
(1) set up, (2) data and calibration, (3) tests first, (4) implementation,
(5) measurements and documentation.

## Run

From the repository root, Python 3.10 or later:

```bash
python3 -m pip install -r Submissions/HuangJiaxin/Class3/requirements.txt
```

Further commands will be added with each step.

## Data and calibration (`data.py`)

* Input: `Class3/data/hourly/<SYMBOL>.csv` (40 assets, 1 Nov 2021 to 31 Oct 2026, UTC).
  Every file has 43,823 rows: the hour 2023-03-24 13:00 UTC is missing. Rows are
  counted, never assumed.
* Window: the last N + 1 closes. "One year" is N = 8,760 periods (the last year has no
  gap, so it spans exactly 8,760 hours); "five years" is the whole file, N = 43,822
  periods over 43,823 hours.
* One tree period = one row step. T (for the interest rate) comes from the timestamps,
  in 365.25-day years. So for the five-year window the tree has one period fewer than
  the hours it spans; the effect on R is negligible (R per period changes by a factor
  of about 1 + 1e-10).
* s = sample standard deviation of the hourly log returns (divides by N - 1);
  u = e^s, d = 1/u, R = e^(0.04 T / N), q = (R - d)/(u - d); `calibrate` checks d < R < u.
* Contract: American put, S0 = K = P_0 (at the money), exercisable at hours 0..N.
