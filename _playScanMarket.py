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

    async def deal_msg(self, msg):
        topic = msg["topic"]
        log.info(topic)
        for p in self.all_pairs.split(","):
            pair = self.pairs[p]
            data = msg["data"]
            if topic == f"{self.topic}:{p}":
                tokenA, tokenB = p.split("-")
                await self.run_strategy(pair, data, tokenA, tokenB)
            if topic == self.private_trade_topic:
                await self.update_pair_status(p, pair, data)

    async def run_strategy(self, *args):
        log.info("Inside Strategy")

    async def update_pair_status(self, *args):
        log.info("Inside Update Pairs")

    async def main(self, loop):

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


if __name__ == "__main__":
    pairs = {
        "ONE-USDT": Pair(**metadata["ONE"]),
        # "LUNC-USDT": Pair(**metadata['LUNC']),
    }

    pairs.update({"all_pairs": ",".join([k for k in pairs.keys()])})
    rb = ScanMarket(creds, pairs, level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rb.main(loop))


place_taker = {
    "symbol": "ONE-USDT",
    "orderType": "limit",
    "side": "buy",
    "orderId": "62c3e6112367290001cec6e9",
    "liquidity": "taker",
    "type": "match",
    "orderTime": 1657005585711758431,
    "size": "10",
    "filledSize": "10",
    "price": "0.018765",
    "matchPrice": "0.018765",
    "matchSize": "10",
    "tradeId": "62c3e6114f42a85380e12e3e",
    "remainSize": "0",
    "status": "match",
    "ts": 1657005585711758431,
}

filled_buy = {
    "symbol": "ONE-USDT",
    "orderType": "limit",
    "side": "buy",
    "orderId": "62c3e6112367290001cec6e9",
    "type": "filled",
    "orderTime": 1657005585711758431,
    "size": "10",
    "filledSize": "10",
    "price": "0.018765",
    "remainSize": "0",
    "status": "done",
    "ts": 1657005585711758431,
}

placed_sell = {
    "symbol": "ONE-USDT",
    "orderType": "limit",
    "side": "sell",
    "orderId": "62c3e664e122f80001b6f7fa",
    "type": "open",
    "orderTime": 1657005668598686531,
    "size": "10",
    "filledSize": "0",
    "price": "0.018763",
    "remainSize": "10",
    "status": "open",
    "ts": 1657005668598686531,
}

cancelled = {
    "symbol": "ONE-USDT",
    "orderType": "limit",
    "side": "sell",
    "orderId": "62c3e664e122f80001b6f7fa",
    "type": "canceled",
    "orderTime": 1657005668598686531,
    "size": "10",
    "filledSize": "0",
    "price": "0.018763",
    "remainSize": "0",
    "status": "done",
    "ts": 1657005744728667664,
}

filled_sell = {
    "symbol": "ONE-USDT",
    "orderType": "limit",
    "side": "sell",
    "orderId": "62c3e70b069bc70001f37580",
    "type": "filled",
    "orderTime": 1657005835239443510,
    "size": "10",
    "filledSize": "10",
    "price": "0.018702",
    "remainSize": "0",
    "status": "done",
    "ts": 1657005835804196800,
}

market_taker = {
    "symbol": "ONE-USDT",
    "orderType": "market",
    "side": "sell",
    "orderId": "62c3e93c7c7ecc00012e3c0b",
    "liquidity": "taker",
    "type": "match",
    "orderTime": 1657006396485752184,
    "size": "535.5612",
    "filledSize": "535.5612",
    "matchPrice": "0.018665",
    "matchSize": "535.5612",
    "tradeId": "62c3e93c4f42a85380e16451",
    "remainSize": "0",
    "status": "match",
    "ts": 1657006396485752184,
}

market_filled = {
    "symbol": "ONE-USDT",
    "orderType": "market",
    "side": "sell",
    "orderId": "62c3e93c7c7ecc00012e3c0b",
    "type": "filled",
    "orderTime": 1657006396485752184,
    "size": "535.5612",
    "filledSize": "535.5612",
    "remainSize": "0",
    "status": "done",
    "ts": 1657006396485752184,
}
