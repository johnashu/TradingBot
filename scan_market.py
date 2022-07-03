#  MarketData
from datetime import datetime
import asyncio
import websockets
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from tools.utils import create_averages
from includes.config import *

from core.trade import Trader
from core.user import Account


class ScanMarket:

    buy_price = None
    sell_price = None
    buy_sell = "buy"
    new_trade = True

    sell_order_num = 0
    buy_order_num = 0

    def __init__(
        self,
        creds: dict,
        pairs: str,
        level: int = 2,
        depth: int = 5,
        market: str = "spotMarket",
    ) -> None:
        # private
        self.client = WsToken(**creds)

        # TODO: Move to strategy logic class
        self.trade = Trader(creds)
        self.user = Account(creds)

        self.topic = f"/{market}/level{level}Depth{depth}"
        self.topic = f"/market/ticker"
        self.path = f"{self.topic}:{pairs}"
        self.pairs = pairs

    async def deal_msg(self, msg):
        topic = msg["topic"]

        for pair in self.pairs.split(","):
            if topic == f"{self.topic}:{pair}":
                data = msg["data"]

                amount = 5000
                sell_perc = 1.0005
                stop_loss_perc = 0.9995

                tokenA, tokenB = pair.split("-")

                price = float(data["bestAsk"])
                volume = float(data["bestAskSize"])

                acc_amount_tokenA = await self.user.get_account_data(tokenA)
                acc_amount_tokenB = await self.user.get_account_data(tokenB)

                log.debug(data)
                log.debug(
                    f"""
                {pair}:
                Price: {price}
                Sell Price: {self.sell_price}
                Volume: {volume}
                
                """
                )
                log.info(acc_amount_tokenA)
                log.info(acc_amount_tokenB)
                log.info(self.buy_sell)

                stop_loss = price

                if self.new_trade:
                    log.info(f"Setting Buy Order: {price}")
                    self.buy_order_num = await self.trade.limit_order(
                        pair, "buy", str(amount), price
                    )
                    log.info(
                        f"SET BUY Limit Order for {amount} ONE @ ${price} for ${price * amount}\n{self.buy_order_num}"
                    )
                    self.buy_price = price
                    self.sell_price = round(price * sell_perc, 6)
                    self.new_trade = False

                else:
                    stop_loss = round(self.buy_price * stop_loss_perc, 6)

                    if acc_amount_tokenB[0]["holds"] == "0" and self.buy_sell != "sell":
                        log.info(
                            f"BUY Order Filled for {amount} ONE @ ${self.buy_price} for ${self.buy_price * amount}"
                        )
                        self.sell_order_num = await self.trade.limit_order(
                            pair, "sell", str(amount), str(self.sell_price)
                        )
                        log.info(
                            f"SELL Limit Order for {amount} ONE @ ${self.sell_price} for ${self.sell_price * amount}\n{self.sell_order_num}"
                        )
                        self.buy_sell = "sell"

                    log.info(
                        f'float(acc_amount_tokenA[0]["holds"]) == 0  ::  {float(acc_amount_tokenA[0]["holds"]) == 0}'
                    )

                    filled = await self.trade.is_filled(self.sell_order_num, amount)
                    log.info(f"Is filled?? {filled}")
                    if filled:
                        self.buy_sell = "buy"
                        self.buy_price = None
                        self.new_trade = True
                        log.info(
                            f"SELL Order Filled for {amount} ONE @ ${self.sell_price} for ${self.sell_price * amount}"
                        )

                    if price <= stop_loss and float(acc_amount_tokenA[0]["holds"]) >= 1:
                        # cancel_all_orders
                        cancelled = await self.trade.cancel_all_orders(pair)
                        log.info(f"MARKET SELL Order Filled: {cancelled}")
                        wallet_amount = float(acc_amount_tokenA[0]["available"])
                        market_sell = await self.trade.market_buy(
                            pair, "sell", wallet_amount
                        )
                        log.info(
                            f"SELL Order Filled for {wallet_amount} ONE\n{market_sell}"
                        )
                        self.buy_sell = "buy"
                        self.buy_price = None
                        self.new_trade = True
                        log.info(
                            f"STOP LOSS ${stop_loss}  ::  Price ${price}  ::  Sell Price ${self.sell_price}"
                        )

    async def main(self):

        ws_client = await KucoinWsClient.create(
            None, self.client, self.deal_msg, private=False
        )

        try:
            await ws_client.subscribe(self.path)
            # await ws_client.subscribe(self.path)
        except websockets.exceptions.ConnectionClosedOK as e:
            log.error(e)
        while True:
            await asyncio.sleep(60, loop=loop)


if __name__ == "__main__":
    pairs = "ONE-USDT"
    sm = ScanMarket(creds, pairs, level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sm.main())
