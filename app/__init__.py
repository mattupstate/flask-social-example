import os

from .assets import init_assets
from .forms import RegisterForm
from .helpers import Flask

from flask import current_app, redirect, render_template, request, flash

from flask.ext.security import (Security, LoginForm, current_user, 
                                login_required, user_datastore)
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
    
    try: 
        db.drop_all()
        db.create_all()
    except: 
        pass
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        if current_user.is_authenticated():
            return redirect(request.referrer or '/')
        
        return render_template('login.html', form=LoginForm())
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated():
            return redirect(request.referrer or '/')
        
        form = RegisterForm()
        
        if form.validate_on_submit():
            user = user_datastore.create_user(
                    username=form.username.data, 
                    email=form.email.data,
                    password=form.password.data)
            
            return render_template('thanks.html', user=user)
        
        return render_template('register.html', form=form)
    
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html',
            twitter_conn=current_app.social.twitter.get_connection(),
            facebook_conn=current_app.social.facebook.get_connection())
    
    return app