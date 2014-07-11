
# coding: utf-8

# In[141]:

import mechanize, re, json
import urlparse
import re,string
from collections import OrderedDict

class StatsNotAuthorized(Exception) :
    pass

class SLStats(object) :
    
    _browser = None
    _credentials= { 'user' : '', 'password' : '' }
    
    def login(self) :
		try :
			r=self._browser.open("https://client.scribblelive.com/")
			if len([b for b in self._browser.forms()])>0 :
				self._browser.select_form(nr=0)
				self._browser["ctl00$PageInfo$Email"]=self._credentials["user"]
				self._browser["ctl00$PageInfo$Password"]=self._credentials["password"]
				self._browser.submit()
				if len([b for b in self._browser.forms()])>0 :
					self._browser.select_form(nr=0)
					self._browser.submit()
		except Exception, e :
			raise e
        
    
    def __init__(self,**kwargs) :
        br=mechanize.Browser()
        br.addheaders = [('User-agent', kwargs.get('useragent','Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'))]
        self._browser=br
        if kwargs :
            self._credentials=kwargs
        


    def stats(self,eventid) :
        self.login()
        r=self._browser.open("https://client.scribblelive.com/client/Reports.aspx?id=%s" % eventid) 
        d=r.get_data()
        try :
            auth=re.search(r'Auth: "([^"]+)"',d).groups()[0]
        except AttributeError :
            """ Page contains no Auth Token -> Event is not accessible """
            raise StatsNotAuthorized(eventid)
        m=re.search(r'<h2 class="page_title">(?P<title>[^<]+)',d)
        m=m.groupdict() if m else {}
        r=self._browser.open("https://apiv1secure.scribblelive.com/api/rest/metrics/%s/origin/total?callback=jQuery191049792258255183697_1401883792306&Auth=%s&format=json&SourceType=3&LastHashKey=&LastRangeKey=" % (eventid,auth)).get_data()
        o=json.loads(r[r.find("({")+1:-1])
        o.update(m)
        return o
    
    
    
    
    
    def table(self,eventid) :
        data=self.stats(eventid)



        def do_map(a) :
            r={}
            for c in ("Source","WatchersSum","Uniques") :
                r[string.lower(c)]=a[c]
            u=urlparse.urlparse(r["source"])
            us=u.netloc.split(".")
            r.update({ 'url' : u.netloc, 'host' : ".".join(us[-2:])})
            return r



        db=OrderedDict()

        def do_reduce(a) :
            if a["host"] not in db :
                db[a["host"]]= { 'host' : a["host"], 'urls' : [], "watcherssum" : 0, "n" : 0, "uniques" : 0 }
            me=db[a["host"]]
            if a["url"] not in me["urls"] :
                me["urls"].append(a["url"])
            for ss in ["watcherssum","uniques"] :
                me[ss]=me[ss]+a[ss]
            me["n"]=me["n"]+1



        for n in data["Sources"] :
            m=do_map(n)
            # print m
            try :
                do_reduce(m)
            except Exception, e:
                print "EXCEPTION ",n,m,e


        return dict(title="%s [%s]" % (unicode(data["title"],"utf-8"),eventid),
                    header=['kunde','watchersum','unique','domains'], 
                    data=[(v.get("host",""),v.get("watcherssum",0), v.get("uniques",0), ", ".join(v.get("urls",[]))) for v in db.values() ]
                   )



