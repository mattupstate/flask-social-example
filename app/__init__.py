import os

from .assets import init_assets
from .helpers import Flask

from flask import current_app, redirect, render_template, request

from flask.ext.security import Security, LoginForm, current_user, login_required
from flask.ext.security.datastore.sqlalchemy import SQLAlchemyUserDatastore

from flask.ext.social import Social
from flask.ext.social.datastore.sqlalchemy import SQLAlchemyConnectionDatastore

from flask.ext.sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    app.config.from_yaml(app.root_path)
    
    try:
        app.config.from_bundle_config()
    except Exception, e:
        print "Error: %s" % e
    
    init_assets(app)
    
    db = SQLAlchemy(app)
    Security(app, SQLAlchemyUserDatastore(db))
    Social(app, SQLAlchemyConnectionDatastore(db))
    
    try: db.create_all()
    except: pass
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        if current_user.is_authenticated():
            return redirect(request.referrer or '/')
        
        return render_template('login.html', form=LoginForm())
    
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html',
            twitter_conn=current_app.social.twitter.get_connection(),
            facebook_conn=current_app.social.facebook.get_connection())
    
    return app