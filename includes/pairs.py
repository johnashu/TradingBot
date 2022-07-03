class Pair:

    mark_price = None
    buy_price = 0
    sell_price = 0
    buy_sell = "buy"
    new_trade = True

    sell_order_num = 0
    buy_order_num = 0

    sell_perc = 1.0005
    stop_loss_perc = 0.9995
    swing_perc = 0.9995

    stop_loss = 0

    def __init__(self, name, decimals, amount) -> None:
        self.name = name
        self.decimals = decimals
        self.amount = amount

    def __str__(self):
        return self.name

    def reset_data(self):
        self.buy_sell = "buy"
        self.new_trade = True
        self.mark_price = None
        self.buy_price = 0
        self.sell_price = 0
        self.sell_order_num = 0
        self.buy_order_num = 0
        self.stop_loss


pairs = {
    "ONE-USDT": Pair("ONE-USDT", 6, 5000),
    "LUNC-USDT": Pair("LUNC-USDT", 8, 700_000),
}


# pairs = {
#     "ONE-USDT": {"decimals": 6, "amount": 5000},
#     # "LUNC-USDT": {"decimals": 8, "amount": 700_000},
# }

pairs.update({"all_pairs": ",".join([k for k in pairs.keys()])})
