#  MarketData
import asyncio
import websockets
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from includes.config import *
from includes.pairs import pairs

from core.trade import Trader
from core.user import Account


class ScanMarket:

    mark_price = None
    buy_price = 0
    sell_price = 0
    buy_sell = "buy"
    new_trade = True

    sell_order_num = 0
    buy_order_num = 0

    sell_perc = 1.005
    stop_loss_perc = 0.995
    swing_perc = 0.995

    def __init__(
        self,
        creds: dict,
        pairs: str,
        level: int = 2,
        depth: int = 5,
        market: str = "spotMarket",
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose
        # private
        self.client = WsToken(**creds)

        # TODO: Move to strategy logic class
        self.trade = Trader(creds)
        self.user = Account(creds)

        self.topic = f"/{market}/level{level}Depth{depth}"
        self.topic = f"/market/ticker"
        all_pairs = pairs["all_pairs"]
        self.path = f"{self.topic}:{all_pairs}"

        self.pairs = pairs

    def display_prices(
        self,
        stop_loss: str,
        price,
        data,
        pair,
        volume,
        acc_amount_tokenA,
        acc_amount_tokenB,
    ):
        spaces = "-" * 85
        log.info(spaces)
        log.info(
            f"Pair {pair}  ::  SL ${stop_loss}  ::  Price ${price}  ::  Buy ${self.buy_price}  ::  Sell ${self.sell_price}  ::  Mark ${self.mark_price}"
        )

        log.info(
            f'float(acc_amount_tokenA[0]["holds"]) == 0  ::  {float(acc_amount_tokenA[0]["holds"]) == 0}'
        )

        log.info(f"acc_amount_tokenA: {acc_amount_tokenA}")
        log.info(f"acc_amount_tokenB: {acc_amount_tokenB}")
        log.info(self.buy_sell)

        if self.verbose:
            log.info(data)
            log.info(
                f"""
            {pair}:
            Price: {price}
            Sell Price: {self.sell_price}
            Volume: {volume}
            
            """
            )
        log.info(spaces)

    def reset_data(self):
        self.buy_sell = "buy"
        self.new_trade = True
        self.mark_price = None
        self.buy_price = 0
        self.sell_price = 0
        self.sell_order_num = 0
        self.buy_order_num = 0

    def calc_buy_price(self, decimals):
        price = round(self.mark_price * self.swing_perc, decimals)
        log.info(f"Buy in Price  ${price}  ::  Mark Price  ${self.mark_price}")
        return price

    async def place_buy_order(self, price, pair, logs_args, token_decimals, amount):
        if price <= self.calc_buy_price(token_decimals):
            log.info(f"Setting Buy Order: {price}")
            self.display_prices(*logs_args)
            self.buy_order_num = await self.trade.limit_order(
                pair, "buy", str(amount), price
            )
            log.info(
                f"SET BUY Limit Order for {amount} ONE @ ${price} for ${price * amount}\n{self.buy_order_num}"
            )
            self.buy_price = price
            self.sell_price = round(price * self.sell_perc, token_decimals)
            self.new_trade = False

    async def place_sell_order(self, pair, acc_amount_tokenB, logs_args, amount):
        if acc_amount_tokenB[0]["holds"] == "0" and self.buy_sell != "sell":
            log.info(
                f"BUY Order Filled for {amount} ONE @ ${self.buy_price} for ${self.buy_price * amount}"
            )
            self.display_prices(*logs_args)
            self.sell_order_num = await self.trade.limit_order(
                pair, "sell", str(amount), str(self.sell_price)
            )
            log.info(
                f"SELL Limit Order for {amount} ONE @ ${self.sell_price} for ${self.sell_price * amount}\n{self.sell_order_num}"
            )
            self.buy_sell = "sell"

    async def check_filled(self, logs_args, amount):

        filled = await self.trade.is_filled(self.sell_order_num, amount)
        if filled:
            self.reset_data()
            log.info(
                f"LIMIT SELL Order Filled for {amount} ONE @ ${self.sell_price} for ${self.sell_price * amount}"
            )
            return True
        self.display_prices(*logs_args)
        return False

    async def check_stop_loss(
        self, price, pair, stop_loss, acc_amount_tokenA, logs_args, amount
    ):
        if price <= stop_loss and float(acc_amount_tokenA[0]["holds"]) >= 1:
            # cancel_all_orders
            cancelled = await self.trade.cancel_all_orders(pair)
            log.info(f"MARKET SELL Order Filled: {cancelled}")
            self.display_prices(*logs_args)
            wallet_amount = amount  # float(acc_amount_tokenA[0]["available"])
            market_sell = await self.trade.market_trade(pair, "sell", wallet_amount)
            log.info(f"SELL Order Filled for {wallet_amount} ONE\n{market_sell}")
            self.reset_data()

    async def deal_msg(self, msg):
        topic = msg["topic"]

        for pair in self.all_pairs.split(","):
            if topic == f"{self.topic}:{pair}":
                data = msg["data"]

                amount = self.pairs[pair]["amount"]

                tokenA, tokenB = pair.split("-")
                token_decimals = pairs[pair]["decimals"]

                price = float(data["bestAsk"])
                volume = float(data["bestAskSize"])

                if not self.mark_price:
                    self.mark_price = round(price, token_decimals)

                acc_amount_tokenA = await self.user.get_account_data(tokenA)
                acc_amount_tokenB = await self.user.get_account_data(tokenB)

                # Set Stop loss amount before creating sell order
                stop_loss = round(self.buy_price * self.stop_loss_perc, token_decimals)
                logs_args = (
                    stop_loss,
                    price,
                    data,
                    pair,
                    volume,
                    acc_amount_tokenA,
                    acc_amount_tokenB,
                )

                # Start new buy
                if self.new_trade:
                    await self.place_buy_order(
                        price, pair, logs_args, token_decimals, amount
                    )
                else:
                    await self.place_sell_order(
                        pair, acc_amount_tokenB, logs_args, amount
                    )

                    # Check if filled and reset and start again if it is..
                    is_filled = await self.check_filled(logs_args, amount)

                    if not is_filled:
                        # Check price for stop loss - cancel, market sell and reset.
                        await self.check_stop_loss(
                            price, pair, stop_loss, acc_amount_tokenA, logs_args, amount
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
    sm = ScanMarket(creds, pairs, level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sm.main())
