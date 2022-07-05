class Pair:

    profit_loss = 0

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
    DELAY = 60
    stop_loss_count = 0

    def __init__(
        self,
        name: str = "",
        decimals: int = 0,
        amount: float = 0,
        sell_perc: float = 0,
        stop_loss_perc: float = 0,
        swing_perc_buy: float = 0,
        swing_perc_reset: float = 0,
    ) -> None:
        self.name = name
        self.decimals = decimals
        self.amount = amount
        self.sell_perc = sell_perc / 100 + 1
        self.stop_loss_perc = -stop_loss_perc / 100 + 1
        self.swing_perc_buy = swing_perc_buy / -100 + 1
        self.swing_perc_reset = swing_perc_reset / 100 + 1

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

    def calc_buy_price(self):
        price = round(self.mark_price * self.swing_perc_buy, self.decimals)
        return price

    def set_buy_prices(self, price: float) -> None:
        self.buy_price_usd = round(price * self.amount, self.decimals)
        self.buy_price = price
        self.market_sell_buy_price = round(price * self.amount, self.decimals)

    def set_sell_prices(self, price: float) -> None:
        self.reset_price = round(self.mark_price * self.swing_perc_reset, self.decimals)
        self.sell_price = round(price * self.sell_perc, self.decimals)
        self.sell_price_usd = round(self.sell_price * self.amount, self.decimals)
        self.stop_loss = round(price * self.stop_loss_perc, self.decimals)
        self.profit = round(
            (self.sell_price * self.amount) - (self.buy_price * self.amount),
            self.decimals,
        )
        self.loss_if_stopped = round(
            (self.buy_price * self.amount) - (self.stop_loss * self.amount),
            self.decimals,
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
            self.market_sell_buy_price = 0
            self.market_sell = False
        elif inc:
            self.profit_loss += self.profit
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
