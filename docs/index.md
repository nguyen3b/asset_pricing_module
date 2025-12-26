# Valuation Modeling Library

A lightweight Python library for **valuation modeling**, **cashflow valuation**, and **interest rate risk analysis**.

This project is designed as a **foundational valuation toolkit**, focusing on clarity, correctness, and extensibility rather than heavy abstractions or opaque APIs.

---

## Features

### Yield Curves
- Spot yield curve representation
- Flat and linear curve construction
- Discount factor computation
- Parallel curve shifts (basis-point shocks) for DV01 analysis

### Cashflows
- Flexible cashflow streams over discrete periods
- Common cashflow patterns:
  - level
  - linear
  - geometric growth
  - arithmetic growth
- Present value using:
  - flat interest rates
  - yield curve discount factors
- Optional perpetuity tail valuation

### Fixed Income Instruments
- Level-coupon bond implementation
- Pricing using:
  - flat yields
  - yield curve discount factors
- Cashflow schedules
- Effective-interest amortization tables
- Duration (Macaulay)
- DV01 via parallel curve shifts

---

## Quick example

```python
from fixed_income import Yield, Bond

# Build a flat yield curve
curve = Yield(10)
curve.set_flat_rate(1, 10, 4.0)

# Define a bond
bond = Bond(
    face=100,
    redemption=100,
    coupon_rate=5.0,
    maturity=10
)

# Price the bond and compute risk
price = bond.price_by_df(curve)
duration = bond.duration(curve)
dv01 = bond.dv01(curve)

print(price, duration, dv01)
```

## Documentation

- **Curves** – spot yield curves and discounting  
- **Cashflows** – cashflow construction and valuation  
- **Instruments** – fixed income instruments (currently bonds)

Each module includes usage examples and mathematical definitions.

---

## Roadmap

Planned extensions include:

- Zero-coupon bonds
- Floating-rate instruments
- Portfolio-level valuation and risk
- Alternative compounding conventions
- Additional curve construction methods

---

## Disclaimer

This library is intended for **educational and analytical purposes only**.
It is not production-grade financial software and should not be used for
live trading or investment decisions.
