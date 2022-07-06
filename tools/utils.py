from decimal import Decimal, ROUND_DOWN
import logging as log


def round_down(amount: str, decimals: int) -> float:
    places = f'.{"".join(["0" for _ in range(decimals)])}'
    rounded = Decimal(amount).quantize(Decimal(places), rounding=ROUND_DOWN)
    return float(rounded)


def calc_price_from_amount(
    available: str, desired_amount: str, price: str, decimals: int
) -> float:

    desired_amount = (float(desired_amount) * 0.99) / float(price)
    other = (float(available) * 0.99) / float(price)

    # check if funds are avialable.  Sometimes the loop will go to fast so we ensure that other is at least greater than half desired.  This will also serve as a stop in case of severe volatility
    if desired_amount / 2 < other < desired_amount:
        log.info(f"Amount {desired_amount}  ::  Other  {other}")
        desired_amount = other
    return round_down(desired_amount, decimals)


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


# places = float(f'0.{"".join(["0" for _ in range(4-1)])}1')
# print(places)

# d = 180
# o = 90.1
# d2 = d /2
# print(d2 < o < d)
