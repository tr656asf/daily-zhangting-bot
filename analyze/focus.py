def get_focus_stocks(stocks):
    stocks = sorted(stocks, key=lambda x: x.get("days", 1), reverse=True)
    return stocks[:3]
