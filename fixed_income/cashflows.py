import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from .curves import Yield

from typing import Optional, List

class CashFlowStream:
    def __init__(self, n_periods):
        self.n_periods = n_periods
        self.cf = [0.0] + [None] * (n_periods)

    def set_period(self,period: int, cashflow: float) -> None:
        self.check_bounds(period)
        self.cf[period] = cashflow

    def fill(self, cashflow: float) -> None:
        cashflow = float(cashflow)
        for i in range(1, self.n_periods + 1):
            self.cf[i] = cashflow 

    def fill_linear(self, start_period: int, end_period: int, start_amt: float, end_amt: float) -> None:
        self.check_bounds(start_period)
        self.check_bounds(end_period)
        if(start_period > end_period): 
            raise ValueError("start period is greater than endding period")

        start_amt = float(start_amt)
        end_amt = float(end_amt)

        if(start_period == end_period): 
            self.cf[start_period] = start_amt
            return

        m = (end_amt - start_amt) / (end_period - start_period)
        b = start_amt - m * start_period

        for i in range(start_period, end_period +1):
            self.cf[i] = m * i + b

    def fill_geometric(self, start_period: int, end_period: int, start_amt: float, rate: float) -> None:
        self.check_bounds(start_period)
        self.check_bounds(end_period)
        if(start_period > end_period):
            raise ValueError("start period is greater than endding period")

        start_amt = float(start_amt)
        g = 1 + float(rate) / 100

        for i in range(0, end_period + 1 - start_period):
            self.cf[start_period + i] = start_amt * (g ** i) 

    def fill_arithmetic(self, start_period: int, end_period: int, start_amt: float, increase_amt: float) -> None:
        self.check_bounds(start_period)
        self.check_bounds(end_period)
        if(start_period > end_period):
            raise ValueError("start period is greater than endding period") 

        start_amt = float(start_amt) 
        increase_amt = float(increase_amt)        
        for i in range(0, end_period + 1 - start_period):
            self.cf[start_period + i] = start_amt + increase_amt * i 

    def pv(self, interest: float) -> float:
        present_value = 0.0
        interest = interest / 100
        for i in range(self.n_periods + 1):
            if self.cf[i] == None:
                raise ValueError (f"period {i} is None")
            present_value += self.cf[i] * (1 + interest) ** -i 

        return present_value
    
    def pv_perpetuity(self, interest: float) -> float:
        present_value = self.pv(interest)
        interest = interest / 100
        if interest <= 0:
            raise ValueError("intrest must be > 0")        
        cf = self.cf[self.n_periods]
        if cf == None:
            raise ValueError(f"{self.n_periods} period is None")

        present_value +=  (cf / interest) * (1 + interest) ** -self.n_periods

        return present_value
        
    def pv_df(self, curve: Yield) -> float:
        if self.n_periods > curve.get_period():
            raise ValueError(f"Cash flow stream is greater than curve periods")

        pv = self.cf[0]
        for i in range(1, self.n_periods + 1):
            if self.cf[i] == None:
                raise ValueError(f"period {i} is None")
            pv += self.cf[i] * curve.discount_factor(i)

        return pv

    def check_bounds(self, period: int) -> None:
        if not (0 <= period <= self.n_periods): 
            raise ValueError(f"period {period} is out of bounds")

    def print(self) -> None:
        for i in range(self.n_periods + 1):
            print(self.cf[i])  
