import flask
from app import app
from .forms import LoginForm

@app.route('/')
@app.route('/index')

def index():
	user = {'nickname' : 'Ankit'} #some user
	posts = [
		{
			'author' : {'nickname' : 'Anuj'},
			'body' : 'Working fellow now!'
		},
		{
			'author' : {'nickname' : 'Susan'},
			'body': 'some bitch'
		}
	]
	return flask.render_template('index.html',
		title = 'Test', 
		user = user,
		posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flask.flash('Login requested for OpenID="%s", remember_me=%s' %
			(form.openid.data, str(form.remember_me.data)))
		return flask.redirect('/index')
	return flask.render_template('login.html', 
		title ='Sign In',
		form = form
		)