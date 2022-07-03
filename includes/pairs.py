pairs = {
    "ONE-USDT": {"decimals": 6, "amount": 5000},
    "LUNC-USDT": {"decimals": 8, "amount": 700_000},
}
pairs.update({"all_pairs": ",".join([k for k in pairs.keys()])})
