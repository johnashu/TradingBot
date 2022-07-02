#  MarketData
from datetime import datetime as dt

ft = dt.fromtimestamp

ex = {
    "asks": [
        ["19261.9", "4.70068987"],
        ["19262.1", "0.578"],
        ["19262.3", "0.54044"],
        ["19262.5", "0.16"],
        ["19262.7", "0.2954762"],
    ],
    "bids": [
        ["19261.8", "0.14342041"],
        ["19260.9", "0.02775464"],
        ["19260.8", "0.44"],
        ["19260", "1.18921734"],
        ["19259.6", "0.00203"],
    ],
    "timestamp": 1656768274402,
}


def create_averages(arr: list, ts: int) -> dict:

    prices = [float(x[0]) for x in arr]
    volumes = [float(x[1]) for x in arr]
    rtn = dict(
        avg_price=sum(prices) / len(arr), avg_volume=sum(volumes) / len(arr), ts=ts
    )
    return rtn


avg_ask = create_averages(ex["asks"], ex["timestamp"])
avg_bid = create_averages(ex["bids"], ex["timestamp"])
print(avg_ask)
print(avg_bid)

import requests
ip = requests.get('https://checkip.amazonaws.com').text.strip()
print(ip)