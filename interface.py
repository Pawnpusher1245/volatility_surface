def print_interface(ticker_str, risk_free_rate, dividend_yield, option_type):
    user_input = None
    while user_input != 1:
        try:
            user_input = int(input(
            f"""
        Current parameters are:
            Ticker: {ticker_str}
            Risk free rate (annual %): {risk_free_rate * 100:.2f}
            Dividend Yield (annual %): {dividend_yield * 100:.2f}
            Option type: {option_type}

            Enter (1-5)
            1: Plot implied volatility 
            2: Change ticker
            3: Change risk free rate
            4: Change dividend yield
            5. Change option type
            """
        )
            )
            if not 1 <= user_input <= 5:
                print("Invalid choice. Please enter a number between 1 and 5.")
                continue

            if user_input == 2:
                ticker_str = get_ticker_from_user()
            elif user_input == 3:
                risk_free_rate = get_risk_free_rate()
            elif user_input == 4:
                dividend_yield = get_dividend_yield()
            elif user_input == 5:
                option_type = get_option_type()

        except ValueError:
            print("Invalid input. Please enter an integer between 1 and 5.")

    return ticker_str, risk_free_rate, dividend_yield, option_type  

def get_ticker_from_user():
    ticker = input("Enter the ticker symbol").strip().upper()
    return ticker

def get_risk_free_rate():
    while True:
        try:
            rate = float(input("Enter the risk-free rate (in decimal, e.g., 0.05 for 5%): "))
            if rate < 0:
                print("Risk-free rate cannot be negative. Try again.")
            else:
                return rate
        except ValueError:
            print("Invalid input. Enter a numeric value in decimal form.")

def get_dividend_yield():
    while True:
        try:
            dividend = float(input("Enter the dividend yield (in decimal, e.g., 0.03 for 3%): "))
            if dividend < 0:
                print("Dividend yield cannot be negative. Try again.")
            else:
                return dividend
        except ValueError:
            print("Invalid input. Enter a numeric value in decimal form.")

def get_option_type():
    while True:
        option = input("Enter the option type (Call or Put): ").strip().lower()
        if option == "call":
            return "Call"
        elif option == "put":
            return "Put"
        else:
            print("Invalid input. Please enter 'Call' or 'Put'.")
