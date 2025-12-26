# Cashflows

This module provides a simple **cash flow stream** object for building and valuing cashflows over discrete periods.

A `CashFlowStream` stores cashflows `cf[t]` for `t = 0..n_periods` and supports:

- setting cashflows by period
- filling common cashflow patterns (level, linear, geometric, arithmetic)
- present value using a **flat interest rate**
- present value using a **spot yield curve** (`Yield`) discount factors
- optional perpetuity tail valuation at the final period

---

## Quick start

### Create a level cashflow stream and compute PV at a flat rate

```python
from fixed_income import CashFlowStream

cfs = CashFlowStream(n_periods=5)
cfs.fill(100)                 # 100 each period (t=1..5)
cfs.set_period(0, -450)       # initial outflow at t=0

pv = cfs.pv(interest=5.0)     # 5% flat annual rate
print(pv)
```

### Build a linear cashflow stream (e.g. 100 → 200)

```python
from fixed_income import CashFlowStream

cfs = CashFlowStream(10)
cfs.fill_linear(
    start_period=1,
    end_period=10,
    start_amt=100,
    end_amt=200
)

print(cfs.pv(interest=4.0))

```

### Use a yield curve for discounting

```python
from fixed_income import Yield, CashFlowStream

curve = Yield(10)
curve.set_flat_rate(1, 10, 4.0)   # 4% flat spot curve

cfs = CashFlowStream(10)
cfs.fill(100)
cfs.set_period(0, -900)

pv = cfs.pv_df(curve)
print(pv)

```

### Perpetuity tail after the final period

```python
from fixed_income import CashFlowStream

cfs = CashFlowStream(5)
cfs.fill(50)
cfs.set_period(0, -800)

pv = cfs.pv_perpetuity(interest=6.0)
print(pv)

```

## Notes

- Cashflows are stored for periods $t = 0 \dots n_{\text{periods}}$.
  - $t = 0$ is the valuation time (often an initial investment or price).
  - $t \ge 1$ are future cashflows.

- Period indexing is **1-based** for future periods, consistent with the yield
  curve module.

- All fill methods write cashflows into the internal array.
  If any period required for valuation is `None`, valuation will raise an error.

---

## Cashflow builders

### `set_period(period, cashflow)`

Sets a single cashflow at a specific period.

---

### `fill(cashflow)`

Fills every period $t = 1 \dots n_{\text{periods}}$ with the same cashflow amount.

---

### `fill_linear(start_period, end_period, start_amt, end_amt)`

Creates a linear ramp from `start_amt` to `end_amt` over the specified range
(inclusive).

Cashflows follow:

$$CF_t = CF_{\text{start}} + m (t - \text{start})$$

where:

$$m = \dfrac{CF_{\text{end}} - CF_{\text{start}}}{\text{end} - \text{start}}$$

---

### `fill_geometric(start_period, end_period, start_amt, rate)`

Creates geometric growth cashflows.

- `rate` is entered as a **percent** (e.g. `3.0` means 3%).

Cashflows follow:

$$CF_t = CF_{\text{start}} (1 + g)^{(t - \text{start})}$$

where:

$$g = \dfrac{\text{rate}}{100}$$

---

### `fill_arithmetic(start_period, end_period, start_amt, increase_amt)`

Creates arithmetic growth cashflows.

Cashflows follow:

$$CF_t = CF_{\text{start}} + k (t - \text{start})$$

where:

$k$ is the per-period increase amount.

---

## Present value

### Flat-rate PV

`pv(interest)` computes:

$$PV = \sum_{t=0}^{n} CF_t (1 + i)^{-t}$$

where:

$$i = \dfrac{\text{interest}}{100}$$

Annual compounding is assumed.

---

### Perpetuity tail PV

`pv_perpetuity(interest)` computes the present value up to $n_{\text{periods}}$
and then adds a perpetuity tail based on the final cashflow:

$$PV = \sum_{t=0}^{n} CF_t (1 + i)^{-t} + \left(\dfrac{CF_n}{i}\right)(1 + i)^{-n}$$

This assumes the final cashflow repeats forever beyond the last period.

---

### Curve-discounted PV

`pv_df(curve)` discounts each cashflow using spot discount factors from a
`Yield` curve:

$$PV = CF_0 + \sum_{t=1}^{n} CF_t \cdot DF(t)$$

where $DF(t)$ is computed by `Yield.discount_factor(t)`.
