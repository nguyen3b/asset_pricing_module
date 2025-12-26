# Instruments

This module contains basic fixed-income instruments built on top of the
`CashFlowStream` and `Yield` curve utilities.

Currently implemented:

- `Bond`: level-coupon bond with redemption value, pricing, cashflow schedule,
  amortization table, duration, and DV01.

---

## Bond

A `Bond` is defined by:

- `face`: coupon face amount (used to compute coupon payments)
- `redemption`: principal paid at maturity (e.g., par value)
- `coupon_rate`: annual coupon rate in **percent** (e.g. `5.0` means 5%)
- `maturity`: number of periods to maturity

### Cashflows

The bond pays a level coupon each period and returns redemption at maturity.

Coupon per period:

$$
C = \frac{\text{face} \cdot \text{coupon_rate}}{100}
$$

Cashflow at time \( t \):

- For \( t = 1, \dots, n-1 \): \( CF_t = C \)
- For \( t = n \): \( CF_n = C + \text{redemption} \)

---

## Quick start

### Price with a flat yield

```python
from fixed_income import Bond

bond = Bond(face=100, redemption=100, coupon_rate=5.0, maturity=10)

price = bond.price(interest=4.0)   # 4% flat yield
print(price)
```

### Price with a yield curve (discount factors)

```python
from fixed_income import Yield, Bond

curve = Yield(10)
curve.set_flat_rate(1, 10, 4.0)

bond = Bond(face=100, redemption=100, coupon_rate=5.0, maturity=10)
price = bond.price_by_df(curve)

print(price)
```

### View the cashflow schedule

```python
df = bond.cashflow()
print(df)
```

** TO DO ADD a photo of DataFrame ** 

## Pricing

### Flat-rate pricing

`price(interest)` discounts the coupons and redemption at a constant rate $i$
(entered as a percent).

$$
P = C \cdot \frac{1 - (1 + i)^{-n}}{i} + \text{redemption} \cdot (1 + i)^{-n}
$$

where:

$$
i = \frac{\text{interest}}{100}
$$

$$
n = \text{maturity}
$$

$$
C = \text{coupon per period}
$$

> **Note:** this assumes $i > 0$.  
> If you plan to support $i = 0$, that case should be handled separately.

---

### Curve-based pricing

`price_by_df(curve)` uses spot discount factors from a `Yield` curve:

$$
P = \sum_{t=1}^{n-1} C \cdot DF(t) + (C + \text{redemption}) \cdot DF(n)
$$

where:

$$
DF(t) = \text{Yield.discount_factor}(t)
$$

---

## Amortization table

`amortiztion(yield_rate, purchase_price=None)` produces an effective-interest
amortization schedule (premium/discount amortization).

### Definitions

$$
y = \frac{\text{yield_rate}}{100}
$$

Book value at $t = 0$:

$$
BV_0 =
\begin{cases}
\text{purchase_price}, & \text{if provided} \\
\text{model price}, & \text{otherwise}
\end{cases}
$$

---

### Per-period calculations

For each period $t = 1, \dots, n$:

**Interest income**

$$
\text{Interest}_t = BV_{t-1} \cdot y
$$

**Payment**

$$
\text{Payment}_t =
\begin{cases}
C, & t < n \\
C + \text{redemption}, & t = n
\end{cases}
$$

**Amortization**

$$
\text{Amort}_t = \text{Interest}_t - C
$$

**Book value update**

$$
BV_t = BV_{t-1} + \text{Amort}_t
$$

---

The returned DataFrame includes the following columns:

- `period`
- `payment`
- `interest_income`
- `premium_discount_amort`
- `book_value`

---

## Duration

`duration(curve)` computes the **Macaulay duration** (in periods) using
curve-based discounting:

$$
D = \frac{\sum_{t=1}^{n} t \cdot PV(CF_t)}{P}
$$

where:

$$
P = \text{price_by_df(curve)}
$$

$$
PV(CF_t) = CF_t \cdot DF(t)
$$

### Expanded form

$$
D =
\frac{
\sum_{t=1}^{n-1} t \cdot (C \cdot DF(t))
+ n \cdot \big((C + \text{redemption}) \cdot DF(n)\big)
}{
P
}
$$

---

## DV01 (parallel shift)

`dv01(curve, bp=1.0)` estimates DV01 using a symmetric difference and a parallel
curve shift.

- `bp` is in **basis points** (e.g. `1.0` means 1 bp = 0.01%)

Let:

$$
P_{+} = \text{price under upward shift}
$$

$$
P_{-} = \text{price under downward shift}
$$

Then:

$$
DV01 \approx \frac{P_{-} - P_{+}}{2}
$$

This returns the approximate price change for a **1 bp move** (if `bp = 1.0`).

---
