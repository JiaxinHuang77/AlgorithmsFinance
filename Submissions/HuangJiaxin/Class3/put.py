"""PriceAmericanPut (Class 3 lab). Step 3: interface only; the tests must fail."""


def price_plain(S0, K, u, d, R, N, american=True):
    """Two arrays, plain Python (slides 23 and 25). Returns (value, boundary)."""
    raise NotImplementedError


def price_numpy(S0, K, u, d, R, N, american=True):
    """Two arrays, numpy vectorized over the nodes of one date. Returns (value, boundary)."""
    raise NotImplementedError


def price_full_tree(S0, K, u, d, R, N, american=True):
    """Stores every node of the tree (extra 2: memory grows like N^2)."""
    raise NotImplementedError


def tree_prices(S0, u, d, t):
    """Stock prices S_t,j for j = 0..t (numpy array)."""
    raise NotImplementedError


def first_exercise(path, boundary, K):
    """First t >= 1 with path[t] <= boundary[t] and K - path[t] > 0: (t, payoff) or None."""
    raise NotImplementedError
