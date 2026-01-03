from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .instruments import ZeroCouponBond

class BaseCurve(ABC):
    def __init__(self, n_periods: int ) -> None:
        self.n_periods = n_periods

    def check_bounds(self, period: int) -> None:
        if not (1 <= period <= self.n_periods):
            raise ValueError(f"Parameter not in bounds min: 1 and max is {self.n_periods}")

    @abstractmethod
    def value_at(self, period: int) -> float:
        pass

    def plot(self, start: int = 1, end: int | None = None, *, title: str | None = None) -> None:
        if end is None:
            end = self.n_periods

        xs = []
        ys = []

        for t in range(start, end + 1):
            try:
                y = self.value_at(t)
            except ValueError:
                continue   # skip missing periods

            if y is None:
                continue

            xs.append(t)
            ys.append(y)

        if not xs:
            raise ValueError("No valid data points to plot")

        plt.figure()
        plt.plot(xs, ys, marker="o")
        plt.xlabel("Period")
        plt.ylabel("Value")
        if title:
            plt.title(title)

        plt.show(block=True)
    
class Yield(BaseCurve):
    def __init__(self, n_periods: int):
        super().__init__(n_periods)
        self.rates = [None] * (n_periods + 1)

    def set_rate(self, period: int, rate: float) -> None:
        self.check_bounds(period)
        self.rates[period] = rate / 100
    
    def get_spot(self, period:int) -> float:
        self.check_bounds(period)
        if self.rates[period] == None:
            raise ValueError(f"period {period} is None")
        return self.rates[period]

    def set_flat_rate(self, start_period: int, end_period: int, rate: float) -> None:
        self.check_bounds(start_period)
        self.check_bounds(end_period)
        if end_period < start_period:
            raise ValueError(f"end period is smaller than start period")
        r = rate / 100 
        for i in range( start_period, end_period + 1):
            self.rates[i] = r
    
    def set_linear_rate(self, start_period: int, end_period: int, start_rate: float, end_rate: float) -> None:
        self.check_bounds(start_period)
        self.check_bounds(end_period)
        if end_period < start_period:
            raise ValueError(f"end period is smaller than start period")
        start_rate = start_rate / 100
        end_rate = end_rate / 100

        m = (end_rate - start_rate) / (end_period - start_period)
        b = start_rate - m * start_period

        for i in range(start_period, end_period + 1):
            self.rates[i] = i*m + b 

    def discount_factor(self, period: int) -> float:
        self.check_bounds(period)
        if self.rates[period] == None:
            raise ValueError(f"period {period} is None")
        rate = 1 + (self.rates[period])
        
        return pow(rate, -period)
    
    def shift(self, bp: float):
        
        shifted = Yield(self.n_periods)

        for i in range(1, self.n_periods + 1):
            if self.rates[i] == None:
                raise ValueError(f"period {i} is empty") 
            shifted.set_rate(i, (self.rates[i] + bp / 10000.0) * 100)
        
        return shifted
    
    def value_at(self, period: int):
        return self.get_spot(period)

    def print(self) -> None:
        for i in range(1, self.n_periods + 1):
            print(self.rates[i])    
    
    def get_period(self) -> int:
        return self.n_periods

class DiscountCurve(BaseCurve):
    def __init__(self, n_periods: int) -> None:
        super().__init__(n_periods) 
        self.rates = [None] * (n_periods + 1)

    def set_rate(self, period: int, rate: float) -> None:
        self.check_bounds(period)
        self.rates[period] = rate

    @classmethod
    def from_zcb(cls, zero_coupon_bonds: list[ZeroCouponBond]):
        zero_coupon_bonds.sort(key=lambda x: x.get_maturity())
        curve = cls(zero_coupon_bonds[len(zero_coupon_bonds)-1].get_maturity())
        for bond in zero_coupon_bonds:
            maturity = bond.get_maturity()
            curve.check_bounds(maturity)
            curve.set_rate(maturity, bond.implied_df())

        return curve

    def df(self, period: int) -> float:
        self.check_bounds(period)
        if self.rates[period] == None:
            raise ValueError(f"period {period} is empty")
        return self.rates[period]

    def value_at(self, period: int):
        return self.df(period)