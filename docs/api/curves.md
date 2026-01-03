# Curves

This module provides curve objects for **time-value-of-money modeling**,
including both **spot yield curves** and **discount factor curves**.

Curves are used to discount cashflows, price fixed-income instruments,
and perform basic interest-rate risk analysis.

The module currently supports:

- **Spot yield curves** (rates by maturity)
- **Discount factor curves** (discount factors by maturity)
- Common curve construction methods (flat, linear)
- Discount factor calculation
- Parallel curve shocks (basis-point shifts) for DV01-style risk

---

## Yield Curve (Spot Rates)

The `Yield` class represents a **spot yield curve**, storing spot interest
rates by maturity and deriving discount factors from those rates.

Spot rates are entered in **percent form** and stored internally as
**decimals**.

---

### Flat Yield Curve

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

## DiscountCurve (Discount Factor Curve)

The `DiscountCurve` class stores **discount factors directly** by period.

### Characteristics

- Each period `t` stores a discount factor `DF(t)`
- Discount factors typically lie in the interval `(0, 1]`
- Useful when discount factors are **observed** or **bootstrapped directly**
- Can be constructed manually or from zero-coupon bonds

---

### Construction from Zero-Coupon Bonds

A zero-coupon bond implies a discount factor at its maturity:

\[
DF(t) = \frac{P}{FV}
\]

where:

- \( P \) is the bond price  
- \( FV \) is the face value  
- \( t \) is the maturity in periods  

The class method  
`DiscountCurve.from_zcb(...)` constructs a discount curve from a list of
`ZeroCouponBond` instruments.

- Bonds are sorted by maturity
- Discount factors are populated at each bond’s maturity

---

### Example

```python
from fixed_income import DiscountCurve, ZeroCouponBond

zcbs = [
    ZeroCouponBond(maturity=2, face_value=100.0, price=95.12),
    ZeroCouponBond(maturity=3, face_value=100.0, price=92.18),
    ZeroCouponBond(maturity=5, face_value=100.0, price=87.01),
]

dc = DiscountCurve.from_zcb(zcbs)
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

