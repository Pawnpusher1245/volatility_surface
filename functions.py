import yfinance as yf
import matplotlib as plt
import math
import pandas as pd
from scipy.optimize import brentq
from datetime import datetime


def norm_cdf(x):
    """Cumulative distribution function for standard normal distribution"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def black_scholes_price(S, K, T, r, sigma, option_type='call', q=0.0):
    """
    Black–Scholes price for a European call/put.
    S is spot price
    K is strike price
    T is the time until expiry (years)
    r is risk free return rate (annualized)
    sigma is volatility (annualized)
    option_type is call/put
    q is annualized dividend yield
    """
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive numbers.")
    if T < 0:
        raise ValueError("T (time to maturity) cannot be negative.")
    if sigma < 0:
        raise ValueError("sigma (volatility) cannot be negative.")
    
    # if no volatility or no time until expirery
    option_type = option_type.lower()
    if T == 0 or sigma == 0:
        if option_type == "call":
            return max(0.0, S - K)
        elif option_type == "put":
            return max(0.0, K - S)
        else:
            raise ValueError("option_type must be 'call' or 'put'")    
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    
    if option_type == "call":
        price = S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * math.exp(-q * T) * norm_cdf(-d1)
    return price

def implied_volatility(market_price, S, K, T, r, option_type='call', q=0.0, low_vol=1e-4, high_vol=4.0):
    """
    Calculates the implied volatility from option data
    S, K, T, r, option_type, q: Black-Scholes parameters
    low_vol is lower bound for the volatility search
    high_vol is upper bound for the volatility search
    """
    
    def objective_function(sigma):
        return black_scholes_price(S, K, T, r, sigma, option_type, q) - market_price

    try:
        iv = brentq(
            f=objective_function,
            a=low_vol,            # The lower bound of the search interval.
            b=high_vol,           # The upper bound of the search interval.
            xtol=1e-6,            # The acceptable tolerance
        )
    except ValueError:
        iv = float('nan') 

    return iv
def get_spot_price(ticker):
    """
    Gets the real-time spot price for a ticker.
    It tries to get the regular market price and falls back to the previous
    day's close if a real-time price is not available.
    """
    info = ticker.info
    # 'regularMarketPrice' usually holds the most recent trading price.
    if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
        return info['regularMarketPrice']
    else:
        # Fallback for when real-time data is not available (e.g., pre-market)
        print("Warning: Real-time price not available, using previous day's close.")
        data = ticker.history(period="1d")
        return data['Close'].iloc[-1]
    
def get_options_data(ticker, option_type):
    """
    Returns all option data and all expiration dates
    """
    expiration_dates = ticker.options
    if option_type == "Call":
        option_dict = {date: ticker.option_chain(date).calls for date in expiration_dates}
    else:
        option_dict = {date: ticker.option_chain(date).puts for date in expiration_dates}

    for date, df in option_dict.items():
        df['expiration'] = date

    calls_concatenated = pd.concat(option_dict.values())
    return calls_concatenated, expiration_dates

def time_to_expiration(option) -> float:
    """Return time to expiration in years from today"""
    expiration_date_str = option.expiration
    expiration = datetime.strptime(expiration_date_str, "%Y-%m-%d")
    now = datetime.now()
    delta = expiration - now
    return delta.total_seconds() / (365 * 24 * 60 * 60)

def get_risk_free_rate():
    # 3-month Treasury yield
    rate_ticker = yf.Ticker("^IRX")  # ^IRX is 13-week T-bill yield
    rate = rate_ticker.history(period="1d")["Close"].iloc[-1] / 100
    return rate 

def get_dividend_yield():
    user_input = input(f"Enter annual dividend yield rate (default=0): ").strip()
    return float(user_input)
