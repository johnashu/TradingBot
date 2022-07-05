from decimal import Decimal, ROUND_DOWN


def round_down(amount, decimals):
    places = "." + "".join(["0" for _ in range(decimals)])
    rounded = Decimal(amount).quantize(Decimal(places), rounding=ROUND_DOWN)
    return float(rounded)


def create_averages(arr: list, ts: int) -> dict:

    prices = [float(x[0]) for x in arr]
    volumes = [float(x[1]) for x in arr]
    rtn = dict(
        avg_price=sum(prices) / len(arr), avg_volume=sum(volumes) / len(arr), ts=ts
    )
    return rtn


def readable_price(num, d: int = 18, show_decimals=True, print_res=True):
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
