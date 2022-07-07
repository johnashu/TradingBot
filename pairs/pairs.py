class Pair:

    profit_loss = 0

    feeRate = 0.001

    limit_sells_count = 0
    market_sells_count = 0

    mark_price = None
    buy_sell = "buy"
    new_trade = True

    buy_price = 0
    buy_price_usd = 0
    buy_order_num = 0
    buy_filled = False

    sell_price = 0
    sell_price_usd = 0
    sell_order_num = 0
    sell_filled = False

    stop_loss = 0
    profit = 0
    loss_if_stopped = 0
    reset_price = 0

    market_sell = False
    market_sell_buy_price = 0

    sell_perc = 0
    stop_loss_perc = 0
    swing_perc_buy = 0
    swing_perc_reset = 0

    # Anti Dump flag.. If it dumps and we lose 3 x SL in a row, chill for a min!
    STOP_LOSS_MAX = 3
    stop_loss_count = 0
    DELAY = 600

    def __init__(
        self,
        name: str = "",
        price_decimals: int = 0,
        amount: float = 0,
        dollar_base_amount: float = 0,
        sell_perc: float = 0,
        stop_loss_perc: float = 0,
        swing_perc_buy: float = 0,
        swing_perc_reset: float = 0,
        token_amount_decimals: int = 4,
    ) -> None:
        self.name = name
        self.price_decimals = price_decimals
        self.amount = amount
        self.dollar_base_amount = dollar_base_amount
        self.sell_perc = sell_perc / 100 + 1
        self.stop_loss_perc = -stop_loss_perc / 100 + 1
        self.swing_perc_buy = swing_perc_buy / -100 + 1
        self.swing_perc_reset = swing_perc_reset / 100 + 1
        self.token_amount_decimals = token_amount_decimals

    def __str__(self):
        return self.name

    def reset_data(self):
        self.buy_sell = "buy"
        self.new_trade = True
        self.mark_price = None

        self.buy_price = 0
        self.buy_order_num = 0
        self.buy_price_usd = 0
        self.buy_filled = False

        self.sell_price = 0
        self.sell_order_num = 0
        self.sell_price_usd = 0
        self.sell_filled = False

        self.stop_loss = 0
        self.profit = 0
        self.loss_if_stopped = 0
        self.buy_price_usd = 0

    def calc_buy_price(self) -> float:
        price = round(self.mark_price * self.swing_perc_buy, self.price_decimals)
        return price

    def set_buy_prices(self, price: float) -> None:
        self.buy_price = price

        buy_price_usd_with_fee = price * self.amount
        print(buy_price_usd_with_fee)
        fee = buy_price_usd_with_fee * self.feeRate
        usd = round(buy_price_usd_with_fee - fee, self.price_decimals)
        self.buy_price_usd = usd
        self.market_sell_buy_price = usd

    def set_sell_prices(self, price: float) -> None:
        self.reset_price = round(
            self.mark_price * self.swing_perc_reset, self.price_decimals
        )
        self.sell_price = round(price * self.sell_perc, self.price_decimals)
        self.sell_price_usd = round(self.sell_price * self.amount, self.price_decimals)
        self.stop_loss = round(price * self.stop_loss_perc, self.price_decimals)
        self.profit = round(
            (self.sell_price * self.amount) - (self.buy_price * self.amount),
            self.price_decimals,
        )
        self.loss_if_stopped = round(
            (self.buy_price * self.amount) - (self.stop_loss * self.amount),
            self.price_decimals,
        )

    def stop_loss_counter(self, reset=False):
        if self.stop_loss_count > self.STOP_LOSS_MAX:
            self.stop_loss_count = 0
            return True
        elif reset:
            self.stop_loss_count = 0
        else:
            self.stop_loss_count += 1
        return False

    def update_profit_loss(self, inc: bool = False, market_sell: float = -1) -> None:
        if market_sell != -1:
            self.profit_loss += market_sell
            self.market_sells_count += 1
            self.market_sell_buy_price = 0
            self.market_sell = False

        elif inc:
            self.profit_loss += self.profit
            self.limit_sells_count += 1
        else:
            self.profit_loss -= self.loss_if_stopped

    def update_reset_and_checks(
        self, inc=False, reset: bool = False, update_prices: bool = False
    ) -> bool:

        if update_prices:
            self.update_profit_loss(inc=inc)

        res = self.stop_loss_counter(reset=reset)
        self.reset_data()

        return res
