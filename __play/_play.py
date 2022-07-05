
from decimal import *    
decimals = 4
places = '.' + "".join(["0" for _ in range(decimals)])
print(places)
res = Decimal('10000.12346').quantize(Decimal(places), rounding=ROUND_DOWN)
print(float(res))