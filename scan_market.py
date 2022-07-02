#  MarketData
from datetime import datetime
import asyncio
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from tools.utils import create_averages


class ScanMarket:

    mark_price = None

    def __init__(
        self, pairs: str, level: int = 2, depth: int = 5, market: str = "spotMarket"
    ) -> None:
        # is public
        self.client = WsToken()
        # is private
        # client = WsToken(key='', secret='', passphrase='', is_sandbox=False, url='')
        # is sandbox
        # client = WsToken(is_sandbox=True)
        self.topic = f"/{market}/level{level}Depth{depth}"
        self.path = f"{self.topic}:{pairs}"

    async def deal_msg(self, msg):
        if msg["topic"] == self.path:
            data = msg["data"]
            avg_ask = create_averages(data["asks"], data["timestamp"])
            avg_bid = create_averages(data["bids"], data["timestamp"])
            print(avg_ask)
            print(avg_bid)

        # elif msg['topic'] == '/spotMarket/level2Depth5:KCS-USDT':
        #     print(f'Get KCS level3:{msg["data"]}')

    async def main(self):

        ws_client = await KucoinWsClient.create(
            None, self.client, self.deal_msg, private=False
        )
        # await ws_client.subscribe('/market/ticker:BTC-USDT,ETH-USDT')
        await ws_client.subscribe(self.path)
        while True:
            await asyncio.sleep(60, loop=loop)


if __name__ == "__main__":
    sm = ScanMarket("ONE-USDT", level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sm.main())
