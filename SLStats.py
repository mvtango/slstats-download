
# coding: utf-8

# In[141]:

import mechanize, re, json
import urlparse
import re,string
from collections import OrderedDict
import datetime

class StatsNotAuthorized(Exception) :
	pass

class SLStats(object) :
	
	_browser = None
	_credentials= { 'user' : '', 'password' : '' }
	_lastlogin=0
	
	def login(self) :
		try :
			if (self._lastlogin!=0) and (datetime.datetime.now()-self._lastlogin).seconds<30 :
				return
			else :
				r=self._browser.open("https://client.scribblelive.com/")
				if len([b for b in self._browser.forms()])>0 :
					self._browser.select_form(nr=0)
					self._browser["ctl00$PageInfo$Email"]=self._credentials["user"]
					self._browser["ctl00$PageInfo$Password"]=self._credentials["password"]
					self._browser.submit()
					if len([b for b in self._browser.forms()])>0 :
						self._browser.select_form(nr=0)
						self._browser.submit()
						self._lastlogin=datetime.datetime.now()
		except Exception, e :
			raise e
		
	
	def __init__(self,**kwargs) :
		br=mechanize.Browser()
		br.addheaders = [('User-agent', kwargs.get('useragent','Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'))]
		self._browser=br
		if kwargs :
			self._credentials=kwargs
		

	def normalize_eventid(self,id_or_url) :
		self.login()
		if not re.match(r"\d+",id_or_url) :
			id_or_url=self.id_for_event(id_or_url)
		return id_or_url



	def get_from_endpoint(self,endpoint) :
		eventid=re.findall(r"\d+",endpoint)[0]	
		r=self._browser.open("https://client.scribblelive.com/client/Reports.aspx?id=%s" % eventid) 
		d=r.get_data()
		try :
			auth=re.search(r'Auth: "([^"]+)"',d).groups()[0]
		except AttributeError :
			""" Page contains no Auth Token -> Event is not accessible """
			raise StatsNotAuthorized(endpoint)
		m=re.search(r'<h2 class="page_title">(?P<title>[^<]+)',d)
		m=m.groupdict() if m else {}
		apiurl="https://apiv1secure.scribblelive.com/api/rest/%s?callback=jQuery191049792258255183697_1401883792306&Auth=%s&format=json&LastHashKey=%%(LastHashKey)s&LastRangeKey=%%(LastRangeKey)s&LastTime=%%(LastTime)s&LastSourceType=%%(LastSourceType)s" % (endpoint,auth)
		bdict=dict(LastRangeKey="",LastHashKey="",LastTime="",LastSourceType="")
		m["Sources"]=[]
		while True :
			# print "getting %s" % repr(bdict)
			req=self._browser.open(apiurl % bdict)
			r=req.get_data()
			o=json.loads(r[r.find("({")+1:-1])
			if req.code==200 :
				if not "Sources" in m or len(m["Sources"])==0 :
					m.update(o)
				else :
					m["Sources"].extend(o["Sources"])
				return m
			for k in bdict.keys() :
				bdict[k]=o.get(k,"")
			m["Sources"].extend(o["Sources"])



	def origin(self,eventid) :
		eid=self.normalize_eventid(eventid)
		return self.get_from_endpoint("metrics/%s/origin/total" % eid)


	def syndication(self,eventid) :
		eid=self.normalize_eventid(eventid)
		return self.get_from_endpoint("metrics/%s/syndication" % eid)

	
	def events(self) :
		self.login()
		r=self._browser.open("https://client.scribblelive.com/MyEvents.aspx")
		d=r.get_data()
		return re.findall(r'href="(?P<url>https://client.scribblelive.com/Event/[^"]+)"',d)
		
	
	def id_for_event(self,n) :
		self.login()
		try :
			r=self._browser.open(n)
			d=r.get_data()
			return re.findall(r"var ThreadId = '(?P<id>\d+)';",d)[0]
		except Exception, e :
			return False

	def syndicationtable(self,eventid) :
		o=self.syndication(eventid)
		header=['ClientName','Title','TotalPageViews','TotalUniquePageViews','TotalWatchers']
		data=[]
		for tr in o['MetricList'] :
			data.append([tr[k] for k in header])
		return(dict(title=o["title"],header=header,data=data))
			
		
	def table(self,eventid) :
		data=self.origin(eventid)


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


if __name__ == '__main__' : 
	b=SLStats(user='mvirtel@dpa-newslab.com',password="")
	import pprint
	l=b.events()
	# print l[0],":",b.id_for_event(l[2])
	pprint.pprint(b.table(l[2]))
	pprint.pprint(b.syndication(l[2]))	
	STOP
	
