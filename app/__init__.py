import os

from .assets import init_assets
from .forms import RegisterForm
from .helpers import Flask
from .middleware import MethodRewriteMiddleware

from flask import current_app, redirect, render_template, request, flash, \
                  url_for, session

from flask.ext.security import (Security, LoginForm, current_user, 
                                login_required, user_datastore)
from flask.ext.security.datastore.sqlalchemy import SQLAlchemyUserDatastore

from flask.ext.social import Social, social_login_failed
from flask.ext.social.datastore.sqlalchemy import SQLAlchemyConnectionDatastore

from flask.ext.sqlalchemy import SQLAlchemy

class SocialLoginError(Exception):
    pass

def create_app():
    app = Flask(__name__)
    app.config.from_yaml(app.root_path)
    app.config.from_heroku()
    app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
    
    app.logger.debug(app.config)
    
    init_assets(app)
    
    db = SQLAlchemy(app)
    Security(app, SQLAlchemyUserDatastore(db))
    Social(app, SQLAlchemyConnectionDatastore(db))
    
    try:
        db.create_all()
    except: 
        pass
    
    @app.context_processor
    def template_extras():
        return dict(
            google_analytics_id=app.config.get('GOOGLE_ANALYTICS_ID', None)
        )
    
    @social_login_failed.connect_via(app)
    def on_social_login_failed(sender, provider_id, oauth_response):
        app.logger.debug('Social Login Failed: provider_id=%s'
                         '&oauth_response=%s' % (provider_id, oauth_response))

        # Save the oauth response in the session so we can make the connection
        # later after the user possibly registers
        session['last_oauth_response'] = dict(provider_id=provider_id,
                                              oauth_response=oauth_response)
        raise SocialLoginError()

    @app.errorhandler(SocialLoginError)
    def social_login_error(error):
        return redirect(url_for('register', social_login_failed=1))
    
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

            # See if there was an attempted social login prior to registering
            # and if there was use the provider connect_handler to save a connection
            social_login_response = session.pop('last_oauth_response', None)

            if social_login_response:
                provider = getattr(app.social, social_login_response['provider_id'])
                provider.connect_handler(social_login_response['oauth_response'], 
                                         user_id=str(user.id))
            
            return render_template('thanks.html', user=user)
        
        social_login_failed = int(request.args.get('social_login_failed', 0))

        return render_template('register.html', form=form, 
                               social_login_failed=social_login_failed)
    
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html',
            twitter_conn=current_app.social.twitter.get_connection(),
            facebook_conn=current_app.social.facebook.get_connection())
    
    @app.route('/profile/<provider_id>/post', methods=['POST'])
    @login_required
    def social_post(provider_id):
        message = request.form.get('message', None)
        
        if message:
            conn = getattr(current_app.social, provider_id).get_connection()
            api = conn['api']
            
            if provider_id == 'twitter':
                display_name = 'Twitter'
                api.PostUpdate(message)
            if provider_id == 'facebook':
                display_name = 'Facebook'
                api.put_object("me", "feed", message=message)
            
            flash('Message posted to %s: %s' % (display_name, message), 'info')
            
        return redirect(url_for('profile'))
    
    
    return app
