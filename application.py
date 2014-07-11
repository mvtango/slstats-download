from flask import Flask,render_template,request
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from SLStats import SLStats

class SubmitForm(Form):
    eventid  = TextField('Event ID', validators=[DataRequired()])
    username = TextField('ScribbleLive-Nutzername (email)',validators=[DataRequired()])
    password = PasswordField('ScribbleLive-Passwort',validators=[DataRequired()])
    submit   = SubmitField('Abschicken')



app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
Bootstrap(app)



@app.route('/',methods=('GET','POST'))
def get_result():
	form=SubmitForm(request.form)
	atable=""
	response={ "class" : "success", "text" : "" }
	if request.method=='POST' :
		try :
			statbot=SLStats(user=form.username.data,password=form.password.data)
			table=statbot.table(form.eventid.data)
			response["text"]="Heruntergeladen: Ereignis Nr.  {form.eventid.data}".format(form=form,table=table)
			atable=[table["title"], ";".join(table["header"])]
			atable.extend([";".join(["%s" % a for a in row]) for row in table["data"]])
			atable="\r\n".join(atable)
		except Exception, e:
			response["text"]="Fehler beim Herunterladen {form.eventid.data} : {0}".format(repr(e),form=form)
			response["class"]="warning"
			table={}
	else :
		response={}
		table={}
	return render_template("start.html",form=SubmitForm(),response=response,table=table,atable=atable)

if __name__ == '__main__':
    app.run(debug=True)


