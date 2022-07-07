from core.scan_market import *


class Ticker(ScanMarket):

    current_price = 0

    async def run_strategy(self, pair: Pair, data: dict, *args) -> None:

        price = float(data["bestAsk"])
        volume = float(data["bestAskSize"])
        if self.current_price != price:
            print(f"{pair.name}  ::  {price:<8}  ::  {volume}")
            self.current_price = price


if __name__ == "__main__":
    pairs = {
        "ONE-USDT": Pair(**metadata["ONE"]),
        # "LUNC-USDT": Pair(**metadata['LUNC']),
    }
    pairs.update({"all_pairs": ",".join([k for k in pairs.keys()])})
    rb = Ticker(creds, pairs, level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rb.main(loop))
