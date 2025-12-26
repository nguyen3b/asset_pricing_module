# Curves

This module provides a simple **spot yield curve** object for discounting cashflows by period.

The curve stores spot rates `r[t]` (as decimals) for `t = 1..n_periods` and exposes:

- setting individual spot rates
- building common shapes (flat, linear)
- discount factor calculation
- parallel curve shocks (basis-point shifts) for DV01-style risk

---

## Quick start

### Create a flat curve and compute discount factors

```python
from fixed_income import Yield

curve = Yield(n_periods=10)
curve.set_flat_rate(start_period=1, end_period=10, rate=4.0)  # 4% flat

df_1y = curve.discount_factor(1)
df_5y = curve.discount_factor(5)

print(df_1y, df_5y)
```

### Create a linear curve (e.g 3% -> 5%)

```python

curve = Yield(10)
curve.set_linear_rate(
    start_period=1,
    end_period=10,
    start_rate=3.0,
    end_rate=5.0
)

print(curve.discount_factor(10))

```

### Parallel Shifts

```python

curve = Yield(10)
curve.set_flat_rate(1, 10, 4.0)

curve_up = curve.shift(1.0)     # +1 bp (0.01%)
curve_dn = curve.shift(-1.0)    # -1 bp

```

## Notes

- Rates are entered as **percent values** (e.g. `4.0` means 4%) and are stored internally as **decimals** (e.g. `0.04`).

- Period indexing is **1-based**.  
  Period `0` is not used for curve rates and is reserved for valuation time.

- The discount factor for period \( t \) is computed using **annual compounding**:

$$
DF(t) = (1 + r_t)^{-t}
$$

where:

- \( r_t \) is the spot rate for period \( t \)  
- \( t \) is the time in periods

