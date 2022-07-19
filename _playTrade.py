# Trade
from kucoin.client import Trade
from includes.config import *
from tools.file_op import save_json
from tools.utils import round_down


class Trader:

    feeRate = 0.001

    def __init__(self, creds) -> None:
        self.client = Trade(**creds)

    # place a limit buy order
    def limit_order(self, pair: str, buy_sell: str, amount: str, price: str) -> str:
        order_id = self.client.create_limit_order(pair, buy_sell, amount, price)
        return order_id["orderId"]

    # place a market buy order   Use cautiously
    def market_trade(self, pair: str, buy_sell: str, amount: str) -> str:
        order_id = self.client.create_market_order(pair, buy_sell, size=amount)
        return order_id["orderId"]

    def cancel_orders(self, order_ids: list) -> list:
        return [self.client.cancel_order(x) for x in order_ids]

    def cancel_all_orders(self, pair: str, tradeType="trade") -> list:
        return self.client.cancel_all_orders(symbol=pair, tradeType=tradeType)

    def view_order(self, orderId: str) -> dict:
        try:
            return True, self.client.get_order_details(orderId)
        except Exception as e:
            return False, {"Error": e}

    def get_fill_list(self, orderId, tradeType="TRADE"):
        return self.client.get_fill_list(tradeType, **{"orderId": orderId})

    def is_filled(self, orderId: str, amount, tradeType="TRADE"):
        oid = self.get_fill_list(orderId, tradeType=tradeType)
        filled_amount = sum([float(x["size"]) for x in oid["items"]])
        return filled_amount == amount

    def get_market_price_sold(self, orderId: str):
        res, oid = self.view_order(orderId)
        if res:
            funds = float(oid["dealFunds"])
            print(funds)
            fee = float(oid["fee"])
            print(fee)
            total = funds - fee
            return total
        return 0

    def get_recent_orders(self) -> list:
        lst = self.client.get_recent_orders()
        save_json(os.path.join("data", "recent_orders"), lst)
        return lst


if __name__ == "__main__":

    pair = "ONE-USDT"
    buy_sell = "buy"
    amount = "10"
    price = "0.017"

    t = Trader(creds)
    # oid = t.market_trade(pair, "buy", round_down("10.000061233213", 4))
    # # print(oid)
    # oid = t.market_trade(pair, "sell", round_down("10.000061233213", 4))
    # print(oid)
    # l = t.limit_order(pair, buy_sell, amount, price)
    # print(l)
    # c = t.cancel_all_orders(pair)
    # print(c)

    oid = "62c5902022c6610001ab4cdb"
    # # # r = t.view_order(oid)
    # # # print(r)

    pl = 100
    rf = t.get_market_price_sold(oid)
    x = 150 - rf
    print(x)
    pl += x
    print(pl)

    recent = t.get_recent_orders()
    print(recent)

    # vo = t.view_order(oid)
    # print(vo)

    # print(t.is_filled(oid, 5000))
