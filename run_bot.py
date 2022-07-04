from core.scan_market import *


class RunBot(ScanMarket):
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
            f"SET BUY Limit Order for {pair.amount} {pair.name} @ ${buy_price} for ${pair.buy_price_usd}  ::  OrderId {pair.buy_order_num}"
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
                f"SELL Limit Order Created for {pair.amount} {pair.name} @ ${pair.sell_price} for ${pair.sell_price_usd}  ::  OrderId {pair.sell_order_num}"
            )
            pair.buy_sell = "sell"
            self.display_prices(*logs_args)

    async def check_sell_order_filled(self, pair, logs_args):

        filled = await self.trade.is_filled(pair.sell_order_num, pair.amount)
        if filled:
            log.info(
                f"LIMIT SELL Order Filled for {pair.amount} {pair.name} @ ${pair.sell_price} for ${pair.sell_price_usd}"
            )
            self.display_prices(*logs_args)
            pair.update_reset_and_checks(inc=True, update_prices=True, reset=True)
            return True
        return False

    async def cancel_flow(
        self,
        pair,
        orders,
        logs_args,
        reason="Stop Loss",
        update_prices=False,
        reset=False,
    ):
        # cancel_all_orders
        log.info(
            f"** {reason.upper()} **Cancelling OrderId {orders} for Pair {pair.name}"
        )
        cancelled = await self.trade.cancel_orders([orders])
        log.info(f"Orders Cancelled: {cancelled}")

        # Market sell if cancelled sell order
        # assign buy price to grab the correct P/L when sold.
        if not update_prices:
            pair.market_sell = True
            pair.market_sell_buy_price = pair.buy_price_usd

        # Updates
        self.display_prices(*logs_args)

        chillax = pair.update_reset_and_checks(update_prices=update_prices, reset=reset)
        if chillax:
            log.info(
                f"Stop Loss occured [ {pair.stop_loss_count} ] times in a row.. Chilling for {pair.DELAY} Seconds.."
            )
            await asyncio.sleep(pair.DELAY)
        else:
            log.info("Restarting Cycle..")

    async def check_stop_loss(self, price, pair, acc_amount_tokenA, logs_args):
        if price <= pair.stop_loss and float(acc_amount_tokenA[0]["holds"]) > 0:
            await self.cancel_flow(
                pair,
                pair.sell_order_num,
                logs_args,
                update_prices=True,
            )

    async def check_reset_buy(self, price, pair, acc_amount_tokenB, logs_args):
        if price >= pair.reset_price and float(acc_amount_tokenB[0]["holds"]) >= 1:
            await self.cancel_flow(
                pair, pair.buy_order_num, logs_args, reason="Reset Order", reset=True
            )

    async def check_market_sell(self, pair, acc_amount_tokenA):
        if pair.market_sell:
            wallet_amount = float(acc_amount_tokenA[0]["available"])
            log.info(f"Attempting Market Sell of {wallet_amount} {pair.name}")
            market_sell = await self.trade.market_trade(
                pair.name, "sell", wallet_amount
            )

            log.info(f"Market Sell orderId  ::  {market_sell}")

            sold_for = (
                pair.market_sell_buy_price
                - await self.trade.get_market_price_sold(market_sell)
            )

            log.info(
                f"MARKET SELL Order Filled for {wallet_amount} ONE  @ ${sold_for}::  orderId {market_sell}"
            )

            pair.update_profit_loss(market_sell=sold_for)

    async def run_strategy(self, p, data, tokenA, tokenB):

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

        # check if any market sells required
        await self.check_market_sell(pair, acc_amount_tokenA)

        # Start new buy
        if pair.new_trade:
            await self.place_buy_order(pair, logs_args)
        else:
            await self.place_sell_order(pair, acc_amount_tokenB, logs_args)

            # Check if filled and reset and start again if it is..
            is_filled = await self.check_sell_order_filled(pair, logs_args)

            if not is_filled:
                # Check price for stop loss - cancel, market sell and reset.
                await self.check_stop_loss(price, pair, acc_amount_tokenA, logs_args)

                # check if price has gone up and is a buy
                await self.check_reset_buy(price, pair, acc_amount_tokenB, logs_args)


if __name__ == "__main__":
    pairs = {
        "ONE-USDT": Pair(**metadata["ONE"]),
        # "LUNC-USDT": Pair(**metadata['LUNC']),
    }
    pairs.update({"all_pairs": ",".join([k for k in pairs.keys()])})
    rb = RunBot(creds, pairs, level=2, depth=5, market="spotMarket")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rb.main(loop))
