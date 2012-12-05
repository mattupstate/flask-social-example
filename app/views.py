
from flask import render_template, redirect, request, current_app, session, \
     flash, url_for
from flask.ext.security import LoginForm, current_user, login_required, \
     login_user
from flask.ext.social.utils import get_provider_or_404
from flask.ext.social.views import connect_handler

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
@app.route('/register/<provider_id>', methods=['GET', 'POST'])
def register(provider_id=None):
    if current_user.is_authenticated():
        return redirect(request.referrer or '/')

    form = RegisterForm()

    if provider_id:
        provider = get_provider_or_404(provider_id)
        connection_values = session.get('failed_login_connection', None)
    else:
        provider = None
        connection_values = None

    if form.validate_on_submit():
        ds = current_app.security.datastore
        ds.create_user(email=form.email.data, password=form.password.data)
        ds.commit()
        user = ds.find_user(email=form.email.data)

        # See if there was an attempted social login prior to registering
        # and if so use the provider connect_handler to save a connection
        connection_values = session.pop('failed_login_connection', None)

        if connection_values:
            connection_values['user_id'] = user.id
            connect_handler(connection_values, provider)

        if login_user(user, remember=True):
            flash('Account created successfully', 'info')
            return redirect(url_for('profile'))

        return render_template('thanks.html', user=user)

    login_failed = int(request.args.get('login_failed', 0))

    return render_template('register.html',
                           form=form,
                           provider=provider,
                           login_failed=login_failed,
                           connection_values=connection_values)


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
