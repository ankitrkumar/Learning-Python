from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm, oid
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, EditForm, PostForm, SearchForm
from .models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, DATABASE_QUERY_TIMEOUT
from flask.ext.sqlalchemy import get_debug_queries

@app.route('/', methods =['GET','POST'])
@app.route('/index', methods =['GET','POST'])
@app.route('/index/<int:page>', methods =['GET','POST'])
@login_required
def index(page = 1):
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
		db.session.add(post)
		db.session.commit()
		flash('Post published.')
		return redirect(url_for('index'))		#this request makes sure that on a refresh we
												# don't do a Post, if user refreshes we get the 
												#GET request for the index post and not the POST 
												#request which will post the new post again
	posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	return render_template('index.html',
		title = 'Home', 
		form = form,
		posts = posts)


@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
	return render_template('login.html', 
		title ='Sign In',
		form = form,
		providers = app.config['OPENID_PROVIDERS']
		)


@oid.after_login
def after_login(resp):
	if resp.email is None or resp.email == "":
		flash('Invaid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email = resp.email).first()
	if user is None:
		nickname = resp.nickname
		if nickname is None or nickname == "":
			nickname = resp.email.split('@')[0]
		nickname = User.make_unique_nickname(nickname)
		user = User(nickname = nickname, email = resp.email)
		db.session.add(user)
		db.session.commit()
		db.session.add(user.follow(user))
		db.session.commit()
	remember_me = False
	
	if'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.search_form = SearchForm()

@app.after_request
def after_request(resp):
	for query in get_debug_queries():
		if query.duration >= DATABASE_QUERY_TIMEOUT:
			app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
	return resp

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
	user = User.query.filter_by(nickname = nickname).first()
	if user == None:
		flash('User %s not found.' % nickname)
		return redirect(url_for('index'))
	posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
	return render_template('user.html',
							user = user,
							posts = posts)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Profile has been updated successfully!')
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form = form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash("User %s not found" % nickname)
		return redirect(url_for('index'))
	if user == g.user:
		flash("Following self isn't allowed")
		return redirect(url_for('index'))
	u = g.user.follow(user)
	if u is None:
		flash("Can't follow" + nickname + '.')
		return redirect(url_for('index'))
	db.session.add(u)
	db.session.commit()
	flash('Following ' + nickname + ' successful!')
	return redirect(url_for('user', nickname= nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user = User.query.filter_by(nickname= nickname).first()
	if user is None:
		flash("User %s not found" % nickname)
		return redirect(url_for('index'))
	if user == g.user:
		flash("Unfollowing self not allowed")
		return redirect(url_for('index'))
	u = g.user.unfollow(user)
	if u is None:
		flash("Can't unfollow " + nickname +'.')
		return redirect(url_for('user',nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash('Unfollowing ' + nickname + ' successful!')
	return redirect(url_for('user', nickname= nickname))

@app.route('/search', methods =['POST'])
@login_required
def search():
	if not g.search_form.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
	results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
	return render_template('search_results.html',
							query = query,
							results = results
							)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
	post = Post.query.get(id)
	if post is None:
		flash('Post Not Found.')
		return redirect(url_for('index'))
	if post.author.id != g.user.id:
		flash('Can only delte your own posts!')
		return redirect(url_for('index'))
	db.session.delete(post)
	db.session.commit()
	flash('Post deleted.')
	return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
