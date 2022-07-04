#  MarketData
import asyncio
import websockets
from datetime import datetime
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient

from includes.config import *
from pairs.pairs import Pair
from core.trade import Trader
from core.user import Account


class ScanMarket:
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
        self.all_pairs = pairs["all_pairs"]
        self.path = f'{self.topic}:{pairs["all_pairs"]}'

        self.pairs = pairs

    def display_prices(
        self,
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
            f"Pair {pair.name}  ::  SL ${pair.stop_loss}  ::  Price ${price}  ::  Buy ${pair.buy_price}  ::  Sell ${pair.sell_price}  ::  Mark ${pair.mark_price}  ::  Profit ${pair.profit}  ::  Loss  ${pair.loss_if_stopped}  ::  Reset ${pair.reset_price}"
        )
        log.info(f"Current Profit / Loss = {pair.profit_loss}")

        log.info(
            f'float(acc_amount_tokenA[0]["holds"]) == 0  ::  {float(acc_amount_tokenA[0]["holds"]) == 0}'
        )

        log.info(f"acc_amount_tokenA: {acc_amount_tokenA}")
        log.info(f"acc_amount_tokenB: {acc_amount_tokenB}")
        log.info(pair.buy_sell)

        if self.verbose:
            log.info(data)
            log.info(
                f"""
            {pair}:
            Price: {price}
            Sell Price: {pair.sell_price}
            Volume: {volume}
            
            """
            )
        log.info(spaces)

    async def place_buy_order(self, pair, logs_args):
        buy_price = pair.calc_buy_price()
        log.info(f"Setting Buy Order of {pair.amount} @  ${buy_price}")
        pair.buy_order_num = await self.trade.limit_order(
            pair.name, "buy", str(pair.amount), buy_price
        )
        pair.set_buy_prices(buy_price)
        pair.set_sell_prices(buy_price)
        pair.new_trade = False
        log.info(
            f"SET BUY Limit Order for {pair.amount} {pair.name} @ ${buy_price} for ${pair.buy_price_usd}\n{pair.buy_order_num}"
        )
        self.display_prices(*logs_args)

    async def place_sell_order(self, pair, acc_amount_tokenB, logs_args):
        if acc_amount_tokenB[0]["holds"] == "0" and pair.buy_sell != "sell":
            log.info(
                f"BUY Order Filled for {pair.amount} {pair.name} @ ${pair.buy_price} for ${pair.buy_price_usd}"
            )
            pair.sell_order_num = await self.trade.limit_order(
                pair.name, "sell", str(pair.amount), str(pair.sell_price)
            )
            log.info(
                f"SELL Limit Order Created for {pair.amount} {pair.name} @ ${pair.sell_price} for ${pair.sell_price_usd}\n{pair.sell_order_num}"
            )
            pair.buy_sell = "sell"
            self.display_prices(*logs_args)

    async def check_filled(self, pair, logs_args):

        filled = await self.trade.is_filled(pair.sell_order_num, pair.amount)
        if filled:
            pair.update_reset_and_checks(inc=True)
            log.info(
                f"LIMIT SELL Order Filled for {pair.amount} {pair.name} @ ${pair.sell_price} for ${pair.sell_price_usd}"
            )
            self.display_prices(*logs_args)
            return True
        return False

    async def cancel_flow(self, pair, logs_args, do_not_update_prices=False):
        # cancel_all_orders
        cancelled = await self.trade.cancel_all_orders(pair)
        log.info(f"MARKET SELL Order Filled: {cancelled}")
        wallet_amount = pair.amount  # float(acc_amount_tokenA[0]["available"])
        market_sell = await self.trade.market_trade(pair.name, "sell", wallet_amount)
        log.info(f"SELL Order Filled for {wallet_amount} ONE\n{market_sell}")
        self.display_prices(*logs_args)
        chillax = pair.update_reset_and_checks(
            do_not_update_prices=do_not_update_prices
        )
        if chillax:
            log.info(
                f"Stop Loss occured [ {pair.stop_loss_count} ] times in a row.. Chilling for {pair.DELAY} Seconds.."
            )
            await asyncio.sleep(pair.DELAY)

    async def check_stop_loss(self, price, pair, acc_amount_tokenA, logs_args):

        if price <= pair.stop_loss and float(acc_amount_tokenA[0]["holds"]) >= 1:
            self.cancel_flow(self, pair, logs_args)

        if price >= pair.reset_price:
            self.cancel_flow(
                self,
                pair,
                logs_args,
                do_not_update_prices=True,
            )

    # async def deal_msg(self, msg):
    #     topic = msg["topic"]
    #     await self.run_strategy(topic)

    # async def run_strategy(self, topic):
    #     pass

    async def deal_msg(self, msg):
        topic = msg["topic"]

        for p in self.all_pairs.split(","):
            if topic == f"{self.topic}:{p}":
                data = msg["data"]
                tokenA, tokenB = p.split("-")

                price = float(data["bestAsk"])
                volume = float(data["bestAskSize"])

                pair = self.pairs[p]

                if not pair.mark_price:
                    pair.mark_price = round(price, pair.decimals)

                acc_amount_tokenA = await self.user.get_account_data(tokenA)
                acc_amount_tokenB = await self.user.get_account_data(tokenB)

                # Set arguments for logging.
                logs_args = (
                    price,
                    data,
                    pair,
                    volume,
                    acc_amount_tokenA,
                    acc_amount_tokenB,
                )

                # Start new buy
                if pair.new_trade:
                    await self.place_buy_order(pair, logs_args)
                else:
                    await self.place_sell_order(pair, acc_amount_tokenB, logs_args)

                    # Check if filled and reset and start again if it is..
                    is_filled = await self.check_filled(pair, logs_args)

                    if not is_filled:
                        # Check price for stop loss - cancel, market sell and reset.
                        await self.check_stop_loss(
                            price, pair, acc_amount_tokenA, logs_args
                        )

    async def main(self):

        ws_client = await KucoinWsClient.create(
            None, self.client, self.deal_msg, private=False
        )

        try:
            await ws_client.subscribe(self.path)
        except websockets.exceptions.ConnectionClosedOK as e:
            log.error(e)
        while True:
            await asyncio.sleep(60, loop=loop)


if __name__ == "__main__":
    pairs = {
        "ONE-USDT": Pair(**metadata["ONE"]),
        # "LUNC-USDT": Pair(**metadata['LUNC']),
    }
    pairs.update({"all_pairs": ",".join([k for k in pairs.keys()])})
    sm = ScanMarket(creds, pairs, level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sm.main())
