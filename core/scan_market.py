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
        self.client = WsToken(**creds)

        self.trade = Trader(creds)
        self.user = Account(creds)

        self.topic = f"/{market}/level{level}Depth{depth}"
        self.topic = f"/market/ticker"
        self.all_pairs = pairs["all_pairs"]
        self.path = f'{self.topic}:{pairs["all_pairs"]}'

        # https://docs.kucoin.com/#private-channels
        # Topic: /spotMarket/tradeOrders
        # This topic will push all change events of your orders.
        self.private_trade_topic = "/spotMarket/tradeOrders"

        self.pairs = pairs

    def display_prices(
        self,
        price: float,
        data: dict,
        pair: Pair,
        volume: float,
        acc_amount_tokenA: list,
        acc_amount_tokenB: list,
    ) -> None:
        spaces = "-" * 85
        log.info(spaces)
        log.info(
            f"""
Pair {pair.name}
Price ${price}
Mark ${pair.mark_price}
Buy ${pair.buy_price}
Sell ${pair.sell_price}
Profit ${pair.profit}
Loss  ${pair.loss_if_stopped}
SL ${pair.stop_loss}
Reset ${pair.reset_price}"
Limit Sells = {pair.limit_sells_count}
Market Sells = {pair.limit_sells_count}
            """
        )
        log.info(f"Current Profit / Loss = ${pair.profit_loss}")

        if self.verbose:
            log.info(
                f"""
            Data: {data}
            Pair: {pair}:
            Price: {price}
            Buy / Sell: {pair.buy_sell}
            Sell Price: {pair.sell_price}
            Volume: {volume}

            float(acc_amount_tokenA[0]["holds"]) == 0  ::  {float(acc_amount_tokenA[0]["holds"]) == 0}
            price >= pair.reset_price ::  {price >= pair.reset_price}
            float(acc_amount_tokenB[0]["holds"]) >= 1  :: {float(acc_amount_tokenB[0]["holds"]) >= 1}
            price <= pair.stop_loss  ::  {price <= pair.stop_loss}
            float(acc_amount_tokenA[0]["holds"]) > 0     ::  {float(acc_amount_tokenA[0]["holds"]) > 0}
            acc_amount_tokenA: {acc_amount_tokenA}
            acc_amount_tokenB: {acc_amount_tokenB}
            """
            )
        log.info(spaces)

    async def deal_msg(self, msg: dict) -> None:
        topic = msg["topic"]
        for p in self.all_pairs.split(","):
            pair = self.pairs[p]
            data = msg["data"]
            if topic == f"{self.topic}:{p}":
                tokenA, tokenB = p.split("-")
                await self.run_strategy(pair, data, tokenA, tokenB)
            if topic == self.private_trade_topic:
                await self.update_pair_status(p, pair, data)

    async def run_strategy(self, *args) -> None:
        pass

    async def update_pair_status(self, *args) -> None:
        pass

    async def main(self, loop: asyncio) -> None:

        ws_client = await KucoinWsClient.create(
            None, self.client, self.deal_msg, private=False
        )

        ws_client_private = await KucoinWsClient.create(
            None, self.client, self.deal_msg, private=True
        )

        trades = self.private_trade_topic
        try:
            await ws_client.subscribe(self.path)
            await ws_client_private.subscribe(trades)
        except websockets.exceptions.ConnectionClosedOK as e:
            log.error(e)
        while True:
            await asyncio.sleep(60, loop=loop)
