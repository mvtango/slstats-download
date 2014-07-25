import SLStats
from credentials import login
b=SLStats.SLStats(**login)
a=b.events()

print a[8], b.basic(a[8])

