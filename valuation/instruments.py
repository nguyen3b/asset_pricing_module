from __future__ import annotations
import pandas as pd
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .curves import Yield

class Bond:
    def __init__(self, face, redemption, coupon_rate, maturity):
        self.face = face
        self.redemption = redemption
        self.coupon_rate = coupon_rate
        self.maturity = maturity

    def coupons(self):
        return self.face * self.coupon_rate / 100

    def pv(self, interest):
        interest = interest / 100
        coupon = self.coupons()
        discount = pow((1 + interest), - self.maturity)

        return  coupon * ((1 - discount)/interest) + self.redemption * (discount)
    
    def pv_by_df(self, curve: Yield) -> float:
        if self.maturity > curve.get_period():
            raise ValueError("yeild curve is to small for maturity periods")
        coupon = self.coupons()
        price = 0.0
        for i in range(1, self.maturity):
            price += coupon * curve.discount_factor(i)

        price += (coupon + self.redemption) * curve.discount_factor(self.maturity)

        return price

    def cashflow(self) -> pd.DataFrame:
        coupon = self.coupons()
        periods = list(range(1, self.maturity+1))

        data = {
            "period": periods,
            "coupons": [coupon] * self.maturity,
            "principal": [0] * (self.maturity-1) + [self.redemption]
        }

        df = pd.DataFrame(data)
        df["total_cf"] = (df["coupons"] + df["principal"])

        return df

    def amortization(self, yield_rate, purchase_price = None):
        y = yield_rate / 100
        c = float(self.coupons())
        n = int(self.maturity)
        redemption = float(self.redemption)
        bv = float(purchase_price) if purchase_price is not None else float(self.pv(yield_rate)) 

        rows = []
        rows.append({
            "period": 0,
            "payment": 0.0,
            "interest_income": 0.0,
            "premium_discount_amort": 0.0,
            "book_value": bv
        })

        for t in range(1, n +1):
            interest_income = bv * y
            payment = c if t < n else (c + redemption)
            
            amort = interest_income - c
            bv = bv + amort

            rows.append({
                "period": t,
                "payment": payment,
                "interest_income": interest_income,
                "premium_discount_amort": amort,
                "book_value": bv
            })
            
        return pd.DataFrame(rows)

    def duration(self, curve: Yield) -> float:
        price = self.pv_by_df(curve) 
        c =  self.coupons()
        weighted_pv = 0.0

        for i in range(1, self.maturity):
            weighted_pv += (c * curve.discount_factor(i)) * i 
        weighted_pv += ((c + self.redemption) * curve.discount_factor(self.maturity)) * self.maturity
        return weighted_pv / price

    def dv01(self, curve: Yield, bp = 1.0) -> float:
        shock_up = curve.shift(bp)
        shock_down = curve.shift(-bp)

        price_up = self.pv_by_df(shock_up)
        price_down = self.pv_by_df(shock_down)

        return (price_down - price_up) / 2.0 

class ZeroCouponBond:
    def __init__(self, maturity: int, face_value: float, price: float):
        self.maturity = maturity
        self.face_value = face_value
        self.pv = price

    def __repr__(self):
        return f"ZCB(T={self.maturity}, FV={self.face_value}, Price={self.pv:.4f})"

    def get_maturity(self) -> int:
        return self.maturity

    def implied_df(self) -> float:
        if self.pv == None:
            raise ValueError("Need market price to imply DF")
        
        return self.pv / self.face_value
    