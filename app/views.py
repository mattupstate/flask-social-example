
from flask import render_template, redirect, request, current_app, session, \
     flash, url_for
from flask.ext.security import LoginForm, current_user, login_required, \
     login_user
from flask.ext.social.utils import get_display_name

from . import app
from .forms import RegisterForm
from .models import User
from .tools import requires_auth


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if current_user.is_authenticated():
        return redirect(request.referrer or '/')

    return render_template('login.html', form=LoginForm())


@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/<provider_id>')
def register(provider_id=None):
    app.logger.debug("/register [%s]" % request.method)

    if current_user.is_authenticated():
        return redirect(request.referrer or '/')

    form = RegisterForm()

    if form.validate_on_submit():
        user = current_app.security.datastore.create_user(
                email=form.email.data,
                password=form.password.data)

        # See if there was an attempted social login prior to registering
        # and if so use the provider connect_handler to save a connection
        social_login_response = session.pop('last_oauth_response', None)

        if social_login_response:
            provider_id = social_login_response['provider_id']
            oauth_response = social_login_response['oauth_response']

            provider = getattr(app.social, provider_id)
            provider.connect_handler(oauth_response, user_id=str(user.id))

        if login_user(user, remember=True):
            flash('Account created successfully', 'info')
            return redirect(url_for('profile'))

        return render_template('thanks.html', user=user)

    social_login_failed = int(request.args.get('social_login_failed', 0))
    provider_name = None

    if social_login_failed and provider_id:
        provider_name = get_display_name(provider_id)

    return render_template('register.html', form=form,
                           social_login_failed=social_login_failed,
                           provider_name=provider_name)


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


@app.route('/admin')
@requires_auth
def admin():
    users = User.query.all()
    user_count = len(users)
    return render_template('admin.html',
                            users=users,
                            user_count=user_count)
