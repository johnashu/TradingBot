from decimal import Decimal, ROUND_DOWN
import logging as log


def round_down(amount: str, decimals: int) -> float:
    places = "." + "".join(["0" for _ in range(decimals)])
    rounded = Decimal(amount).quantize(Decimal(places), rounding=ROUND_DOWN)
    return float(rounded)


def calc_price_from_amount(
    available: str, amount: str, price: str, decimals: int
) -> float:

    amount = (float(amount) * 0.99) / float(price)
    other = (float(available) * 0.99) / float(price)
    if other > amount:
        log.info(f"Amount {amount}  ::  Other  {other}")
        amount = other
    return round_down(amount, decimals)


def create_averages(arr: list, ts: int) -> dict:

    prices = [float(x[0]) for x in arr]
    volumes = [float(x[1]) for x in arr]
    rtn = dict(
        avg_price=sum(prices) / len(arr), avg_volume=sum(volumes) / len(arr), ts=ts
    )
    return rtn


def readable_price(num, d: int = 18, show_decimals=True, print_res=True) -> str:
    temp = []
    c = 1
    try:
        main, decimals = f"{int(num) / 10 ** d:.{d}f}".split(".")
    except ValueError:
        return float(num)

    for d in reversed(main):
        temp.insert(0, d)
        if c == 3:
            temp.insert(0, ",")
            c = 1
        else:
            c += 1

    if not show_decimals:
        decimals = ""

    rtn_str = "".join(temp)
    rtn_str += f".{decimals}" if show_decimals else ""
    if rtn_str[0] == ",":
        rtn_str = rtn_str[1:]

    if print_res:
        print(rtn_str)
    return rtn_str


# p = calc_price_from_amount('180', '180', '0.018152', 1)
# print(p)
#

# print(180 * 0.99)
