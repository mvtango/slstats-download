# coding: utf-8
import sys,traceback

#for p in ['.', '', '/srv/scribble-stat/venv/local/lib/python2.7/site-packages/distribute-0.6.24-py2.7.egg', '/srv/scribble-stat/venv/local/lib/python2.7/site-packages/pip-1.1-py2.7.egg', '/srv/scribble-stat/venv/lib/python2.7/site-packages/distribute-0.6.24-py2.7.egg', '/srv/scribble-stat/venv/lib/python2.7/site-packages/pip-1.1-py2.7.egg', '/srv/scribble-stat/venv/lib/python2.7', '/srv/scribble-stat/venv/lib/python2.7/plat-linux2', '/srv/scribble-stat/venv/lib/python2.7/lib-tk', '/srv/scribble-stat/venv/lib/python2.7/lib-old', '/srv/scribble-stat/venv/lib/python2.7/lib-dynload', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-linux2', '/usr/lib/python2.7/lib-tk', '/srv/scribble-stat/venv/local/lib/python2.7/site-packages', '/srv/scribble-stat/venv/lib/python2.7/site-packages'] :
#	if not p in sys.path :
#		sys.path.append(p)

# print sys.path


from flask import Flask,render_template,request
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from SLStats import SLStats

class SubmitForm(Form):
    eventid  = TextField('Event ID / URL eintragen', validators=[DataRequired()])
    eventurl = SelectField(u'... oder Event auswählen', choices=[(0,"Ereignisliste ist leer")])
    username = TextField('ScribbleLive-Nutzername (email)',validators=[DataRequired()])
    password = PasswordField('ScribbleLive-Passwort',validators=[DataRequired()])
    submit   = SubmitField('Abschicken')



app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
Bootstrap(app)



@app.route('/scribble/',methods=('GET','POST'))
def get_result():
	form=SubmitForm(request.form)
	atable=""
	response={ "class" : "success", "text" : "" }
	other=[]
	syndication={}
	if request.method=='POST' :
		try :
			statbot=SLStats(user=form.username.data,password=form.password.data)
			#if form.eventurl.data :
			import pprint
			cc=pprint.pformat(form.eventurl.data)
			#else :
			table=statbot.table(form.eventid.data)
			other=statbot.events()
			syndication=statbot.syndicationtable(form.eventid.data)
			response["text"]="Heruntergeladen: {form.eventid.data}".format(form=form,table=table)
			atable=[table["title"], ";".join(table["header"])]
			atable.extend([";".join(["%s" % a for a in row]) for row in table["data"]])
			atable.append(";".join(syndication["header"]))
			atable.extend([";".join(["%s" % a for a in row]) for row in syndication["data"]])
			atable="\r\n".join(atable)
		except Exception, e:
			response["text"]="Fehler beim Herunterladen {form.eventid.data} : {0} -- {exc} ".format(repr(e),form=form,exc=traceback.format_exc())
			response["class"]="warning"
			table={}
	else :
		response={}
		table={}
		other=[]
	return render_template("start.html",form=SubmitForm(),response=response,
						   table=table,atable=atable, other=other,syndication=syndication)

if __name__ == '__main__':
    app.run(debug=True)


