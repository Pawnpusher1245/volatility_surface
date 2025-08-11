import functions as fn
import yfinance as yf
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.interpolate import griddata
from interface import print_interface

ticker_str = "TSLA"
risk_free_rate = fn.get_risk_free_rate()
dividend_yield = 0.0
option_type = "Call"

ticker_str, risk_free_rate, dividend_yield, option_type = print_interface(ticker_str, risk_free_rate, dividend_yield, option_type)

print(f"Fetching {ticker_str} data...")
ticker = yf.Ticker(ticker_str)
spot = fn.get_spot_price(ticker)


calls_concatenated, expirations = fn.get_options_data(ticker, option_type)
moneyness = []
years_to_expiry = []
ivs = []
strikes = []

# to compare with yf iv. If running code on the weekends the data 
# will be stale while T is accurate causing higher IVs
yf_iv = []

# Iterate through all options and calculate iv
print("Calculating IV...")
for option in calls_concatenated.itertuples():
    time_to_expiration = fn.time_to_expiration(option)
    strike_price = option.strike
    option_price = (option.bid + option.ask)/2
    implied_volatility = fn.implied_volatility(option_price, spot, strike_price, time_to_expiration, risk_free_rate, option_type=option_type, q=dividend_yield)

    if not math.isnan(implied_volatility):
        moneyness.append(spot/strike_price)
        years_to_expiry.append(time_to_expiration)
        ivs.append(implied_volatility*100)
        yf_iv.append(option.impliedVolatility*100)
        strikes.append(strike_price)
print("Plotting...")
strikes = np.array(strikes)  
years_to_expiry = np.array(years_to_expiry)
ivs = np.array(ivs)

# Create grid to interpolate on
strike_grid = np.linspace(min(strikes), max(strikes), 50)
time_grid = np.linspace(min(years_to_expiry), max(years_to_expiry), 50)
strike_mesh, time_mesh = np.meshgrid(strike_grid, time_grid)

# Interpolate ivs on grid
iv_grid = griddata(
    points=(strikes, years_to_expiry),  
    values=ivs,
    xi=(strike_mesh, time_mesh),
    method='linear' 
)

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111, projection='3d')

# Plot the surface
surf = ax.plot_surface(strike_mesh, time_mesh, iv_grid, cmap='viridis')

ax.set_xlabel("Strike Price ($)")
ax.set_ylabel("Time to Expiration (Years)")
ax.set_zlabel("Implied Volatility (%)")

fig.colorbar(surf)

plt.title(f"Implied Volatility Surface ({ticker_str})" )
plt.show()

