import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, List

class Yield:
    n_periods: int
    rates: List[Optional[float]]
    def __init__(self, n_periods):
        self.n_periods = n_periods
        self.rates = [None] * (n_periods + 1)

    def set_rate(self, period: int, rate: float) -> None:
        self.check_bounds(period)
        self.rates[period] = rate / 100

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
    
    def print(self) -> None:
        for i in range(1, self.n_periods + 1):
            print(self.rates[i])    

    def check_bounds(self, period: int) -> None:
        if not (1 <= period <= self.n_periods):
            raise ValueError(f"Parameter not in bounds min: 1 and max is {self.n_periods}")
    
    def get_period(self) -> int:
        return self.n_periods