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
            f"Pair {pair.name}  ::   Price ${price}  ::  Buy ${pair.buy_price}  ::  Sell ${pair.sell_price}  ::  Mark ${pair.mark_price}  ::  Profit ${pair.profit}  ::  Loss  ${pair.loss_if_stopped}  ::  SL ${pair.stop_loss}  ::  Reset ${pair.reset_price}"
        )
        log.info(f"Current Profit / Loss = ${pair.profit_loss}")

        log.info(f"acc_amount_tokenA: {acc_amount_tokenA}")
        log.info(f"acc_amount_tokenB: {acc_amount_tokenB}")

        log.info(pair.buy_sell)

        if self.verbose:
            log.info(
                f"""
            Data: {data}
            Pair: {pair}:
            Price: {price}
            Sell Price: {pair.sell_price}
            Volume: {volume}

            float(acc_amount_tokenA[0]["holds"]) == 0  ::  {float(acc_amount_tokenA[0]["holds"]) == 0}
            price >= pair.reset_price ::  {price >= pair.reset_price}
            float(acc_amount_tokenB[0]["holds"]) >= 1  :: {float(acc_amount_tokenB[0]["holds"]) >= 1}
            price <= pair.stop_loss  ::  {price <= pair.stop_loss}
            float(acc_amount_tokenA[0]["holds"]) > 0     ::  {float(acc_amount_tokenA[0]["holds"]) > 0}
            """
            )
        log.info(spaces)

    async def deal_msg(self, msg):
        topic = msg["topic"]
        for p in self.all_pairs.split(","):
            if topic == f"{self.topic}:{p}":
                data = msg["data"]
                tokenA, tokenB = p.split("-")
                await self.run_strategy(p, data, tokenA, tokenB)

    async def run_strategy(self, *args):
        pass

    async def main(self, loop):

        ws_client = await KucoinWsClient.create(
            None, self.client, self.deal_msg, private=False
        )

        try:
            await ws_client.subscribe(self.path)
        except websockets.exceptions.ConnectionClosedOK as e:
            log.error(e)
        while True:
            await asyncio.sleep(60, loop=loop)
