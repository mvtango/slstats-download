import SLStats
from credentials import login
b=SLStats.SLStats(**login)
a=b.events()

tl=b.timeline(a[8],"watchers")
import pprint
pprint.pprint(tl)

