
from flask import redirect, url_for, session
from flask.ext.assets import Environment
from flask.ext.security import Security
from flask.ext.security.datastore import SQLAlchemyUserDatastore
from flask.ext.social import Social, social_login_failed
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
from flask.ext.sqlalchemy import SQLAlchemy

from .helpers import Flask
from .middleware import MethodRewriteMiddleware


app = Flask(__name__)
app.config.from_yaml(app.root_path)
app.config.from_heroku()
app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)

db = SQLAlchemy(app)
webassets = Environment(app)

# Late import so modules can import their dependencies properly
from . import assets, models, views

security_ds = SQLAlchemyUserDatastore(db, models.User, models.Role)
social_ds = SQLAlchemyConnectionDatastore(db, models.Connection)

app.security = Security(app, security_ds)
app.social = Social(app, social_ds)


class SocialLoginError(Exception):
    def __init__(self, provider_id):
        self.provider_id = provider_id


@app.before_first_request
def before_first_request():
    try:
        models.db.create_all()
    except Exception, e:
        app.logger.error(str(e))


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
    raise SocialLoginError(provider_id)


@app.errorhandler(SocialLoginError)
def social_login_error(error):
    return redirect(url_for('register',
                            provider_id=error.provider_id,
                            social_login_failed=1))
