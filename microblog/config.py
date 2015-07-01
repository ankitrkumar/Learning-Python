# -*- coding: utf-8 -*-
import os
WTF_CSRF_ENABLED = True
SECRET_KEY ='some-random-key-here'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 2
MAIL_USERNAME = None
MAIL_PASSWORD = None

#admin list

ADMINS = ['me@kumarankit.com']

#pagination
POSTS_PER_PAGE = 5

#whoosh config
WHOOSH_BASE = os.path.join(basedir, 'search.db')
# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None
MAX_SEARCH_RESULTS = 0

#available langauges
LANGUAGES ={
	'en' : 'English',
	'es' : 'Español'
}

DATABASE_QUERY_TIMEOUT = 0.5
SQLALCHEMY_RECORD_QUERIES = True