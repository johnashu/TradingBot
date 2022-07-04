# Trade
from kucoin.client import Trade


class Trader:
    def __init__(self, creds) -> None:
        self.client = Trade(**creds)

    # place a limit buy order
    async def limit_order(
        self, pair: str, buy_sell: str, amount: str, price: str
    ) -> str:
        order_id = self.client.create_limit_order(pair, buy_sell, amount, price)
        return order_id["orderId"]

    # place a market buy order   Use cautiously
    async def market_trade(self, pair: str, buy_sell: str, amount: str) -> str:
        order_id = self.client.create_market_order(pair, buy_sell, size=amount)
        print(order_id)
        return order_id

    async def cancel_orders(self, order_ids: list) -> list:
        return [self.client.cancel_order(x) for x in order_ids]

    async def cancel_all_orders(self, pair: str, tradeType="trade") -> list:
        return self.client.cancel_all_orders(symbol=pair, tradeType=tradeType)

    async def view_order(self, orderId: str) -> dict:
        try:
            return True, self.client.get_order_details(orderId)
        except Exception as e:
            return False, {}

    async def get_fill_list(self, orderId, tradeType="TRADE"):
        return self.client.get_fill_list(tradeType, **{"orderId": orderId})

    async def is_filled(self, orderId: str, amount, tradeType="TRADE"):
        oid = await self.get_fill_list(orderId, tradeType=tradeType)
        filled_amount = sum([float(x["size"]) for x in oid["items"]])
        return filled_amount == amount
