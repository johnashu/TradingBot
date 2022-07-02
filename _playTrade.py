# Trade
from kucoin.client import Trade
from includes.config import envs

# key=envs.spot_key
# secret=envs.spot_secret

# key=envs.futures_key
# secret=envs.futures_secret

client = Trade(
    key=envs.spot_key,
    secret=envs.spot_secret,
    passphrase=envs.api_passphrase,
    is_sandbox=False,
    # url="https://api.kucoin.com",
)
print(dict(key=envs.spot_key,
    secret=envs.spot_secret,
    passphrase=envs.api_passphrase))

# place a limit buy order
order_id = client.create_limit_order("ONE-USDT", "buy", "10", "0.017")
print(order_id)
{'orderId': '62c057b6fe28860001db153f'}

# place a market buy order   Use cautiously
# order_id = client.create_market_order('ONE-USDT', 'buy', size='10')
order_ids = []
order_ids.append(order_id)
# cancel limit order
for x in order_ids:
    cancelled = client.cancel_order(x['orderId'])
    print(cancelled)
